# groqai-vectorsearch-by-streamlit
- Groq AI APIを使ってベクタ検索付きのAI-Chatbotを作成してみる

## Setup
```sh
# after git clone
cd groqai-vectorsearch-by-streamlit
poetry install
```

## Usage
- 文章のベクトル化は別サーバで実施
  - 別に`encoding-api-using-sentence-transformers`プロジェクトを起動する
- `GROQ_API_KEY`を事前に取得する
```sh
poetry shell
export GROQ_API_KEY="GROQ_API_KEY"
streamlit run main.py
```

## LICENSE
- Apache-2.0 license
