# utils/chat_utils.py
import streamlit as st

def init_chat(clear=False):
    if clear or "chat_history" not in st.session_state:
        st.session_state.chat_history = []

def render_chat_interface(agent, df):
    st.header("💬 Chat with Cybersecurity Agent")
    user_input = st.text_input("Ask a question about the simulation/data")

    if user_input:
        with st.spinner("Generating response..."):
            response = agent._run_llm(user_input)
            st.markdown(f"**Response:** {response}")

    st.subheader("Chat History")
    for entry in reversed(st.session_state.chat_history):
        if entry["role"] == "user":
            st.markdown(f"🧑‍💻 **You**: {entry['content']}")
        else:
            st.markdown(f"🤖 **Agent**: {entry['content']}")
