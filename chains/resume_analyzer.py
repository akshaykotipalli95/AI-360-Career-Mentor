from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

# Define the structured output we want from the LLM
class ResumeAnalysis(BaseModel):
    match_score: int = Field(description="An estimated ATS match score as a percentage (0-100) based on keyword alignment.")
    missing_keywords: List[str] = Field(description="A list of important keywords from the job description that are missing in the resume.")
    improvement_suggestions: List[str] = Field(description="A bulleted list of actionable suggestions to improve the resume's content, clarity, and impact.")
    summary: str = Field(description="A brief, 2-3 sentence summary of the resume's strengths and weaknesses against the job description.")

def analyze_resume(resume_text: str, jd_text: str) -> dict:
    """
    Analyzes a resume against a job description to provide an ATS score and improvement suggestions.
    """
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    
    parser = JsonOutputParser(pydantic_object=ResumeAnalysis)
    
    prompt = ChatPromptTemplate.from_template("""
    You are an expert career coach and ATS (Applicant Tracking System) analyzer.
    Your task is to analyze the provided resume against the given job description.
    
    Follow these steps:
    1.  Identify the key skills, technologies, and qualifications required by the job description.
    2.  Scan the resume to see which of these keywords are present.
    3.  Calculate a "match score" percentage based on how well the resume's content aligns with the job description's requirements.
    4.  List the critical keywords that are missing from the resume.
    5.  Provide concrete, actionable suggestions for improving the resume. Focus on using stronger action verbs, quantifying achievements, and tailoring the content to the job description.
    
    Return your analysis in the specified JSON format.
    
    {format_instructions}

    Job Description:
    ---
    {jd}
    ---
    
    Resume Text:
    ---
    {resume}
    ---
    """)
    
    chain = prompt | llm | parser
    
    return chain.invoke({
        "jd": jd_text,
        "resume": resume_text,
        "format_instructions": parser.get_format_instructions()
    })