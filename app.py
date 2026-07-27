# app.py

import streamlit as st
from embed_store import build_vectorstore
from query import ask

st.set_page_config(page_title="Document Q&A Chatbot", page_icon="📄")
st.title("📄 Document Q&A Chatbot")
st.caption("Ask questions about the documents in your knowledge base.")

MAX_QUERIES_PER_SESSION = 15

@st.cache_resource
def get_vectorstore():
    return build_vectorstore()

vectorstore = get_vectorstore()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "query_count" not in st.session_state:
    st.session_state.query_count = 0

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Ask a question about your documents...")

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