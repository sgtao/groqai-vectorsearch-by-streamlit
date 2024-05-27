# etl_page.py
import os
from datetime import datetime
import streamlit as st
import PyPDF2
from groq import Groq
import requests
import faiss
import numpy as np
import pandas as pd
import torch
import tempfile

# Streamlitページのタイトル表示情報
st.set_page_config(page_title="ETL Page", page_icon="🔄")

# ETLページ関連の情報の初期化
if "collection_name" not in st.session_state:
    st.session_state.collection_name = ""
    st.session_state.etl_success = False
    st.session_state.extract_items = []


# ETL処理の関数
def extract_process(pdf_file):
    # 一時ディレクトリの作成
    temporal_dir = "temporal_storage"
    os.makedirs(temporal_dir, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temporal_dir) as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, pdf_file.name)

        # PDFファイルの保存
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        file_title = pdf_file.name

        # PDFファイルの処理
        with open(temp_pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            st.write(f"Number of pages: {num_pages}")

            # 各ページのテキストを抽出
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                # ページの情報を辞書形式で作成
                page_item = {
                    "title": file_title,
                    "pageNumber": page_num + 1,
                    "text": text,
                }
                # extract_itemsリストにページの情報を追加
                extract_items.append(page_item)
                st.session_state.extract_items.append(page_item)

                st.write(f"Page {page_num+1}: {text}")

        # st.session_state.extract_items = extract_items
        st.success("Extract process completed. Continue to Transform Process.")
        return True


def transform_process():
    # APIエンドポイント
    api_base_url = "http://localhost:5000"
    embedding_url = api_base_url + "/encoding"

    # ベクトル値の取得
    items_embeddings = torch.tensor([])
    for item in extract_items:
        st.write(f"{item}")
        # Groq APIを使用してベクトル情報に変換
        # vector = groq_client.encode(item['text'])
        # st.write(f"Vector representation:{vector}")
        # response = groq_client.embeddings.create(
        #     # model="nomic-embed-text-v1.5",
        #     model="ada-30b-4096",
        #     input=item['text']
        # )
        # st.write("Vector representation:")
        # st.write(response['data'])
        sentences = item["text"]
        response = requests.post(embedding_url, json={"sentences": sentences})
        if response.status_code == 200:
            embeddings = response.json().get("embeddings", [])
            st.write("Vector representation for page", item["pageNumber"])
            st.write(embeddings)
            # NumPy配列に変換してリストに追加
            embeddings_np = np.array(embeddings)
            embeddings_tensor = torch.tensor(embeddings_np).float()
            # Tensorに追加
            items_embeddings = torch.cat(
                (items_embeddings, embeddings_tensor.unsqueeze(0)), dim=0
            )
        else:
            st.error("Failed to get embeddings from API")
            return False

    # FAISSインデックスの作成
    now = datetime.now()
    collection_name = now.strftime("%y%m%d-%H%M%S")  # %yで2桁の年、%Hで24h表記
    create_index_url = api_base_url + "/collections/" + collection_name
    st.session_state.collection_name = collection_name
    print(f"put URL is {create_index_url}")
    # put URL is http://localhost:5000/collections/240527-065556
    print(type(items_embeddings))
    # <class 'torch.Tensor'>
    if items_embeddings.size(0) > 0:
        # Tensorをリストに変換
        items_embeddings_list = items_embeddings.detach().cpu().numpy().tolist()
        request_body = {"embedding_reference": items_embeddings_list}
        # print(request_body)
        response = requests.put(create_index_url, json=request_body)
        print(f"response_state is {response.status_code}")
        if response.status_code == 201:
            print("FAISS index created successfully!")
        else:
            print("Failed to create FAISS index")
            return False

    return True


# def save_data_process():
#     st.error("Save function has not been implemented!")
#     return False


def similarity_search(query_text):
    api_base_url = "http://localhost:5000"
    collection_name = st.session_state.collection_name
    similarity_url = f"{api_base_url}/collections/{collection_name}/similarity"
    response = requests.post(similarity_url, json={"query": query_text})
    if response.status_code == 200:
        result = response.json()
        closest_point_id = result["closest_point_id"]
        st.write(f"Closest point ID: {closest_point_id}")
        st.write(f"Distance: {result['distance']}")
        result_item = st.session_state.extract_items[closest_point_id]
        st.write(f"Page: {result_item['pageNumber']} at {result_item['title']}")
        st.write(f"Text: {result_item['text']}")
    else:
        st.error("Failed to perform similarity search")


# Streamlit のページ生成
st.title("🔄ETL Processing")
st.write("This page is dedicated to ETL (Extract, Transform, Load) operations.")


# PDFファイルのアップロード
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
extract_items = []
num_pages = 0
faiss_index_db = None

st.session_state.etl_success = False


# ETL処理の実行
if uploaded_file is None:
    st.warning("Please upload a PDF file first.")
else:
    if st.button("Run ETL"):
        st.session_state.etl_success = False
        with st.status("ETL processing ...", expanded=True) as status:
            extract_items = []
            st.session_state.extract_items = []
            num_pages = 0
            if extract_process(uploaded_file) == False:
                st.warning("Extract Process is failed.")
                st.stop()

            if transform_process() == False:
                st.warning("Transform Process is failed.")
                st.stop()

            # if save_data_process() == False:
            #     st.warning("Save Process is failed.")
            #     st.stop()
            st.session_state.etl_success = True
            st.success("ETL process finished!")

st.title("🔍️Check Vector Indexies.")
query_text = st.text_input("Enter text to search for similar collections")
if st.button("Search"):
    similarity_search(query_text)
