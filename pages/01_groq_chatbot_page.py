# chatbot_page.py
import os
import json
import streamlit as st
from groq import Groq

# ページの設定
st.set_page_config(page_title="Groq API Chatbot", page_icon="💬")

if "groq_api_key" in st.session_state:
    groq_api_key = st.session_state.groq_api_key
else:
    groq_api_key = ""

st.session_state.system_prompt = (
    "You are a helpful assistant. And response in only Japanese."
)
# チャット履歴の初期化
if "groq_chat_history" not in st.session_state:
    st.session_state.groq_chat_history = []

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
    "[View the source code](https://github.com/sgtao/groqai-vectorsearch-by-streamlit/blob/main/pages/02_chatbot_page.py)"

    # SYSTEM_PROMPTの編集
    if st.checkbox(
        "use SYSTEM PROMPT", disabled=(st.session_state.groq_chat_history != [])
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
        disabled=("groq_chat_history" not in st.session_state),
    ):
        chat_history_json = json.dumps(
            st.session_state.groq_chat_history, ensure_ascii=False, indent=4
        )
        st.download_button(
            label="Download chat_history.json",
            data=chat_history_json,
            file_name="chat_history.json",
            mime="application/json",
        )

    if st.button("Clear Chat Message (click 2 times)"):
        st.session_state.groq_chat_history = []

st.title("💬 Groq-API Chatbot")
st.write("This page hosts a chatbot interface.")

if not groq_api_key:
    st.info("Please add your API key to continue.")
else:
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

if question := st.chat_input("Ask something", disabled=not groq_api_key):

    # promptの作成
    user_prompt = ""
    if st.session_state.groq_chat_history == []:
        # 最初のチャットの場合：
        # SYSTEM_PROMPTをメッセージに連結
        if st.session_state.use_system_prompt:
            system_prompt_item = [
                {
                    "role": "system",
                    "content": st.session_state.system_prompt,
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
