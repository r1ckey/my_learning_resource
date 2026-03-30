# Part 4 Week 2②：実世界の「RAG」パイプライン構築手順

**RAG (Retrieval-Augmented Generation / 検索拡張生成)** は、単なるバズワードではなく、「自社の機密情報を、ChatGPT（LLM）の脳内に安全に一時注入して答えさせる」現代AIの事実上の標準アキテクチャです。

前章の「Vector Search（ベクターDB）」とWeek 1の「Foundation Model API（モデルAPI）」を合体させて、完全なRAGシステムをDatabricks上で構築する流れを追いかけます。

## 1. RAGの4つのステップ（裏側の動き）

営業チームの人が、社内チャット画面から **「先週の新製品Xのリリースに関する社内向けFAQをまとめて」** と質問した瞬間、裏側で以下の4つのパイプラインが0.5秒で走ります。

1.  **質問のベクトル化 (Embed)**
    ユーザーの質問文字列を、`bge-large-en` 等のEmbeddingモデルAPIに投げて「数字の配列」に変換します。
2.  **Vector DBへの検索 (Retrieve)**
    その「数字の配列」を持って、Mosaic AI Vector Searchの中を駆け巡り、「意味が一番近い上位3つの社内ドキュメントの段落（チャンク）」を引っ張り出します（※ここで「新製品XのFAQマニュアルの第2段落」などがHitします）。
3.  **プロンプトへの注入 (Augment)**
    元のユーザーの質問と、②で見つけてきた社内情報を繋ぎ合わせて、**以下のような「超巨大でズルい指示文（プロンプト）」を裏側で自動作成します。**
    > *「あなたは優秀な社内AIです。以下の【社内情報】だけを見て、ユーザーの質問に答えてください。情報がない場合は『わからない』と答えてください。
    > 【社内情報】: [RAGが見つけてきた新製品XのFAQテキスト1000文字]
    > 【ユーザーの質問】: ユーザーの質問文字列」*
4.  **LLMによる回答生成 (Generate)**
    この巨大なプロンプトを、Llama 3等のFoundation Model APIに投げ込みます。モデルは【社内情報】を見ながら回答文（日本語）を作り上げ、ユーザーに返却します。

## 2. 実装のベストプラクティス（LangChain等の活用）

上記の①〜④の流れを、ゼロからPythonの `requests` や `for文` で書くのは大変です。
そこで、この流れ（チェーン）をたった数行で表現できる **LangChain (ラングチェーン)** や **LlamaIndex** といったライブラリを利用し、Databricks上にデプロイします。

```python
# 【概念コード】LangChainによるRAGの数行実装
from langchain.vectorstores import DatabricksVectorSearch
from langchain.chat_models import ChatDatabricks
from langchain.chains import RetrievalQA

# 1. 接続先として、DatabricksのVector DB（インデックス）を指定
vector_store = DatabricksVectorSearch(index_name="catalog.schema.my_rag_index")

# 2. 賢い脳みそとして、Databricksでホストしている Dbrx モデルを指定
llm = ChatDatabricks(endpoint="databricks-dbrx-instruct")

# 3. RAGのチェーン（検索してから答える）を構築
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vector_store.as_retriever(search_kwargs={"k": 3}) # 上位3件を検索
)

# 4. 実行！
answer = rag_chain.run("先週の新製品XのFAQをまとめて")
```

> [!WARNING]
> **🚨 AI幻覚（ハルシネーション）を防ぐ要件定義**
> どれだけRAGを優秀に組んでも、「③プロンプトへの注入」のルール設定が甘いと、AIは勝手にインターネット上で学んだ無関係な知識を混ぜ合わせて嘘（ハルシネーション）の回答を作ってしまいます。
> アーキテクトとして、「絶対に渡した情報ソース（Context）以外からは回答を生成するな」「情報ソースの内容と矛盾するなら、分からないと謝れ」という強固なシステムプロンプトの設計が、RAG構築における魂（コア）となります。
