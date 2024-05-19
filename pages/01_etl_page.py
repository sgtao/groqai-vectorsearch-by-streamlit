# etl_page.py
import os
import streamlit as st
import PyPDF2
from groq import Groq
import requests
import faiss
import numpy as np
import pandas as pd
import torch

# Streamlitページのタイトル表示情報
st.set_page_config(page_title="ETL Page", page_icon="🔄")

st.title("🔄ETL Processing")
st.write("This page is dedicated to ETL (Extract, Transform, Load) operations.")

# Groqクライアントの初期化
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("APIキーが設定されていません。")
    st.stop()



# PDFファイルのアップロード
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
extract_items = []
num_pages = 0
faiss_index_db = None

# ETL処理の関数
def extract_process(pdf_file):
    # PDFファイルの読み込み
    with open(pdf_file.name, "wb") as f:
        f.write(pdf_file.getbuffer())

    file_title = pdf_file.name

    # PDFファイルの処理
    with open(pdf_file.name, "rb") as f:
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
                "text": text
            }
            # extract_itemsリストにページの情報を追加
            extract_items.append(page_item)
            
            st.write(f"Page {page_num+1}: {text}")

    st.success("ETL process completed. Continue to Transform Process.")
    return True

def transform_process():
    groq_client = Groq(api_key=api_key)
    # APIエンドポイント
    api_url = "http://localhost:5000/encoding"

    # st.write(extract_items)
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
        sentences = item['text']
        response = requests.post(api_url, json={"sentences": sentences})
        if response.status_code == 200:
            embeddings = response.json().get("embeddings", [])
            st.write("Vector representation for page", item['pageNumber'])
            st.write(embeddings)
            # NumPy配列に変換してリストに追加
            embeddings_np = np.array(embeddings)
            embeddings_tensor = torch.tensor(embeddings_np).float()
            # Tensorに追加
            items_embeddings = torch.cat((items_embeddings, embeddings_tensor.unsqueeze(0)), dim=0)
        else:
            st.error("Failed to get embeddings from API")
            return False

    # FAISSインデックスの作成
    if items_embeddings.size(0) > 0:
        # dimension = items_embeddings[0].shape[1]
        # dimension = len(items_embeddings[0])
        dimension = items_embeddings.size(1)
        faiss_index_db = faiss.IndexFlatL2(dimension)

        # リストをNumPy配列に変換してFAISSインデックスに追加
        # items_embeddings_np = np.vstack(items_embeddings)
        # faiss_index_db.add(items_embeddings_np)
        faiss_index_db.add(items_embeddings.detach().cpu().numpy())

        st.success("FAISS index created successfully!")
        # st.write(faiss_index_db)

    return True

def save_data_process():
    st.error("Save function has not been implemented!")
    return False


# ETL処理の実行
if uploaded_file is None:
    st.warning("Please upload a PDF file first.")
else:
    if st.button("Run ETL"):
        with st.status("ETL processing ...", expanded=True) as status:
            extract_items = []
            num_pages = 0
            if extract_process(uploaded_file) == False:
                st.warning("Extract Process is failed.")
                st.stop()

            if transform_process() == False:
                st.warning("Transform Process is failed.")
                st.stop()

            if save_data_process() == False:
                st.warning("Save Process is failed.")
                st.stop()

            st.success("ETL process finished!")
