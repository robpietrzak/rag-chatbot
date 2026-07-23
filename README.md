# RAG Chatbot

A chatbot that answers questions from your own PDFs, grounded in retrieved context using Retrieval-Augmented Generation.

## Features

- Answers questions grounded in your own uploaded PDF documents
- Cites which source document(s) each answer came from
- Refuses to guess when the answer isn't in the provided documents
- Handles complex questions spanning multiple documents via automatic query decomposition
- Simple chat interface built with Streamlit

## Architecture

1. **Ingestion** - PDFs are loaded and split into overlapping chunks
2. **Embedding** - Each chunk is converted into a vector using a local HuggingFace embedding model
3. **Storage** - Vectors are stored in a persistant ChromaDB database
4. **Retrieval** - On a user question, relevant chunks are retrieved via similarity search (complex questions are first decomposed into sub-questions for broader retrieval)
5. **Generation** - Retrieved chunks + the question are sent to Claude, which generates an answer only in that context

## Tech Stack

- **Language:** Python
- **Orchestration:** Langchain
- **Vector Database:** ChromaDB
- **Embeddings:** HuggingFace 'sentence-transformers' (all-MiniLM-L6-v2)
- **LLM:** Anthropic Claude API
- **Interface:** Streamlit

## Setup Instructions

1. Clone the repository
2. Create a virtual environment: 'python -m venv venv'
3. Activate it: 'source venv/Scripts/activate' (Git Bash on Windows) or 'source venv/bin/activate' (Linux/macOS)
4. Install dependencies: 'pip install -r requirements.txt'
5. Create a '.env' file with: 'ANTHROPIC_API_KEY=your_key_here'
6. Add your PDF documents to the 'documents/' folder
7. Run: 'streamlit run app.py'

## Known Limitations

- Single-topic questions retrieve best; genuinely unrelated cross-document questions rely on automatic query decomposition, which adds latency
- No persistent conversational memory yet - each question is answered independently
- The local embedding model has an input length limit, so extremely long chunks may lose some retrieval precision
- Vector store must be rebuilt ('rm -rf chroma_db && python embed_store.py') after adding or changing source documents

## Challenges

See [BUGS_AND_FIXES.md](./BUGS_AND_FIXES.md) for a detailed log of technical issues