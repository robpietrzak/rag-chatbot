# RAG Chatbot — Bugs & Fixes Log

A record of real issues encountered while building this project, how they were diagnosed, and how they were resolved. Kept as both a personal reference and a demonstration of debugging process for anyone reviewing this repo.

---

## 1. `ModuleNotFoundError: No module named 'langchain.text_splitter'`

**When it happened:** Day 2, first run of `ingest.py`.

**Symptom:**
```
DeprecationWarning: `langchain-community` is being sunset...
ModuleNotFoundError: No module named 'langchain.text_splitter'
```

**Diagnosis:** LangChain has been actively splitting its monolithic package into smaller standalone packages. `RecursiveCharacterTextSplitter` was moved out of the core `langchain` package into its own dedicated package, `langchain-text-splitters`.

**Fix:**
```bash
pip install langchain-text-splitters
```
```python
# Before
from langchain.text_splitter import RecursiveCharacterTextSplitter

# After
from langchain_text_splitters import RecursiveCharacterTextSplitter
```

**Takeaway:** LangChain's fast-moving ecosystem means import paths from tutorials/docs can go stale quickly. When an import fails, check whether the class has moved to its own dedicated package before assuming a version mismatch.

---

## 2. Virtual environment activation command differs by shell

**When it happened:** Day 1, environment setup.

**Symptom:** `venv\Scripts\activate` returned "command not found" when run in Git Bash.

**Diagnosis:** Git Bash on Windows uses Windows-style Python (which creates a `Scripts/` folder, not `bin/`), but Git Bash itself uses Linux-style path/command syntax. This creates a hybrid case that doesn't match either standard Windows CMD syntax or true Linux/WSL syntax.

**Fix:**
```bash
# WSL/Linux
source venv/bin/activate

# Windows CMD
venv\Scripts\activate

# Git Bash on Windows (hybrid — the one that was needed here)
source venv/Scripts/activate
```

**Takeaway:** Always confirm which folder actually exists (`ls venv/`) before assuming which activation syntax applies — `bin/` vs `Scripts/` tells you definitively which environment you're in, regardless of which shell you're typing into.

---

## 3. ChromaDB silently accumulating duplicate chunks

**When it happened:** Days 3-5, discovered while debugging a failed multi-part question ("walk me through the full RAG process").

**Symptom:** `similarity_search` returned the *same exact chunk* 5 times in a row for a query, instead of 5 different relevant chunks. This caused answers to be incomplete or repetitive, even for questions that should have been fully answerable from the source documents.

**Diagnosis:** `build_vectorstore()` called `Chroma.from_documents(...)` every time it ran — and every script in the project (`query.py`, `test_retrieval.py`, `debug_chunks.py`, `app.py`) called `build_vectorstore()` on startup. `Chroma.from_documents()` **appends** to the existing persisted database rather than checking whether the data already exists. After repeated runs across a full day of testing, the database had accumulated dozens of duplicate copies of the same chunks, drowning out genuinely diverse results in similarity search.

**Fix:** Rewrote `embed_store.py` to check whether a populated `chroma_db/` directory already exists before rebuilding:
```python
def build_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
        return Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)

    docs = load_documents("documents")
    chunks = split_documents(docs)
    return Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=PERSIST_DIR)
```
Then performed a one-time clean rebuild:
```bash
rm -rf chroma_db
python embed_store.py
```

**Takeaway:** A persistent vector store needs an explicit "does this already exist" check, the same way you wouldn't want a SQL script to blindly `INSERT` the same rows on every run. This bug was mistakenly diagnosed at first as a chunk-size or retrieval-count (`k`) issue — the real root cause only became clear after directly printing raw retrieved chunks rather than just reading the final generated answer.

---

## 4. Cross-document questions failing to retrieve from multiple sources

**When it happened:** Day 5, testing questions that intentionally spanned two unrelated documents (e.g., "How do GPU computing and networking both play a role in training AI models across multiple machines?").

**Symptom:** The chatbot would only retrieve chunks from one document (usually whichever topic dominated the question's phrasing), and give an incomplete or evasive answer, even though both source documents individually covered relevant material.

**Diagnosis:** A single `similarity_search` call embeds the entire question as one vector. When a question spans two unrelated topics, that single embedding doesn't sit close to either topic's chunks individually — it lands somewhere in between, or gets pulled toward whichever topic is more prominent in the phrasing. This is a known limitation of naive single-query RAG: it works well for focused questions but breaks down for genuinely multi-topic ones.

**Fix:** Implemented query decomposition — using Claude itself to break a complex question into 2-4 simpler standalone sub-questions, retrieving separately for each, then merging and deduplicating the results before generating the final answer:
```python
def decompose_question(question):
    # Ask Claude to split the question into sub-questions
    ...

def retrieve_context_multi(vectorstore, question, k=4):
    sub_questions = decompose_question(question)
    all_chunks = []
    seen_content = set()
    for sub_q in sub_questions:
        for r in vectorstore.similarity_search(sub_q, k=k):
            if r.page_content not in seen_content:
                seen_content.add(r.page_content)
                all_chunks.append(r)
    return all_chunks
```

**Result:** Both relevant documents (`gpu_architecture_primer.pdf` and `networking_fundamentals.pdf`) now show up as sources, and the model correctly synthesizes across both — while still honestly flagging which parts of the question (e.g., specific distributed-training protocols like NCCL) go beyond what the source documents actually cover.

**Takeaway:** Basic single-query RAG has a real, well-known ceiling for multi-topic questions. Query decomposition is a standard technique to address this, at the cost of an extra API call and slightly higher latency per query — a reasonable trade-off for the improvement in answer completeness.

---

## Summary Table

| Bug | Root Cause | Fix |
|---|---|---|
| `ModuleNotFoundError` on text splitter | LangChain package restructuring | Install `langchain-text-splitters`, update import |
| venv activation failing | Shell/OS syntax mismatch (Git Bash hybrid) | Use `source venv/Scripts/activate` |
| Duplicate/repeated chunks in retrieval | `Chroma.from_documents()` re-inserting on every run | Check for existing store before rebuilding |
| Cross-document questions failing | Single embedding can't represent two unrelated topics | Query decomposition into sub-questions |
