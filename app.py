from flask import Flask, request, jsonify
from dotenv import load_dotenv
from chains.rag_chain import CareerRAGChain
from chains.jd_analyzer import analyze_jd_skills
from chains.path_generator import generate_learning_path
import os
import traceback # <--- ADDED FOR DEBUGGING
from chains.resume_analyzer import analyze_resume

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize the main RAG chain once
try:
    print("Initializing RAG Chain...") # <--- ADDED FOR DEBUGGING
    if os.path.exists("storage/faiss_index"):
        rag_chain_instance = CareerRAGChain()
        print("Career RAG Chain initialized successfully.")
    else:
        print("FAISS index not found. Please run ingest.py first.")
        rag_chain_instance = None
except Exception as e:
    print("--- RAG CHAIN INITIALIZATION ERROR ---") # <--- ADDED FOR DEBUGGING
    traceback.print_exc()
    print("--------------------------------------")
    rag_chain_instance = None

@app.route('/')
def index():
    return "AI 360 Career Mentor Bot is running! Use the /api endpoints to interact."

@app.route("/api/chat", methods=['POST'])
def chat():
    if not rag_chain_instance:
        return jsonify({"error": "RAG Chain is not available. Check for initialization errors."}), 503
        
    data = request.json
    question = data.get("question")
    profile = data.get("profile", {})
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    try:
        answer = rag_chain_instance.invoke(question, profile)
        return jsonify({"answer": answer})
    except Exception as e:
        # The full error traceback will be printed here
        traceback.print_exc()
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

@app.route("/api/analyze-jd", methods=['POST'])
def analyze_jd():
    data = request.json
    jd_text = data.get("jd_text")
    if not jd_text:
        return jsonify({"error": "jd_text is required"}), 400
    
    try:
        result = analyze_jd_skills(jd_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/api/analyze-resume", methods=['POST'])
def handle_resume_analysis():
    data = request.json
    resume_text = data.get("resume_text")
    jd_text = data.get("jd_text")
    
    if not resume_text or not jd_text:
        return jsonify({"error": "resume_text and jd_text are required"}), 400
    
    try:
        result = analyze_resume(resume_text, jd_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/api/generate-plan", methods=['POST'])
def generate_plan():
    data = request.json
    profile = data.get("profile")
    gaps = data.get("gaps")
    if not profile or not gaps:
        return jsonify({"error": "profile and gaps are required"}), 400
    
    try:
        plan = generate_learning_path(profile, gaps)
        return jsonify({"learning_plan": plan})
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)