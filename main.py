import streamlit as st
from pypdf import PdfReader
from google import genai
import io
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Resume Analyser",
    page_icon="👁",
    layout="centered"
)

st.title("AI Resume Analyser")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API Key not found. Please add it to your .env file.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

uploaded_file = st.file_uploader(
    "Upload your resume",
    type=["pdf", "txt"]
)

job_role = st.text_input(
    "Please enter the job role you're targeting (optional)"
)

analyze = st.button("Analyze your Resume")


def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))

    return uploaded_file.read().decode("utf-8")


if analyze:

    if uploaded_file is None:
        st.warning("Please upload a resume first.")
        st.stop()

    try:

        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("Could not extract text from the uploaded file.")
            st.stop()

        prompt = f"""
You are an expert HR professional and ATS resume reviewer.

Analyze the following resume and provide detailed feedback, dont's use any emojis.

Focus on:

1. Overall Resume Score (out of 100)

2. ATS Compatibility Score

3. Content clarity

4. Skills presentation

5. Experience descriptions

6. Resume formatting

7. Strengths

8. Weaknesses

9. Missing skills for the role:
{job_role if job_role else "General Job Application"}

10. Specific improvements

11. Final verdict:
Would you shortlist this candidate? Explain why.

Return the analysis in Markdown using this structure:

# Overall Score

# ATS Score

# Strengths

# Weaknesses

# Missing Skills

# Recommendations

# Improved Summary

# Final Verdict

Resume:

{file_content}
"""

        with st.spinner("Analyzing your resume..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
        st.success("Analysis Complete!")
        st.markdown("## Analysis Results")
        st.markdown(response.text)

    except Exception as e:
        st.error(f"An error occurred:\n\n{str(e)}")
