# query.py

from dotenv import load_dotenv
import os
from anthropic import Anthropic
from embed_store import build_vectorstore

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def decompose_question(question):
    prompt = f"""Break the following question into 2-4 simpler, standalone sub-questions that together would help answer it. If the question is already simple and doesn't need breaking down, just return it as-is as a single sub-question.

Question: {question}

Return ONLY the sub-questions, one per line, with no numbering or extra text."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )

    sub_questions = [
        line.strip() for line in response.content[0].text.split("\n")
        if line.strip()
    ]
    return sub_questions


def retrieve_context_multi(vectorstore, question, k=4):
    sub_questions = decompose_question(question)
    print(f"Sub-questions: {sub_questions}")

    all_chunks = []
    seen_content = set()

    for sub_q in sub_questions:
        results = vectorstore.similarity_search(sub_q, k=k)
        for r in results:
            if r.page_content not in seen_content:
                seen_content.add(r.page_content)
                all_chunks.append(r)

    return all_chunks


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
    chunks = retrieve_context_multi(vectorstore, question)
    prompt = build_prompt(question, chunks)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.content[0].text
    sources = sorted(set(c.metadata.get("source") for c in chunks))

    return answer, sources


if __name__ == "__main__":
    vectorstore = build_vectorstore()

    question = "How might GPU computing and networking both play a role in training a large AI model across multiple machines?"
    answer, sources = ask(vectorstore, question)

    print("\n--- Answer ---")
    print(answer)
    print("\n--- Sources ---")
    for s in sources:
        print(f"- {s}")