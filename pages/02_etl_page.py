# etl_page.py
import os
from datetime import datetime
import streamlit as st
import PyPDF2
import requests
import torch
import tempfile
from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken

# Streamlitページのタイトル表示情報
st.set_page_config(page_title="ETL Page", page_icon="🔄")

# ETLページ関連の情報の初期化
if "collection_name" not in st.session_state:
    st.session_state.collection_name = ""
    st.session_state.etl_success = False
    st.session_state.extract_items = []

max_chunk_size = 512
if "chunk_size" not in st.session_state:
    st.session_state.chunk_size = max_chunk_size

if "chunk_overlap" not in st.session_state:
    st.session_state.chunk_overlap = 0

# APIエンドポイント
api_base_url = "http://localhost:5000"

def check_exist_embedding_server():
    echo_path = api_base_url + "/echo"
    try:
        response = requests.get(echo_path)
        if response.status_code == 200:
            print("Exist Embedding Server")
            return True
        else:
            print("No Embedding Server")
            st.error("No Embedding Server")
            return False
    except Exception as e:
        print(f"Failed to access server: {e}")
        return False


# ETL処理の関数
def extract_process(pdf_file):
    # 一時ディレクトリの作成
    temporal_dir = "temporal_storage"
    os.makedirs(temporal_dir, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=temporal_dir) as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, pdf_file.name)

        # トークナイザーの設定
        # TokenTextSplitterの設定
        chunk_size = st.session_state.chunk_size
        chunk_overlap_percentage = st.session_state.chunk_overlap
        chunk_overlap = int(chunk_size * (chunk_overlap_percentage / 100))
        st.write(f"Extract Parameter: size={chunk_size}, overlap={chunk_overlap}")
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            model_name="gpt-4",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

        # PDFファイルの保存
        with open(temp_pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        file_title = pdf_file.name

        # PDFファイルの処理
        with open(temp_pdf_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            num_pages = len(pdf_reader.pages)
            st.header(f"File: {file_title}")
            st.write(f"Number of pages: {num_pages}")

            # 各ページのテキストを抽出
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()

                # テキストをトークン単位で分割
                chunks = text_splitter.split_text(text)

                # 各チャンクをページ情報として保存
                for chunk in chunks:
                    page_item = {
                        "title": file_title,
                        "pageNumber": page_num + 1,
                        "text": chunk,
                    }
                    extract_items.append(page_item)

                # st.write(f"Page {page_num+1}: {text}")

            # show chunks
            for item in extract_items:
                page_number = item["pageNumber"]
                text = item["text"]
                st.markdown(f"Page {page_number}: {text}")

            # st.session_state.extract_items = extract_items

        st.success("Extract process completed. Continue to Transform Process.")
        return True


def transform_process(collection_name):
    # embedding_url = api_base_url + "/encoding"

    # ベクトル値の取得
    items_embeddings = torch.tensor([])
    texts = []
    for item in extract_items:
        # st.write(f"{item}")
        sentence = item["text"]
        # st.write(sentence)
        texts.append(sentence)

    # collections（FAISSインデックス）の作成
    create_index_url = api_base_url + "/collections/" + st.session_state.collection_name
    print(f"put URL is {create_index_url}")
    if len(texts) > 0:
        request_body = {"texts": texts}
        response = requests.put(create_index_url, json=request_body)
        print(f"response_state is {response.status_code}")
        if response.status_code == 201:
            print("FAISS index created successfully!")
            st.success("Transfer process completed.")
        else:
            print("Failed to create FAISS index")
            st.error("Failed to create FAISS index")
            return False

    return True


# def save_data_process():
#     st.error("Save function has not been implemented!")
#     return False


# Streamlit のページ生成
with st.sidebar:
    # Extract Parameterの調整
    if st.checkbox("change Chunk Parameters."):
        # Parameterの調整
        st.session_state.chunk_size = st.slider(
            label="chunk_size(token)",
            min_value=128,
            max_value=max_chunk_size,
            step=16,
            value=st.session_state.chunk_size,
        )
        st.session_state.chunk_overlap = st.slider(
            label="overlap(%) is not work at model",
            min_value=0,
            max_value=50,
            step=5,
            value=st.session_state.chunk_overlap,
            disabled=True,
        )


st.title("🔄ETL Processing")
st.write("This page is dedicated to ETL (Extract, Transform, Load) operations.")


# PDFファイルのアップロード
has_embedding_server = check_exist_embedding_server()
if not has_embedding_server:
    st.error("This page needs embedding-server")
else:
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

                # define collection_name
                now = datetime.now()
                collection_name = now.strftime("%y%m%d-%H%M%S")  # %yで2桁の年、%Hで24h表記
                st.session_state.collection_name = collection_name

                if transform_process(collection_name) == False:
                    st.warning("Transform Process is failed.")
                    st.stop()

                # if save_data_process() == False:
                #     st.warning("Save Process is failed.")
                #     st.stop()
                st.session_state.etl_success = True
                st.success(f"ETL process success! - collection : {collection_name} -")

