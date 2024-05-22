# echo_chatbot_page.py
import os
import streamlit as st


st.set_page_config(page_title="Echo Chatbot", page_icon="💬")

# チャット履歴の初期化
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("💬 Echo Chatbot")
st.write(
    "This page is a chatbot interface without LLM. This page responses the ECHO of the user message..."
)

# チャットボットのサンプルコード
with st.chat_message("assistant"):
    st.write("Hello!! Say something from input")

# チャット履歴の表示
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Say something"):
    # ユーザーのメッセージを表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # completionメッセージを生成
    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt,
    #         }
    #     ],
    #     model="llama3-8b-8192",
    # )
    # print(chat_completion.choices[0].message.content)

    completion = prompt

    # エコーメッセージを表示
    with st.chat_message("assistant"):
        st.markdown(f"Assistant: {completion}")

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
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    st.session_state.chat_history.append({"role": "assistant", "content": completion})
    # print(f"chat_history: {st.session_state.chat_history}")
