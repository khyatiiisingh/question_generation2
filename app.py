import os
import json
import faiss
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# Load API key from .env
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise EnvironmentError("Google API Key not found in .env")

import google.generativeai as genai
genai.configure(api_key=GOOGLE_API_KEY)

app = Flask(__name__)
CORS(app)

embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# --- Loaders ---
def load_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def chunk_text(text, chunk_size=500):
    sentences = text.split(". ")
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) <= chunk_size:
            current += sentence + ". "
        else:
            chunks.append(current.strip())
            current = sentence + ". "
    if current:
        chunks.append(current.strip())
    return chunks

# --- Vector DB Functions ---
def save_vector_data(index, chunks, embeddings):
    faiss.write_index(index, "faiss_index.index")
    np.save("chunks.npy", np.array(chunks))
    np.save("embeddings.npy", embeddings)

def load_vector_data():
    if os.path.exists("faiss_index.index"):
        return (
            faiss.read_index("faiss_index.index"),
            np.load("chunks.npy", allow_pickle=True).tolist(),
            np.load("embeddings.npy")
        )
    return None, None, None

def build_vector_index(chunks):
    embeddings = embed_model.encode(chunks)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, chunks, embeddings

def semantic_search(text, index, chunks, embeddings, k=1):
    query_embedding = embed_model.encode([text])
    distances, indices = index.search(np.array(query_embedding), k)
    return [chunks[i] for i in indices[0]]

def build_co_index(co_list):
    co_embeddings = embed_model.encode(co_list)
    co_index = faiss.IndexFlatL2(co_embeddings.shape[1])
    co_index.add(np.array(co_embeddings))
    return co_index, co_embeddings

def get_relevant_co(text, co_list, co_index):
    query_embedding = embed_model.encode([text])
    _, indices = co_index.search(np.array(query_embedding), k=1)
    return co_list[indices[0][0]]

def save_to_json(co, bloom, questions, json_file="generated_questions.json"):
    new_entry = {
        "course_outcome": co,
        "bloom_level": bloom,
        "questions": questions
    }
    data = []
    if os.path.exists(json_file):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    data.append(new_entry)
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- API Route ---
@app.route("/api/generate-questions", methods=["POST"])
def generate_questions():
    selected_cos = request.form.getlist("selected_cos[]")
    selected_blooms = request.form.getlist("selected_bloom[]")
    selected_types = request.form.getlist("selected_types[]")
    extra_prompt = request.form.get("extra_prompt", "")

    if not selected_cos or not selected_blooms or not selected_types:
        return jsonify({"error": "Missing fields"}), 400

    transcript = load_file("cleaned_transcript.txt")
    course_outcomes = load_file("course_outcomes.txt").splitlines()
    co_index, co_embeddings = build_co_index(course_outcomes)

    index, chunks, embeddings = load_vector_data()
    if index is None:
        chunks = chunk_text(transcript)
        index, chunks, embeddings = build_vector_index(chunks)
        save_vector_data(index, chunks, embeddings)

    # Optional case material
    if "case_material" in request.files:
        case_text = request.files["case_material"].read().decode("utf-8")
        case_chunks = chunk_text(case_text)
        case_index, case_chunks, case_embeddings = build_vector_index(case_chunks)
    else:
        case_index = case_chunks = case_embeddings = None

    all_outputs = []
    for co in selected_cos:
        for bloom in selected_blooms:
            if case_index:
                retrieved = semantic_search(co, case_index, case_chunks, case_embeddings)[0]
            else:
                retrieved = semantic_search(co, index, chunks, embeddings)[0]

            relevant_co = get_relevant_co(retrieved + " " + bloom, course_outcomes, co_index)

            prompt_parts = [
                "You are a question generation assistant.",
                f"Course Outcome: {co}",
                f"Bloom's Level: {bloom}",
                f"Question Types: {', '.join(selected_types)}",
                f"Content:\n{retrieved}"
            ]
            if extra_prompt:
                prompt_parts.append(f"Instructions: {extra_prompt}")
            prompt_parts.append("Generate appropriate questions for the above CO and context.")
            prompt_parts.append("Format:\nObjective:\n1. ...\nShort Answer:\n1. ... etc.")

            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content("\n".join(prompt_parts))
            output = response.text.strip()

            all_outputs.append({
                "co": co,
                "bloom_level": bloom,
                "output": output
            })

            save_to_json(co, bloom, output)

    return jsonify({
        "questions": all_outputs
    })

@app.route("/")
def health():
    return jsonify({"status": "running", "message": "API Ready"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
