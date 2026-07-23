from embed_store import build_vectorstore

vectorstore = build_vectorstore()
results = vectorstore.similarity_search(
    "Walk me through what happens from when a chunk is created to when a final answer is generated in a RAG system.",
    k=5
)

for i, r in enumerate(results):
    print(f"\n--- Chunk {i+1} (source: {r.metadata.get('source')}) ---")
    print(r.page_content[:150])