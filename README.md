**Smart ATS - Resume Analyzer**

A Streamlit-based web application that uses Gemini AI to analyze multiple resumes against a job description (JD) and return the Top 5 matching resumes with match percentages in a JSON format.

**Features**
* Upload multiple PDF resumes
* Paste any Job Description (JD)
* Get the Top 5 best matching resumes based on content relevance
* Powered by Groq API using the DeepSeek model.
* Clean and simple UI using Streamlit

**How it Works**

1.Upload PDF resumes (multiple files allowed).

2.Paste the job description in the text area.

3.Click Analyze Resumes.

4.The app sends resumes and the JD to Groq's DeepSeek model for analysis.

5.The AI compares the resumes to the JD and returns exactly 5 resumes with match percentages in JSON format.

6.The results are displayed in the app as a list of the Top 5 matching candidates.
