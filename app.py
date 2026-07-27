# app.py

import streamlit as st
from embed_store import build_vectorstore
from query import ask

st.set_page_config(page_title="Document Q&A Chatbot", page_icon="📄")
st.title("📄 Document Q&A Chatbot")
st.caption("Ask questions about Robert's skills, projects, and experience.")

MAX_QUERIES_PER_SESSION = 15

# Load the vector store once and cache it, so it doesn't rebuild on every interaction
@st.cache_resource
def get_vectorstore():
    return build_vectorstore()

vectorstore = get_vectorstore()

# Keep chat history and usage count across interactions
if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# Example questions recruiters can click instead of typing from scratch
example_questions = [
    "What certifications does Robert have?",
    "How does Robert's hardware background connect to GPU technology?",
    "Does Robert have Kubernetes experience?",  # deliberately triggers the no-answer-found fallback
]

st.write("**Try asking:**")
cols = st.columns(len(example_questions))
for col, q in zip(cols, example_questions):
    if col.button(q):
        st.session_state.pending_question = q

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Handle new input — either typed or from a clicked example button
typed_question = st.chat_input("Ask about Robert's skills, projects, or experience...")
question = st.session_state.pending_question or typed_question
st.session_state.pending_question = None  # reset so it doesn't re-fire on rerun

if question:
    if st.session_state.query_count >= MAX_QUERIES_PER_SESSION:
        st.warning("Demo limit reached for this session. Thanks for trying it out!")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer, sources = ask(vectorstore, question)
            st.write(answer)
            if sources:
                st.caption("Sources: " + ", ".join(sources))

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.query_count += 1