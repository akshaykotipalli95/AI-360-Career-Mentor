import streamlit as st
import requests
import json
import pypdf
import io

# --- Helper function to read PDF text ---
def read_pdf(file):
    """Reads the text content from an uploaded PDF file."""
    try:
        pdf_reader = pypdf.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF file: {e}"

# --- Page Configuration ---
st.set_page_config(
    page_title="AI 360 Career Mentor",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS for the Dark Theme ---
def load_css():
    st.markdown("""
    <style>
        /* --- Dark Theme (Black) --- */
        .stApp {
            background: linear-gradient(135deg, #000000 0%, #1c1c1c 100%);
            color: #e0e0e0;
        }
        .st-emotion-cache-1c7y2kd { /* Chat message container */
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
        }
        .stTextArea, .stTextInput, .stFileUploader {
            background-color: rgba(255, 255, 255, 0.05);
        }
        h1, h2, h3, h4, h5, h6, strong, p, div, span {
           color: #ffffff !important;
        }
        .stButton button {
            background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
            color: white; border: none; border-radius: 12px; padding: 12px 28px;
            font-weight: bold; box-shadow: 0 4px 15px 0 rgba(49, 196, 190, 0.75);
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px 0 rgba(49, 196, 190, 0.9);
        }
    </style>
    """, unsafe_allow_html=True)

# Load the CSS
load_css()

# --- API URL ---
API_URL = "http://127.0.0.1:5001"

# --- Main App Title ---
st.title("AI 360 Career Mentor")
st.caption("Navigate your career path with the power of AI.")

# --- UI Tabs for different functionalities ---
tab1, tab2, tab3, tab4 = st.tabs(["Career Chat", "Job Description Analyzer", "Resume Analyzer", "Learning Plan"])

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
            message_placeholder.markdown("🧠 Thinking...")
            try:
                response = requests.post(f"{API_URL}/api/chat", json={"question": prompt, "profile": {"role": "user"}})
                response.raise_for_status()
                assistant_response = response.json().get("answer", "Sorry, an error occurred.")
                message_placeholder.markdown(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            except requests.exceptions.RequestException as e:
                error_message = f"Could not connect to the backend. Is app.py running? Error: {e}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# --- JD Analyzer Tab ---
with tab2:
    st.header("Analyze a Job Description")
    jd_text = st.text_area("Paste the job description here to extract key skills.", height=300, key="jd_text_analyzer")
    if st.button("Analyze Job Description", key="jd_button"):
        if jd_text:
            with st.spinner("Extracting insights..."):
                try:
                    response = requests.post(f"{API_URL}/api/analyze-jd", json={"jd_text": jd_text})
                    response.raise_for_status()
                    result = response.json()
                    st.success("Analysis Complete!")
                    st.subheader(f"Job Title: {result.get('job_title', 'N/A')}")
                    st.info(f"**Experience Level:** {result.get('experience_level', 'N/A')}")
                    col1_jd, col2_jd = st.columns(2)
                    with col1_jd:
                        st.markdown("**✅ Must-Have Skills:**")
                        for skill in result.get('must_have_skills', []): st.markdown(f"- {skill}")
                    with col2_jd:
                        st.markdown("**👍 Nice-to-Have Skills:**")
                        for skill in result.get('nice_to_have_skills', []): st.markdown(f"- {skill}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not connect to the backend. Error: {e}")

# --- Resume Analyzer Tab (Simplified for PDF Only) ---
with tab3:
    st.header("Get Resume Feedback & ATS Score")
    col1_res, col2_res = st.columns(2)
    with col1_res:
        st.subheader("Upload Your Resume")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    with col2_res:
        st.subheader("Paste the Job Description")
        jd_text_resume = st.text_area("Paste the job description here:", height=280, key="jd_text_resume")
    
    if st.button("Analyze My Resume", key="resume_button"):
        if uploaded_file is not None and jd_text_resume:
            with st.spinner("Analyzing your resume with AI..."):
                file_bytes = io.BytesIO(uploaded_file.getvalue())
                resume_text = read_pdf(file_bytes)
                
                if "Error reading" in resume_text:
                    st.error(resume_text)
                else:
                    try:
                        # This API call sends the extracted text, not the file
                        response = requests.post(
                            f"{API_URL}/api/analyze-resume", 
                            json={"resume_text": resume_text, "jd_text": jd_text_resume}
                        )
                        response.raise_for_status()
                        result = response.json()
                        
                        if "error" in result:
                            st.error(result["error"])
                        else:
                            st.success("Analysis Complete!")
                            score = result.get('match_score', 0)
                            st.metric(label="ATS Match Score", value=f"{score}%")
                            st.progress(score)
                            with st.expander("See Detailed Analysis"):
                                st.subheader("Analysis Summary")
                                st.write(result.get('summary', ''))
                                st.subheader("Missing Keywords")
                                st.warning("Consider adding these keywords to your resume:")
                                for keyword in result.get('missing_keywords', []): st.markdown(f"- **{keyword}**")
                                st.subheader("Improvement Suggestions")
                                st.info("Here are actionable tips to make your resume stronger:")
                                for suggestion in result.get('improvement_suggestions', []): st.markdown(f"- {suggestion}")
                    except requests.exceptions.RequestException as e:
                        st.error(f"Could not connect to the backend. Is app.py running? Error: {e}")
        else:
            st.warning("Please upload your resume (PDF) and paste the job description.")

# --- Learning Plan Tab ---
with tab4:
    st.header("Generate a Custom Learning Plan")
    st.info("Enter your skills and the skills you want to learn to get a personalized plan.")
    
    current_skills = st.text_input(
        "Enter your current skills (comma-separated):", 
        placeholder="e.g., Python, SQL, Data Analysis", 
        key="current_skills_plan"
    )
    skill_gaps = st.text_input(
        "Enter skills you want to learn (comma-separated):", 
        placeholder="e.g., Tableau, Machine Learning", 
        key="gaps_plan"
    )

    if st.button("Generate My Learning Plan", key="plan_button"):
        if current_skills and skill_gaps:
            with st.spinner("Generating your personalized 8-week plan..."):
                try:
                    profile_data = {"skills": [s.strip() for s in current_skills.split(',')]}
                    gaps_data = [g.strip() for g in skill_gaps.split(',')]
                    response = requests.post(f"{API_URL}/api/generate-plan", json={"profile": profile_data, "gaps": gaps_data})
                    response.raise_for_status()
                    plan = response.json().get("learning_plan")
                    st.success("Your learning plan is ready!")
                    st.markdown(plan)
                except requests.exceptions.RequestException as e:
                    st.error(f"Could not connect to the backend. Is app.py running? Error: {e}")
        else:
            st.warning("Please enter your current skills and the skills you want to learn.")