# chatbot_page.py
import os
import streamlit as st
from groq import Groq

st.set_page_config(page_title="Groq API Chatbot", page_icon="💬")

with st.sidebar:
    groq_api_key = st.text_input("Groq API Key", key="file_qa_api_key", type="password", placeholder="gsk_...")
    "[Get an Groq API key](https://console.groq.com/keys)"
    "[View the source code](https://github.com/sgtao/groqai-vectorsearch-by-streamlit/blob/main/pages/02_chatbot_page.py)"

st.title("💬 Chatbot")
st.write("This page hosts a chatbot interface.")

# チャットボットのサンプルコード
with st.chat_message("assistant"):
    st.write("Hello!! Say something from input")
# チャット履歴の初期化／表示
def show_chat_history():
    if "groq_chat_history" not in st.session_state:
        st.session_state.groq_chat_history = []
    else:
        for message in st.session_state.groq_chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


if not groq_api_key:
    st.info("Please add your API key to continue.")
else:
    show_chat_history()

if question := st.chat_input("Ask something"):
    # ユーザーのメッセージを表示
    with st.chat_message("user"):
        st.markdown(question)

    # promptの作成
    user_prompt = question

    # completionの作成
    if groq_api_key:
        client = Groq(
            api_key=groq_api_key,
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
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
    st.session_state.groq_chat_history.append({"role": "user", "content": question})
    st.session_state.groq_chat_history.append({"role": "assistant", "content": completion})
