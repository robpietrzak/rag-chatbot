# query.py

from dotenv import load_dotenv
import os
from anthropic import Anthropic
from embed_store import build_vectorstore

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def retrieve_context(vectorstore, question, k=5):
    results = vectorstore.similarity_search(question, k=k)
    return results

def build_prompt(question, chunks):
    context_text = "\n\n".join(
        f"[Source: {c.metadata.get('source')}]\n{c.page_content}"
        for c in chunks
    )
    prompt = f"""Answer the question using ONLY the context below. If the context doesn't contain the answer, say so clearly instead of guessing.

Context:
{context_text}

Question: {question}

Answer:"""
    return prompt

def ask(vectorstore, question):
    chunks = retrieve_context(vectorstore, question)
    prompt = build_prompt(question, chunks)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.content[0].text
    sources = sorted(set(c.metadata.get("source") for c in chunks))

    return answer, sources

if __name__ == "__main__":
    vectorstore = build_vectorstore()

    question = "How is ketchup made?"
    answer, sources = ask(vectorstore, question)

    print("\n--- Answer ---")
    print(answer)
    print("\n--- Sources ---")
    for s in sources:
        print(f"- {s}")