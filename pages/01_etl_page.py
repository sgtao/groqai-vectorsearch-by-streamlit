# etl_page.py
import streamlit as st
import PyPDF2

st.set_page_config(page_title="ETL Page", page_icon="🔄")

st.title("🔄ETL Processing")
st.write("This page is dedicated to ETL (Extract, Transform, Load) operations.")


# PDFファイルのアップロード
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
extract_items = []
num_pages = 0

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
    # st.write(extract_items)
    for item in extract_items:
        st.write(f"{item}")

    st.error("Transform function has not been implemented!")
    return False

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
