# embed_store.py

import os
from ingest import load_documents, split_documents
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

PERSIST_DIR = "chroma_db"

def build_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        print(f"Loading existing vector store from '{PERSIST_DIR}'...")
        vectorstore = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=embeddings
        )
        return vectorstore

    print("No existing vector store found. Building fresh...")
    docs = load_documents("documents")
    chunks = split_documents(docs)
    print(f"Embedding {len(chunks)} chunks...")

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIR
    )
    print(f"Vector store built and saved to '{PERSIST_DIR}'.")
    return vectorstore


def rebuild_vectorstore():
    """Force a full rebuild, wiping any existing data first."""
    import shutil
    if os.path.exists(PERSIST_DIR):
        shutil.rmtree(PERSIST_DIR)
    return build_vectorstore()


if __name__ == "__main__":
    build_vectorstore()