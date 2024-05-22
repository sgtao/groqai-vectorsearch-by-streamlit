# echo_chatbot_page.py
import os
import streamlit as st

st.title("💬 Echo Chatbot")
st.write(
    "This page is a chatbot interface without LLM. This page responses the ECHO of the user message..."
)

# チャット履歴の初期化／表示
if "temporal_chat_history" not in st.session_state:
    st.session_state.temporal_chat_history = []
else:
    for message in st.session_state.temporal_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# チャットボットのサンプルコード
with st.chat_message("assistant"):
    st.write("Hello!! Say something from input")


if question := st.chat_input("Say something"):

    # ユーザーのメッセージを表示
    with st.chat_message("user"):
        st.markdown(question)

    # completionメッセージを生成
    # chat_completion = client.chat.completions.create(
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": question,
    #         }
    #     ],
    #     model="llama3-8b-8192",
    # )
    # print(chat_completion.choices[0].message.content)

    completion = question

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
    st.session_state.temporal_chat_history.append({"role": "user", "content": question})
    st.session_state.temporal_chat_history.append({"role": "assistant", "content": completion})
    # print(f"chat_history: {st.session_state.temporal_chat_history}")
