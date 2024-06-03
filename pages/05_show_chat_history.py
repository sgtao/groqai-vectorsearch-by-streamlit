# show_chat_history.py
import json
import streamlit as st

st.title("💬 Show Chat History")
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
  
# チャット履歴の初期化／表示
with st.sidebar:
    uploaded_file = st.file_uploader("Choose a JSON file", type="json")
    if uploaded_file is not None:
        st.session_state.shown_chat_history = load_chat_history(uploaded_file)

if st.button("Show Chat History ?"):
    show_chat_history()

if question := st.chat_input("Say something"):
    show_chat_history()
    # ユーザーのメッセージを表示
    with st.chat_message("user"):
        st.markdown(question)

    # completionメッセージを生成
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
    st.session_state.shown_chat_history.append({"role": "user", "content": question})
    st.session_state.shown_chat_history.append({"role": "assistant", "content": completion})

