# search_page.py
import streamlit as st
import requests

# Streamlitページのタイトル表示情報
st.set_page_config(page_title="Search Page", page_icon="🔍️")

# APIエンドポイント
api_base_url = "http://localhost:5000"

if "collection_name" in st.session_state:
    selected_collection = st.session_state.collection_name

if "search_query" in st.session_state:
    search_query = st.session_state.search_query
else:
    search_query = ""

# 近傍結果の指定数
if "number_nearest" in st.session_state:
    number_nearest = st.session_state.number_nearest
else:
    number_nearest = 1


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
    response = requests.get(get_collectiony_url, {})
    if response.status_code == 200:
        result = response.json()
        collection_list = result["collections"]
    else:
        st.error("Failed to get collections")
    return collection_list


def similarity_search(query_text, number_nearest=1):
    collection_name = st.session_state.collection_name
    similarity_url = f"{api_base_url}/collections/{collection_name}/similarity"
    response = requests.post(
        similarity_url, json={"query": query_text, "k": number_nearest}
    )
    if response.status_code == 200:
        result = response.json()
        similar_items = result["similar_items"]
        closest_distance = similar_items[0]["distance"]
        for item in similar_items:
            item_distance = item["distance"]
            rounded_distance = round(item_distance, 3)
            delta = round(item_distance - closest_distance, 3)
            st.metric(
                label="Distance",
                value=rounded_distance,
                delta=delta,
            )
            st.markdown(f"Text: {item['text']}")
    else:
        st.error("Failed to perform similarity search")


# Streamlit のページ生成
with st.sidebar:
    st.session_state.number_nearest = st.slider(
        label="number of nearest neighbors",
        min_value=1,
        max_value=10,
        step=1,
        value=number_nearest,
    )

st.title("🔍️Check Vector Indexies.")

# Embeddingサーバーの存在確認
has_embedding_server = check_exist_embedding_server()
if not has_embedding_server:
    st.error("This page needs embedding-server")
else:
    # コレクションリストの取得
    collections = get_collections()

    # セレクトボックスでコレクションを選択
    st.session_state.collection_name = st.selectbox(
        "Select a collection",
        collections,
    )

    # 選択したコレクション名をセッションステートに保存
    # if selected_collection:
    #     st.session_state.collection_name = selected_collection

    # クエリテキストの入力
    st.session_state.search_query = st.text_input(
        "Enter text to search for similar collections", value=search_query
    )

    # 検索ボタンが押されたときの処理
    if st.button("Search"):
        similarity_search(
            st.session_state.search_query, st.session_state.number_nearest
        )
