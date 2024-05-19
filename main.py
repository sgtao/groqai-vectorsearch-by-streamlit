# main.py
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="LLM-RAG App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# サイドバーの設定
st.sidebar.title("Navigation")
st.sidebar.success("Select a page above.")

# メインページのコンテンツ
st.title("Welcome to the LLM-RAG App")
st.write("This app demonstrates a multi-page Streamlit application with ETL and Chatbot functionalities.")
