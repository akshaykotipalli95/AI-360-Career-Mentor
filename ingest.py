import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables from .env file
load_dotenv()

# Define paths
KB_PATH = "knowledge_base"
FAISS_STORE_PATH = "storage/faiss_index"

def create_vector_store():
    """Loads documents, splits them, creates embeddings, and saves to FAISS."""
    print("Loading documents from the knowledge base...")
    
    loader = DirectoryLoader(
        KB_PATH, 
        glob="**/*.*", 
        loader_cls=lambda path: PyPDFLoader(path) if path.lower().endswith('.pdf') else TextLoader(path, encoding='utf-8', autodetect_encoding=True), 
        recursive=True, 
        show_progress=True,
        use_multithreading=True
    )
    
    documents = loader.load()
    
    for doc in documents:
        source_path = doc.metadata.get("source", "")
        try:
            relative_path = os.path.relpath(source_path, KB_PATH)
            source_folder = relative_path.split(os.sep)[0]
            doc.metadata['source_type'] = source_folder
        except ValueError:
            doc.metadata['source_type'] = 'unknown'
        
    print(f"Loaded {len(documents)} documents.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")

    # Create Google Gemini embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    print("Creating and saving FAISS vector store...")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(FAISS_STORE_PATH)
    print(f"Vector store created and saved at {FAISS_STORE_PATH}")

if __name__ == "__main__":
    create_vector_store()