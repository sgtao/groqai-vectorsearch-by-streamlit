# chatbot_page.py
import streamlit as st

st.set_page_config(page_title="Chatbot Page", page_icon="💬")

st.title("💬 Chatbot")
st.write("This page hosts a chatbot interface.")

# チャットボットのサンプルコード
with st.chat_message("assistant"):
    st.write("Hello!! Say something from input")

if prompt := st.chat_input("Say something"):
    st.chat_message("user").write(prompt)
    st.chat_message("assistant").write(f"Echo: {prompt}")
