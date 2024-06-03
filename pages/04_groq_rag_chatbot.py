# chatbot_page.py
import os
import json
import streamlit as st
from groq import Groq
import requests
from datetime import datetime

# ページの設定
st.set_page_config(page_title="Groq API RAG Chatbot", page_icon="💬")

if "groq_api_key" in st.session_state:
    groq_api_key = st.session_state.groq_api_key
else:
    groq_api_key = ""

st.session_state.system_prompt = (
    """You are a helpful assistant. And response in only Japanese.
    Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
    Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.
    Overall, Assistant is a powerful system that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.`;
    You must only use information from the provided search results.
    Use an unbiased and journalistic tone.
    Combine search results together into a coherent answer.
    Do not repeat text.
    Place these citations at the end of the sentence or paragraph that reference them - do not put them all at the end.
    If different results refer to different entities within the same name, write separate answers for each entity.
    If there is nothing in the context relevant to the question at hand, just say "Hmm, I'm not sure." Don't try to make up an answer.

    You should use bullet points in your answer for readability
    Put citations where they apply rather than putting them all at the end.

    Anything between the following `context`  html blocks is search result retrieved from a knowledge bank,  not part of the conversation with the user.
    """
)
# チャット履歴の初期化
if "groq_chat_history" not in st.session_state:
    st.session_state.groq_chat_history = []

# APIエンドポイント
api_base_url = "http://localhost:5000"

# 初回のみサーバーの存在を確認
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

if "has_embedding_server" not in st.session_state:
    st.session_state.has_embedding_server = check_exist_embedding_server()


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
    closest_text = ""
    if response.status_code == 200:
        result = response.json()
        similar_items = result["similar_items"]
        # closest_distance = similar_items[0]["distance"]
        closest_text = similar_items[0]["text"]
    else:
        st.error("Failed to perform similarity search")
    return closest_text


with st.sidebar:
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
    "[View the source code](https://github.com/sgtao/groqai-vectorsearch-by-streamlit/blob/main/pages/)"

    # SYSTEM_PROMPTの編集
    if st.checkbox(
        "use SYSTEM PROMPT",
        value=True,
    ):
        st.session_state.use_system_prompt = True
        st.session_state.system_prompt = st.text_area(
            "Edit SYSTEM_PROMPT before chat",
            value=st.session_state.system_prompt,
            height=100,
            # disabled=(not st.session_state.no_chat_history),
            disabled=(st.session_state.groq_chat_history != []),
        )
    else:
        st.session_state.use_system_prompt = False

    # Completion Parameterの調整
    if st.checkbox("change Completion Prams."):
        # モデル選択
        llm_model = st.selectbox(
            "Select Model",
            ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"],
            index=0
        )
        # Parameterの調整
        max_tokens = st.slider("max_tokens", 1024, 8192, 8192, 1)
        temperature = st.slider("temperature", 0.0, 1.0, 0.0, 0.1)
        top_p = st.slider("top_p", 0.0, 1.0, 0.0, 0.1)
    else:
        llm_model = "llama3-8b-8192"
        max_tokens = 8192
        temperature = 0.0
        top_p = 0.0

    # チャット履歴をダウンロードするボタン
    if st.checkbox(
        "Download Chat History ?",
        # disabled=(not st.session_state.no_chat_history),
        disabled=("groq_chat_history" not in st.session_state),
    ):
        chat_history_json = json.dumps(
            st.session_state.groq_chat_history, ensure_ascii=False, indent=4
        )
        # define collection_name
        now = datetime.now()
        saved_file_name = now.strftime("%y%m%d_%H%M%S_chat_history.json")  # %yで2桁の年、%Hで24h表記
        st.download_button(
            label="Download chat_history.json",
            data=chat_history_json,
            file_name=saved_file_name,
            mime="application/json",
        )

    if st.button("Clear Chat Message (click 2 times)"):
        st.session_state.groq_chat_history = []

st.title("💬 Groq-API RAG Chatbot")
st.write("This page hosts a chatbot interface.")

if not groq_api_key:
    st.info("Please add your API key to continue.")
else:
    if not st.session_state.has_embedding_server:
        st.error("This page needs embedding-server")
    else:
        # コレクションリストの取得
        collections = get_collections()

        # セレクトボックスでコレクションを選択
        st.session_state.collection_name = st.selectbox("Select a collection", collections)

    # ファイルアップロード
    uploaded_file = st.file_uploader(
        "Before 1st question, You can upload an article",
        type=("txt", "md"),
        disabled=(st.session_state.groq_chat_history != []),
    )
    # チャットボットの最初の表示メッセージ
    with st.chat_message("assistant"):
        st.write("Hello!! Say something from input")
    # チャット履歴の表示
    for message in st.session_state.groq_chat_history:
        if message["role"] != "system":  # SYSTEM_PROMPTは表示しない
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


# PDFファイルのアップロード
if not st.session_state.has_embedding_server:
    st.error("This page needs embedding-server")
else:
    if question := st.chat_input("Ask something", disabled=not groq_api_key):

        # promptの作成
        user_prompt = ""
        if st.session_state.groq_chat_history == []:
            # 最初のチャットの場合：
            # ユーザーの質問を表示
            # with st.chat_message("user"):
            #     st.markdown(question)

            # 類似検索を実行
            closest_text = similarity_search(question)
            # SYSTEM_PROMPTをメッセージに連結
            if st.session_state.use_system_prompt:
                systemp_prompt = st.session_state.system_prompt + \
                    f"""
                    <context>
                    {closest_text}
                    </context>
                    """
                system_prompt_item = [
                    {
                        "role": "system",
                        "content": systemp_prompt,
                        "name": "userSupplement",
                    }
                ]
                st.session_state.groq_chat_history = system_prompt_item

            # 最初のチャットで添付ファイルがある場合、upload_fileをuser_promptに添付
            # print(type(uploaded_file)) # At no attachment, <class 'NoneType'>
            if uploaded_file is not None:
                article = uploaded_file.read().decode()
                # print(f"attachmented article:{article}")
                user_prompt = f"""Human: Here's an article(添付ファイル):\n\n<article>
                {article}\n\n</article>\n\n{question}\n\nAssistant:"""
            else:
                user_prompt = question

        else:
            # 継続チャットの場合：
            user_prompt = question

        # completionのメッセージを履歴に追加
        st.session_state.groq_chat_history.append({"role": "user", "content": user_prompt})

        # ユーザーのメッセージを表示
        with st.chat_message("user"):
            st.markdown(user_prompt)

        # completionの作成
        if groq_api_key:
            client = Groq(
                api_key=groq_api_key,
            )
            chat_completion = client.chat.completions.create(
                messages=st.session_state.groq_chat_history,
                model=llm_model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            # print(chat_completion.choices[0].message.content)
            completion = chat_completion.choices[0].message.content
        else:
            completion = user_prompt

        # prompt, completionのメッセージを履歴に追加
        st.session_state.groq_chat_history.append(
            {"role": "assistant", "content": completion}
        )

        # コンプリーションメッセージを表示
        with st.chat_message("assistant"):
            st.markdown(completion)

        # 最後のメッセージまでスクロール
        st.markdown(
            """
            <script>
                const chatContainer = window.parent.document.querySelector(".chat-container");
                chatContainer.scrollTop = chatContainer.scrollHeight;
            </script>
            """,
            unsafe_allow_html=True,
        )

