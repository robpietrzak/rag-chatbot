# ingest.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def load_documents(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            filepath = os.path.join(folder_path, filename)
            loader = PyPDFLoader(filepath)
            documents.extend(loader.load())
    return documents

def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    chunks = splitter.split_documents(documents)
    return chunks

if __name__ == "__main__":
    docs = load_documents("documents")
    print(f"Loaded {len(docs)} pages from PDFs.")

    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")

    print("\n--- Sample chunk ---")
    print(chunks[0].page_content)