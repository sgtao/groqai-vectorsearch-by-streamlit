# chatbot_page.py
import os
import streamlit as st
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)


st.set_page_config(page_title="Chatbot Page", page_icon="💬")

st.title("💬 Chatbot")
st.write("This page hosts a chatbot interface.")

# チャットボットのサンプルコード
with st.chat_message("assistant"):
    st.write("Hello!! Say something from input")

if prompt := st.chat_input("Say something"):
    st.chat_message("user").write(prompt)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="llama3-8b-8192",
    )

    # print(chat_completion.choices[0].message.content)
    completion = chat_completion.choices[0].message.content
    st.chat_message("assistant").write(f"Assistant: {completion}")
