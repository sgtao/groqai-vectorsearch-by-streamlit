# show_chat_history.py
import json
import streamlit as st
from groq import Groq
from datetime import datetime

# ページの設定
st.set_page_config(page_title="Chat with Past History", page_icon="💬")

if "groq_api_key" in st.session_state:
    groq_api_key = st.session_state.groq_api_key
else:
    groq_api_key = ""


st.title("💬 Chat with Past History")
st.write("This page show saved chat history JSON with chatbot style.")

# JSONファイルの読み込み
def load_chat_history(file):
    return json.load(file)

# チャット履歴の表示
def show_chat_history():
    for message in st.session_state.shown_chat_history:
        if message["role"] != "system":  # SYSTEM_PROMPTは表示しない
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

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

    # Completion Parameterの調整
    if st.checkbox("change Completion Prams."):
        # モデル選択
        llm_model = st.selectbox(
            "Select Model",
            ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"],
            index=0
        )
        # Parameterの調整
        max_tokens = st.slider("max_tokens", 1024, 8192, 2048, 1)
        temperature = st.slider("temperature", 0.0, 1.0, 0.0, 0.1)
        top_p = st.slider("top_p", 0.0, 1.0, 0.0, 0.1)
    else:
        llm_model = "llama3-8b-8192"
        max_tokens = 2048
        temperature = 0.0
        top_p = 0.0

    # チャット履歴をダウンロードするボタン
    if st.checkbox(
        "Download Chat History ?",
        # disabled=(not st.session_state.no_chat_history),
        disabled=("shown_chat_history" not in st.session_state),
    ):
        chat_history_json = json.dumps(
            st.session_state.shown_chat_history, ensure_ascii=False, indent=4
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
        st.session_state.shown_chat_history = []


# チャット履歴の初期化／表示
uploaded_file = st.file_uploader("Choose a JSON file", type="json")
if uploaded_file is not None:
    st.session_state.shown_chat_history = load_chat_history(uploaded_file)

if st.checkbox(
    "Show Chat History ?",
    disabled=(uploaded_file is None),
):
    show_chat_history()

    if question := st.chat_input("Say something"):
        # ユーザーのメッセージを表示
        show_chat_history()
        with st.chat_message("user"):
            st.markdown(question)

        # completionのメッセージを履歴に追加
        st.session_state.shown_chat_history.append({"role": "user", "content": question})

        # completionメッセージを生成
        if groq_api_key:
            client = Groq(
                api_key=groq_api_key,
            )
            chat_completion = client.chat.completions.create(
                messages=st.session_state.shown_chat_history,
                model=llm_model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p
            )
            # print(chat_completion.choices[0].message.content)
            completion = chat_completion.choices[0].message.content
        else:
            completion = question

        # prompt, completionのメッセージを履歴に追加
        st.session_state.shown_chat_history.append(
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

        # question, completionのメッセージを履歴に追加
        st.session_state.shown_chat_history.append({"role": "user", "content": question})
        st.session_state.shown_chat_history.append({"role": "assistant", "content": completion})

