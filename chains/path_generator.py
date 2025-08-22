from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def generate_learning_path(profile: dict, gaps: list, weeks: int = 8) -> str:
    """Generates a weekly learning plan based on skill gaps."""
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    
    prompt = ChatPromptTemplate.from_template("""
    Create a detailed, week-by-week learning plan for a user aiming to achieve their career goal.
    The plan should span {weeks} weeks and focus on bridging the identified skill gaps.
    For each week, suggest 2-3 specific topics to learn and one practical project or task.
    Provide resource suggestions (e.g., "Read articles on Medium," "Build a small project using...").

    User Profile: {profile}
    Skill Gaps to Address: {gaps}

    Return the plan in Markdown format.
    """)
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"profile": profile, "gaps": gaps, "weeks": weeks})