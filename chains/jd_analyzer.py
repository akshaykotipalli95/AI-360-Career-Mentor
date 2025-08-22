from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

class JobDescriptionSkills(BaseModel):
    job_title: str = Field(description="The title of the job role.")
    experience_level: str = Field(description="Estimated experience level, e.g., Junior, Mid-Level, Senior.")
    must_have_skills: List[str] = Field(description="A list of essential, must-have skills.")
    nice_to_have_skills: List[str] = Field(description="A list of skills that are beneficial but not required.")

def analyze_jd_skills(jd_text: str) -> dict:
    """Extracts key skills and requirements from a job description text."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    parser = JsonOutputParser(pydantic_object=JobDescriptionSkills)
    
    prompt = ChatPromptTemplate.from_template("""
    Analyze the following job description and extract the required information.
    Follow the JSON format instructions precisely.
    
    {format_instructions}

    Job Description:
    {jd}
    """)
    
    chain = prompt | llm | parser
    
    return chain.invoke({
        "jd": jd_text,
        "format_instructions": parser.get_format_instructions()
    })