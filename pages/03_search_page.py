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

def get_collections():
    collection_list = []
    get_collectiony_url = f"{api_base_url}/collections"
    response = requests.get(get_collectiony_url,{})
    if response.status_code == 200:
        result = response.json()
        collection_list = result["collections"]
    else:
        st.error("Failed to get collections")
    return collection_list



def similarity_search(query_text):
    collection_name = st.session_state.collection_name
    similarity_url = f"{api_base_url}/collections/{collection_name}/similarity"
    response = requests.post(similarity_url, json={"query": query_text})
    closest_text = ""
    if response.status_code == 200:
        result = response.json()
        st.write(f"Distance: {result['distance']}")
        closest_text = result["closest_text"]
        st.markdown(f"Text: { closest_text }")
    else:
        st.error("Failed to perform similarity search")
    return closest_text


# Streamlit のページ生成
st.title("🔍️Check Vector Indexies.")

# Embeddingサーバーの存在確認
has_embedding_server = check_exist_embedding_server()
if not has_embedding_server:
    st.error("This page needs embedding-server")
else:
    # コレクションリストの取得
    collections = get_collections()

    # セレクトボックスでコレクションを選択
    selected_collection = st.selectbox("Select a collection", collections)

    # 選択したコレクション名をセッションステートに保存
    if selected_collection:
        st.session_state.collection_name = selected_collection

    # クエリテキストの入力
    query_text = st.text_input("Enter text to search for similar collections")

    # 検索ボタンが押されたときの処理
    if st.button("Search"):
        similarity_search(query_text)
