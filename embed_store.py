# embed_store.py

from ingest import load_documents, split_documents
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = "chroma_db"

def build_vectorstore():
    docs = load_documents("documents")
    chunks = split_documents(docs)
    print(f"Embedding {len(chunks)} chunks...")

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )

    print(f"Vector store built and saved to '{PERSIST_DIR}'.")
    return vectorstore

if __name__ == "__main__":
    build_vectorstore()