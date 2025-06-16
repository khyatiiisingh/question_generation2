# 🎓 Question Generation System using Bloom’s Taxonomy, FAISS & Gemini

This project is a smart **Question Generation System** that creates questions from lecture transcripts and course outcomes. It supports **Bloom’s Taxonomy-based filtering**, integrates **semantic vector search using FAISS**, and uses **Google Gemini API** for generating questions. 

---

## 🚀 Technologies Used

- 🧠 **Google Gemini API** – for question generation
- 🧊 **FAISS** – vector search for retrieving relevant content
- 🧾 **SentenceTransformer** – for converting text into dense vectors
- ⚙️ **Flask** – backend API to handle question generation
- 🌐 **Streamlit** – frontend UI to interact with the model

---

## 📁 Folder Structure

```
question_generation2/
├── backend.py                  # Flask API server
├── frontend/                   # Streamlit frontend UI
│   └── app.py                  # Main UI file
├── cleaned_transcript.txt      # Transcript content file
├── course_outcomes.txt         # Course outcomes file
├── case_materials/             # Folder for optional case materials
├── faiss_index.index           # FAISS vector index (auto-generated)
├── embeddings.npy              # Stored sentence embeddings
├── chunks.npy                  # Stored transcript chunks
├── .env                        # API key and config variables
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 💡 How It Works

### 🧩 Step-by-step Flow

1. **User Interface (Streamlit)**:
   - Upload optional **case material** (`.txt`)
   - Select **question type** (MCQ, Short, Long)
   - Choose **Bloom’s Taxonomy levels**
   - Add optional **custom prompt**
   - Click "Generate Questions"

2. **Backend Processing (Flask)**:
   - Loads `cleaned_transcript.txt` and `course_outcomes.txt`
   - Uses SentenceTransformer to convert them into dense vectors
   - Builds a FAISS index and finds relevant content
   - Passes this content with prompt to **Google Gemini API**
   - Returns generated questions back to Streamlit

---

## ⚙️ Installation & Setup

### 🔹 Step 1: Clone the repository

```bash
git clone https://github.com/khyatiiisingh/question_generation2.git
cd question_generation2
```

---

### 🔹 Step 2: Set up a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Git Bash / Linux / Mac
source venv/bin/activate
```

---

### 🔹 Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

---

### 🔹 Step 4: Add your Gemini API Key

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

---

## ▶️ Running the App

### ✅ Step 1: Start the Flask Backend (port 5000)

```bash
python backend.py
```

You’ll see:
```
Running on http://127.0.0.1:5000
```

---

### ✅ Step 2: Start the Streamlit Frontend (port 8501)

In a new terminal:

```bash
cd frontend
streamlit run app.py
```

Visit in browser:  
👉 `http://localhost:8501`

---

## 📌 Notes

- Make sure `cleaned_transcript.txt` and `course_outcomes.txt` are present in the root folder.
- You can upload additional **case material** via the Streamlit UI as a `.txt` file.
- Large vector files like `chunks.npy`, `faiss_index.index`, and `embeddings.npy` are excluded from Git using `.gitignore`.
