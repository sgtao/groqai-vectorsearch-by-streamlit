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
- 別途、[semantic-trans-search](https://github.com/sgtao/semantic-trans-search.git
)プロジェクトを起動する
- その後、`streamlit`でアプリを起動する
```sh
poetry shell
streamlit run main.py
```

## LICENSE
- Apache-2.0 license
