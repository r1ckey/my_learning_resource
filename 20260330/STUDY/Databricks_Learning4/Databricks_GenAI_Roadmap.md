# Databricks Mosaic AI / GenAI Engineering 完全攻略ロードマップ

「データ基盤」という受動的な存在から、AIが自ら思考してビジネスの答えを出す「Data Intelligence Platform」へと進化させる、GenAI（生成AI）エンジニアとしての最後のカリキュラムです。

## 🧠 Part 4: GenAI Engineering (AIシステムビルダー)
**想定期間: 4週間**
社内の機密データ（決算書のPDFや顧客データ）をOpenAIなど外部のSaaSに流出させることなく、Databricksという完全に守られた城（Unity Catalog）の中で、独自のChatGPT（RAGシステム）やAIエージェントを構築する手法を学びます。

*   **Week 1:** Databricksがホストしている「オープンソースの超高性能LLM（Llama 3やDbrx）」を、すぐに自社のアプリから呼び出す `Foundation Model API`。
*   **Week 2:** **[最重要]** 世の中で最も需要の高い「社内文書AI（RAG）」アーキテクチャ。文章のベクトル化（Embedding）と、`Mosaic AI Vector Search` を使った自動同期検索エンジンの構築。
*   **Week 3:** AI開発の泥臭い部分「LLMOps」。LangChain等の複雑な処理を `MLflow` で管理し、「AIの回答が本当に正しいか？」を別のAI・指標に点数付けさせる（LLM-as-a-Judge）評価基盤。
*   **Week 4:** 最先端のエンタープライズAI機能。SQLがなくてもチャットでデータ分析ができる `Genie` と、データパイプラインの中にAI機能を埋め込む `AI Functions` (`ai_gen` 等)。

> [!TIP]
> **🚀 AIアーキテクトとしての心構え**
> ここからは「正しい・間違っている」だけではなく、「AIが幻覚（ハルシネーション）を起こしにくいパイプラインをどう設計するか？」「ユーザーの曖昧な質問にどう安全に回答させるか？」という、確率論を制御する全く新しい次元への挑戦になります。
