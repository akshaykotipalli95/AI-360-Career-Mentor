import json
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser

FAISS_STORE_PATH = "storage/faiss_index"
# Your Gemini API key is placed directly here
GEMINI_API_KEY = "GEMINI_API_KEY"

class CareerRAGChain:
    def __init__(self):
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=GEMINI_API_KEY
        )
        self.vector_store = FAISS.load_local(FAISS_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.1, 
            google_api_key=GEMINI_API_KEY
        )
        
        system_prompt = """You are AI 360, an expert career mentor. 
        Your goal is to provide clear, concise, and actionable career advice.
        Use the following retrieved context to answer the user's question.
        Always cite your sources by referencing the 'source_type' metadata (e.g., [guides], [job_descriptions]).
        If you don't know the answer from the context, state that you couldn't find relevant information.
        Format your answers using markdown with bullet points for readability.
        
        Context:
        {context}
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "My Profile: {profile}\n\nQuestion: {question}")
        ])

        # --- THIS IS THE CORRECTED SECTION THAT FIXES THE KEYERROR ---
        self.chain = (
            # The chain takes the original input dictionary (question, profile)
            RunnableParallel(
                context=RunnableLambda(lambda x: x["question"]) | self.retriever | self._format_docs,
                question=RunnableLambda(lambda x: x["question"]),
                profile=RunnableLambda(lambda x: x["profile"])
            )
            | prompt
            | self.llm
            | StrOutputParser()
        )
        # --- END OF CORRECTED SECTION ---

    def _format_docs(self, docs):
        return "\n\n".join(f"Source Type: [{doc.metadata.get('source_type', 'unknown')}]\nContent: {doc.page_content}" for doc in docs)

    def invoke(self, question: str, profile: dict):
        profile_str = json.dumps(profile, indent=2)
        
        return self.chain.invoke({"question": question, "profile": profile_str})
