# RAG Chatbot

A chatbot that answers questions from your own PDFs, grounded in retrieved context using Retrieval-Augmented Generation.

**🔗 Live demo:** [https://rag-chatbot-robpietrzakdemo.streamlit.app/] — no setup required, just ask a question.

## Features

- Answers questions grounded in your own uploaded PDF documents
- Cites which source document(s) each answer came from
- Refuses to guess when the answer isn't in the provided documents
- Handles complex questions spanning multiple documents via automatic query decomposition
- Simple chat interface built with Streamlit

## Architecture

1. **Ingestion** - PDFs are loaded and split into overlapping chunks
2. **Embedding** - Each chunk is converted into a vector using a local HuggingFace embedding model
3. **Storage** - Vectors are stored in a persistent ChromaDB database
4. **Retrieval** - On a user question, relevant chunks are retrieved via similarity search (complex questions are first decomposed into sub-questions for broader retrieval)
5. **Generation** - Retrieved chunks + the question are sent to Claude, which generates an answer only in that context

## Tech Stack

- **Language:** Python
- **Orchestration:** LangChain
- **Vector Database:** ChromaDB
- **Embeddings:** HuggingFace `sentence-transformers` (all-MiniLM-L6-v2)
- **LLM:** Anthropic Claude API (Haiku model on the public demo, to keep it fast and low-cost for casual visitors)
- **Interface:** Streamlit

## Try It Yourself Locally

Prefer to run it on your own machine and inspect the code as you go? Here's the setup:

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `source venv/Scripts/activate` (Git Bash on Windows) or `source venv/bin/activate` (Linux/macOS)
4. Install dependencies: `pip install -r requirements.txt`
5. Add your own Anthropic API key in one of two ways:
   - **Streamlit-native (recommended):** create `.streamlit/secrets.toml` in the project root with:
     ```toml
     ANTHROPIC_API_KEY = "your_key_here"
     ```
   - **Plain `.env` (works outside Streamlit too):** create a `.env` file with:
     ```
     ANTHROPIC_API_KEY=your_key_here
     ```
   The app checks `st.secrets` first and falls back to the environment variable, so either works.
6. Add your PDF documents to the `documents/` folder
7. Run: `streamlit run app.py`

Note: the deployed demo has its own key configured server-side via Streamlit Cloud's secrets manager — you only need your own key if you're running this locally.

## Demo Guardrails

Since the hosted demo runs on a shared API key, a few limits keep usage (and cost) in check:

- Session-capped query count, after which the app asks visitors to come back later
- Answers use Claude Haiku with a tighter `max_tokens` ceiling, rather than a larger model
- These limits only apply to the hosted demo — running locally with your own key removes them

## Known Limitations

- Single-topic questions retrieve best; genuinely unrelated cross-document questions rely on automatic query decomposition, which adds latency
- No persistent conversational memory yet - each question is answered independently
- The local embedding model has an input length limit, so extremely long chunks may lose some retrieval precision
- Vector store must be rebuilt (`rm -rf chroma_db && python embed_store.py`) after adding or changing source documents

## Challenges

See [BUGS_AND_FIXES.md](./BUGS_AND_FIXES.md) for a detailed log of technical issues
