import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("API_URL")

st.title("📘 Question Generator ")

# Load COs from course_outcomes.txt
with open("course_outcomes.txt", "r", encoding="utf-8") as f:
    co_list = [line.strip() for line in f if line.strip()]

bloom_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
question_types = ["Objective", "Short Answer", "Long Answer", "Case-based"]

# Streamlit inputs
selected_cos = st.multiselect("Select Course Outcomes (COs)", co_list)
selected_blooms = st.multiselect("Select Bloom's Levels", bloom_levels)
selected_types = st.multiselect("Select Question Types", question_types)
extra_prompt = st.text_area("Extra Instructions (Optional)")
case_file = st.file_uploader("Upload Case Material (Optional - .txt only)", type=["txt"])

if st.button("Generate Questions"):
    if not selected_cos or not selected_blooms or not selected_types:
        st.error("Please select all required fields (COs, Bloom Levels, Question Types).")
    else:
        with st.spinner("Generating..."):
            form_data = []
            for co in selected_cos:
                form_data.append(("selected_cos[]", co))
            for bloom in selected_blooms:
                form_data.append(("selected_bloom[]", bloom))
            for qtype in selected_types:
                form_data.append(("selected_types[]", qtype))
            form_data.append(("extra_prompt", extra_prompt))

            files = {}
            if case_file:
                files["case_material"] = (case_file.name, case_file.read(), "text/plain")

            try:
                res = requests.post(f"{API_URL}/api/generate-questions", data=form_data, files=files)
                if res.status_code == 200:
                    result = res.json()
                    for item in result["questions"]:
                        st.markdown(f"### CO: {item['co']} | Bloom Level: {item['bloom_level']}")
                        st.code(item["output"])
                else:
                    st.error(f"Error: {res.json().get('error')}")
            except Exception as e:
                st.error(f"Failed to call API: {e}")
