import streamlit as st
from openai import OpenAI
import os
import PyPDF2
import docx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# We still read the GEMINI_API_KEY from .env because that's where we saved it,
# but we will use it for OpenAI
api_key = os.getenv("GEMINI_API_KEY")
client = OpenAI(api_key=api_key)

# Function to extract text from PDF
def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in range(len(reader.pages)):
        text += reader.pages[page].extract_text()
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# Function to get response from OpenAI
def get_ai_response(resume_text, job_description):
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and AI Resume Analyzer.
    Your task is to evaluate the following resume against the provided job description.
    
    Resume:
    {resume_text}
    
    Job Description:
    {job_description}
    
    Please provide a detailed analysis structured EXACTLY as follows. Use Markdown for formatting.
    
    ## 🎯 Match Score
    Provide a match percentage (e.g., 85%) and a brief sentence explaining the score.
    
    ## 📝 Summary
    Provide a professional summary of the candidate's profile relative to the job description.
    
    ## 💪 Strengths
    List the key strengths and matching qualifications the candidate possesses. Use bullet points.
    
    ## ⚠️ Gaps & Missing Skills
    List the skills or qualifications mentioned in the job description that are missing from the resume. Use bullet points.
    
    ## 💡 Improvement Suggestions
    Provide actionable advice on how the candidate can improve their resume for this specific role.
    
    ## 🔑 ATS-Friendly Keywords
    Provide a comma-separated list of keywords the candidate should ensure are in their resume to pass ATS filters for this role.
    
    ## 🚀 Recommended Projects
    Suggest 1-2 relevant projects the candidate could build to cover their skill gaps or strengthen their profile.
    
    ## 🗣️ Interview Preparation Points
    Provide 3-5 likely interview questions based on the candidate's resume and the job description, along with tips on how to answer them.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful expert resume analyzer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Streamlit App UI
st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI Resume Analyzer & Job Match Tool")
st.markdown("Upload your resume and paste the job description to get a detailed ATS analysis, match score, and improvement suggestions.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload Resume")
    uploaded_file = st.file_uploader("Upload your resume (PDF or DOCX)", type=["pdf", "docx"])

with col2:
    st.subheader("2. Job Description")
    job_description = st.text_area("Paste the job description here", height=250)

submit_button = st.button("Analyze Resume", type="primary")

if submit_button:
    if uploaded_file is not None and job_description:
        with st.spinner("Analyzing your resume... This may take a few seconds."):
            # Extract text
            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.name.endswith(".docx"):
                resume_text = extract_text_from_docx(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload a PDF or DOCX file.")
                st.stop()
            
            # Check for API Key
            if not api_key or api_key == "your_api_key_here":
                st.error("API Key not found. Please set the API key in your .env file.")
            else:
                try:
                    # Get analysis
                    analysis = get_ai_response(resume_text, job_description)
                    st.success("Analysis Complete!")
                    
                    st.markdown("---")
                    st.markdown(analysis)
                    
                except Exception as e:
                    st.error(f"An error occurred during analysis: {e}")
    else:
        st.warning("Please upload a resume and provide a job description to proceed.")
