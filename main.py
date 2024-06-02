# main.py
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="LLM-RAG App",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "groq_api_key" in st.session_state:
    groq_api_key = st.session_state.groq_api_key
else:
    groq_api_key = ""

# サイドバーの設定
with st.sidebar:
    st.sidebar.title("Navigation")
    st.sidebar.success("Select a page above.")

    # API-KEYの設定
    st.session_state.groq_api_key = st.text_input(
        "Groq API Key",
        key="api_key",
        type="password",
        placeholder="gsk_...",
        value=groq_api_key,
    )
    groq_api_key = st.session_state.groq_api_key
    "[Get an Groq API key](https://console.groq.com/keys)"
    "[View the source code](https://github.com/sgtao/groqai-vectorsearch-by-streamlit/blob/main/main.py)"


# メインページのコンテンツ
st.title("🚀 Welcome to the LLM-RAG App")
st.write(
    "This app demonstrates multi pages streamlit application with ETL and Chatbot functionalities."
)
