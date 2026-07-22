from embed_store import build_vectorstore

vectorstore = build_vectorstore()
results = vectorstore.similarity_search("TCP versus UDP", k=5)

for i, r in enumerate(results):
    print(f"\n--- Chunk {i+1} (source: {r.metadata.get('source')}) ---")
    print(r.page_content)