# search_page.py
import streamlit as st
import requests
import numpy as np
import pandas as pd

# Streamlitページのタイトル表示情報
st.set_page_config(page_title="Search Page", page_icon="🔍️")

# APIエンドポイント
api_base_url = "http://localhost:5000"

def check_exist_embedding_server():
    echo_path = api_base_url + "/echo"
    try:
        response = requests.get(echo_path)
        if response.status_code == 200:
            print("Exist Embedding Server")
            # st.success("Exist Embedding Server")
            return True
        else:
            print("No Embedding Server")
            st.error("No Embedding Server")
            return False
    except Exception as e:
        print(f"Failed to access server: {e}")  # デバッグ用プリント文
        return False


def similarity_search(query_text):
    api_base_url = "http://localhost:5000"
    collection_name = st.session_state.collection_name
    similarity_url = f"{api_base_url}/collections/{collection_name}/similarity"
    response = requests.post(similarity_url, json={"query": query_text})
    closest_text = ""
    if response.status_code == 200:
        result = response.json()
        st.write(f"Distance: {result['distance']}")
        closest_text = result["closest_text"]
        st.write(f"Text: { closest_text }")
    else:
        st.error("Failed to perform similarity search")
    return closest_text


# Streamlit のページ生成
st.title("🔍️Check Vector Indexies.")

# PDFファイルのアップロード
has_embedding_server = check_exist_embedding_server()
if not has_embedding_server:
    st.error("This page needs embedding-server")
else:
    query_text = st.text_input("Enter text to search for similar collections")
    if st.button("Search"):
        similarity_search(query_text)

