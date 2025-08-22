import streamlit as st
import requests
import json
import pypdf
import io

# --- Helper function to read PDF text ---
def read_pdf(file):
    try:
        pdf_reader = pypdf.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF file: {e}"

# --- Page Configuration ---
st.set_page_config(page_title="AI 360 Career Mentor", page_icon="🤖", layout="wide")
st.title("AI 360 Career Mentor Bot 🤖")
st.caption("Your personal AI-powered career advisor.")

# --- API URL ---
API_URL = "http://127.0.0.1:5001"

# --- UI Tabs ---
tab1, tab2, tab4, tab3 = st.tabs(["💬 Career Chat", "📄 JD Analyzer", "🔍 Resume Analyzer", "🚀 Learning Plan"])

# --- Career Chat Tab ---
with tab1:
    st.header("Chat with Your Career Mentor")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I help you with your career today?"}]
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    if prompt := st.chat_input("Ask me anything about your career..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                response = requests.post(f"{API_URL}/api/chat", json={"question": prompt, "profile": {"role": "user"}})
                response.raise_for_status()
                assistant_response = response.json().get("answer", "Sorry, I couldn't get a response.")
                message_placeholder.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the backend. Is app.py running? Error: {e}")

# --- JD Analyzer Tab ---
with tab2:
    st.header("Analyze a Job Description")
    jd_text = st.text_area("Paste the full job description here:", height=300, key="jd_text_analyzer")
    if st.button("Analyze Job Description"):
        if jd_text:
            with st.spinner("Analyzing..."):
                try:
                    response = requests.post(f"{API_URL}/api/analyze-jd", json={"jd_text": jd_text})
                    response.raise_for_status()
                    result = response.json()
                    st.success("Analysis Complete!")
                    st.subheader(f"Job Title: {result.get('job_title', 'N/A')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not connect to the backend. Error: {e}")

# --- Resume Analyzer Tab ---
with tab4:
    st.header("Get Resume Feedback & ATS Score")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    with col2:
        st.subheader("Paste the Job Description")
        jd_text_resume = st.text_area("Paste the job description here:", height=280, key="jd_text_resume")

    if st.button("Analyze My Resume"):
        if uploaded_file is not None and jd_text_resume:
            with st.spinner("Your resume is being analyzed by our AI coach..."):
                file_bytes = io.BytesIO(uploaded_file.getvalue())
                resume_text = read_pdf(file_bytes)
                if "Error reading" in resume_text:
                    st.error(resume_text)
                else:
                    try:
                        response = requests.post(
                            f"{API_URL}/api/analyze-resume",
                            json={"resume_text": resume_text, "jd_text": jd_text_resume}
                        )
                        response.raise_for_status()
                        result = response.json()
                        st.success("Analysis Complete!")
                        score = result.get('match_score', 0)
                        st.metric(label="ATS Match Score", value=f"{score}%")
                        st.progress(score)
                        st.subheader("Analysis Summary")
                        st.write(result.get('summary', ''))
                        st.subheader("Missing Keywords")
                        st.warning("Consider adding these keywords from the job description to your resume:")
                        for keyword in result.get('missing_keywords', []):
                            st.markdown(f"- **{keyword}**")
                        st.subheader("Improvement Suggestions")
                        st.info("Here are some actionable tips to make your resume stronger:")
                        for suggestion in result.get('improvement_suggestions', []):
                            st.markdown(f"- {suggestion}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Could not connect to the backend. Is app.py running? Error: {e}")
        else:
            st.warning("Please upload your resume (PDF) and paste the job description.")

# --- Learning Plan Tab ---
with tab3:
    st.header("Generate a Custom Learning Plan")
    st.info("Enter your skills and the skills you want to learn to get a personalized plan.")
    
    current_skills = st.text_input("Enter your current skills (comma-separated):", "Python, SQL", key="current_skills_plan")
    skill_gaps = st.text_input("Enter skills you want to learn (comma-separated):", "Tableau, Machine Learning", key="gaps_plan")

    if st.button("Generate My Learning Plan"):
        if current_skills and skill_gaps:
            with st.spinner("Generating your personalized 8-week plan..."):
                try:
                    profile_data = {"skills": [skill.strip() for skill in current_skills.split(',')]}
                    gaps_data = [gap.strip() for gap in skill_gaps.split(',')]
                    
                    response = requests.post(
                        f"{API_URL}/api/generate-plan",
                        json={"profile": profile_data, "gaps": gaps_data}
                    )
                    response.raise_for_status()
                    plan = response.json().get("learning_plan")
                    
                    st.success("Your learning plan is ready!")
                    st.markdown(plan)
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not connect to the backend. Is app.py running? Error: {e}")
        else:
            st.warning("Please enter your current skills and the skills you want to learn.")