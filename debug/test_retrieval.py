# test_retrieval.py

from embed_store import build_vectorstore

vectorstore = build_vectorstore()

query = "What is a Streaming Multiprocessor?"
results = vectorstore.similarity_search(query, k=2)

for i, r in enumerate(results):
    print(f"\n--- Result {i+1} (source: {r.metadata.get('source')}) ---")
    print(r.page_content)