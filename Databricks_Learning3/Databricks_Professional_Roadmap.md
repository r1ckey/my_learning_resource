# Databricks Advanced Data Engineer & GenAI ロードマップ

「データパイプラインを作る」段階（Part 1 & 2）から、「テラバイト級のデータを絶対に止めず・安く処理する（Part 3）」「LLMを統合してAIシステム化する（Part 4）」という、Databricksアーキテクトの上位1%を目指すアドバンスド・プログラムです。

## 🏛️ Part 3: Advanced Data Engineering (Professional レベル)
**想定期間: 4週間**
データ基盤を構築した後に必ず直面する「遅い」「メモリがパンクする」「CI/CD環境へのデプロイが手作業で辛い」という実務の壁を、自力で突破できるシニアエンジニアになるための道のりです。

*   **Week 1:** 分散処理の悪夢「Data Skew（データの偏り）」の解決と、OOM（Out of Memory）・Spill回避のチューニング技法。
*   **Week 2:** 永遠に止まらないストリームアーキテクチャ。ウォーターマーク処理と、外部DBからの変更同期（CDC）。
*   **Week 3:** **[最重要]** これからのDatabricksインフラの超主役。「Databricks Asset Bundles (DABs)」を用いた宣言的パイプライン展開。
*   **Week 4:** 複雑な行・列レベルの動的アクセス制御と、クラウド破産を防ぐサーバーレス・Spotインスタンス戦略。

## 🧠 Part 4: Mosaic AI & GenAI Engineering
**想定期間: 4週間**
Databricksは単なるビッグデータ基盤から「Data Intelligence Platform」へと変貌を遂げました。このパートでは、自社のデータ（Unity Catalogのデータや機密PDF）を使って、安全に「社内専用のChatGPT（RAG）」等を構築するエンドツーエンドの技術を習得します。

*   **Week 1:** Llama 3や自社モデルを即座にAPI化する `Foundation Model API` と `Model Serving`。
*   **Week 2:** `Mosaic AI Vector Search` の内部構造と、S3のPDFデータを読み込ませるRAGアーキテクチャ完全実装。
*   **Week 3:** LLMOps。プロンプトエンジニアリングの軌跡を `MLflow` で管理し、「AIの回答をAIに評価させる」仕組み。
*   **Week 4:** データ非専門家がチャットでSQL結果を得られる `Databricks Genie` の構築と `AI Functions`。

> [!TIP]
> **🚀 シニアエンジニアへの心構え**
> ここから先の内容は、単純なツールの使い方ではなく「物理的なサーバーのメモリ設計どうなっているのか」「バージョン管理のYAMLはどう設計されるべきか」という**コンピューターサイエンス・インフラ設計の根幹**に関わってきます。「どうやって動かすのか」ではなく「内部で何が起きているから、この設定をすべきなのか」を意識して読み進めてください！
