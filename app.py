# app.py

import streamlit as st
from embed_store import build_vectorstore
from query import ask

st.set_page_config(page_title="Document Q&A Chatbot", page_icon="📄")
st.title("📄 Document Q&A Chatbot")
st.caption("Ask questions about the documents in your knowledge base.")

# Load the vector store once and cache it, so it doesn't rebuild on every interaction
@st.cache_resource
def get_vectorstore():
    return build_vectorstore()

vectorstore = get_vectorstore()

# Keep chat history across interactions
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Handle new input
question = st.chat_input("Ask a question about your documents...")

if question:
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