# chatbot_page.py
import os
import json
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Groq API Chatbot", page_icon="💬")
st.session_state.system_prompt = \
    "Please transrate your responce in Japanese. And answer only Janapse responce."

with st.sidebar:
    groq_api_key = st.text_input(
        "Groq API Key", key="api_key", type="password", placeholder="gsk_..."
    )
    "[Get an Groq API key](https://console.groq.com/keys)"
    "[View the source code](https://github.com/sgtao/groqai-vectorsearch-by-streamlit/blob/main/pages/02_chatbot_page.py)"

    # SYSTEM_PROMPTの編集
    if st.checkbox('use SYSTEM PROMPT'):
        st.session_state.use_system_prompt = True
        st.session_state.system_prompt = st.text_area(
            "Edit SYSTEM_PROMPT before chat",
            value=st.session_state.system_prompt,
            height=100,
            # disabled=(not "groq_chat_history" in st.session_state),
        )

    # チャット履歴をダウンロードするボタン
    if st.button(
        "Download Chat History ?", disabled=not "groq_chat_history" in st.session_state
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

    if st.button("Clear Chat Message"):
        st.session_state.groq_chat_history = []


st.title("💬 Groq-API Chatbot")
st.write("This page hosts a chatbot interface.")

if not groq_api_key:
    st.info("Please add your API key to continue.")
else:
    # チャット履歴の初期化
    if "groq_chat_history" not in st.session_state:
        st.session_state.groq_chat_history = []
    # ファイルアップロード
    uploaded_file = st.file_uploader(
        "Before 1st question, You can upload an article",
        type=("txt", "md"),
        disabled=(st.session_state.groq_chat_history != []),
    )
    # チャットボットのサンプルコード
    with st.chat_message("assistant"):
        st.write("Hello!! Say something from input")
    # チャット履歴の表示
    for message in st.session_state.groq_chat_history:
        if message["role"] != "system":  # SYSTEM_PROMPTは表示しない
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

if question := st.chat_input("Ask something", disabled=not groq_api_key):
    # ユーザーのメッセージを表示
    with st.chat_message("user"):
        st.markdown(question)

    # promptの作成
    # - 最初のチャットのときに添付ファイルがある場合は、upload_fileをuser_prompt二添付
    user_prompt = ""
    # print(type(uploaded_file)) # At no attachment, <class 'NoneType'>
    if st.session_state.groq_chat_history == [] and uploaded_file is not None:
        article = uploaded_file.read().decode()
        # print(f"attachmented article:{article}")
        user_prompt = f"""Human: Here's an article:\n\n<article>
        {article}\n\n</article>\n\n{question}\n\nAssistant:"""
    else:
        user_prompt = question

    # completionのメッセージを履歴に追加
    st.session_state.groq_chat_history.append({"role": "user", "content": user_prompt})
    # SYSTEM_PROMPTとチャット履歴を連結
    system_prompt_item = [{
        "role": "system",
        "content": st.session_state.system_prompt,
        "name": "userSupplement"
    }]
    if st.session_state.use_system_prompt:
        full_chat_history = system_prompt_item + st.session_state.groq_chat_history
    else:
        full_chat_history = st.session_state.groq_chat_history

    # completionの作成
    if groq_api_key:
        client = Groq(
            api_key=groq_api_key,
        )
        chat_completion = client.chat.completions.create(
            # messages=st.session_state.groq_chat_history,
            messages=full_chat_history,
            model="llama3-8b-8192",
        )
        # print(chat_completion.choices[0].message.content)
        completion = chat_completion.choices[0].message.content
    else:
        completion = user_prompt

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

    # prompt, completionのメッセージを履歴に追加
    st.session_state.groq_chat_history.append(
        {"role": "assistant", "content": completion}
    )
