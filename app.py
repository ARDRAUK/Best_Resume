import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load API Key
load_dotenv()  
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to get Gemini AI response
def get_gemini_response(input):
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(input)

        if not response or not response.text:
            raise ValueError("AI returned an empty response. Please check your API key or model.")

        return response.text.strip()
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return ""

# Function to extract text from PDFs
def input_pdf_text(uploaded_file):
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# 🔹 Updated Prompt Template
def create_input_prompt(resumes_json, jd):
    return f"""
Hey, act like a highly experienced ATS (Application Tracking System).

Analyze the following resumes and compare them to the job description.  
Return **exactly 5** resumes **with match percentages**, in **pure JSON format**.

Job Description:
{jd}

Resumes:
{resumes_json}

🛑 **Strict JSON Format (No Explanations!)**
Return ONLY a JSON object with this exact structure:
{{
    "Top_Resumes": [
        {{"Candidate": "Resume1.pdf", "Match_Percentage": 92}},
        {{"Candidate": "Resume2.pdf", "Match_Percentage": 85}},
        {{"Candidate": "Resume3.pdf", "Match_Percentage": 80}},
        {{"Candidate": "Resume4.pdf", "Match_Percentage": 75}},
        {{"Candidate": "Resume5.pdf", "Match_Percentage": 70}}
    ]
}}
"""

# 🔹 Streamlit App
st.title("Smart ATS - Resume Analyzer")
st.text("Optimize Your Resume for ATS and Find the Best Fit")

# User inputs
jd = st.text_area("Paste the Job Description")

uploaded_files = st.file_uploader(
    "Upload Resumes (Multiple PDFs Allowed)", 
    type="pdf", 
    accept_multiple_files=True, 
    help="Upload multiple PDF resumes"
)

submit = st.button("Analyze Resumes")

if submit:
    if not jd.strip():
        st.error("Please provide a job description.")
    elif not uploaded_files:
        st.warning("Please upload at least one resume.")
    else:
        with st.spinner("Analyzing resumes... This may take a moment."):
            resume_texts = []
            for uploaded_file in uploaded_files:
                text = input_pdf_text(uploaded_file).strip()  # Remove unwanted spaces/newlines
                resume_texts.append({"Candidate": uploaded_file.name.strip(), "Text": text})

            # Debugging: Print resume names only
            st.write("Debug - Resumes being analyzed:", [r["Candidate"] for r in resume_texts])

            try:
                # Convert resume data to JSON
                resumes_json = json.dumps(resume_texts, ensure_ascii=False)

                # Create formatted prompt with actual data
                formatted_input = create_input_prompt(resumes_json, jd.strip())

                # Get AI response
                response_text = get_gemini_response(formatted_input)
                
                # Extract JSON portion safely
                json_start = response_text.find("{")
                json_end = response_text.rfind("}")

                if json_start == -1 or json_end == -1:
                    st.error("AI did not return valid JSON. Raw response:")
                    st.code(response_text)
                    st.stop()

                cleaned_json = response_text[json_start:json_end+1].strip()

                # Parse JSON
                parsed_response = json.loads(cleaned_json)

                if "Top_Resumes" not in parsed_response:
                    st.error("Missing 'Top_Resumes' key in AI response.")
                    st.write("Raw AI Response:", response_text)
                    st.stop()

                st.subheader("Top 5 Best Matching Resumes")
                for resume in parsed_response["Top_Resumes"]:
                    st.write(f"📄 **{resume.get('Candidate', 'Unknown')}** - Match: {resume.get('Match_Percentage', 'N/A')}%")
                    st.write("---")

            except json.JSONDecodeError as e:
                st.error(f"AI response is not valid JSON: {e}")
                st.code(response_text)  # Show the raw response in a code block
            except ValueError as ve:
                st.error(str(ve))