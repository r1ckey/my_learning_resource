# 第4週③：Mosaic AIと「Data Intelligence Platform」への進化

Databricksは現在、「単なるLakehouse」にとどまらず、基盤全体に生成AIやLLM（大規模言語モデル）の知能を統合させた「**Data Intelligence Platform**」へと進化しています。（これは、MosaicMLという世界トップクラスの生成AI企業を買収したことで劇的に加速しました）。

ここでは、最新のDatabricksエコシステムにおける「3つの生成AI機能」と、実務での活用法を解説します。

---

## 1. AI Functions (SQL組み込みのAI関数)
データアナリストが100万行の顧客レビュー（テキスト）を分析したい時、これまではPythonで自然言語処理ライブラリを組み込み、重い処理を書く必要がありました。
**AI Functions** を使うと、普通のSQLクエリの中に直接「LLM（言語モデル）に指示を出す関数」を書き込み、表データ全体に対して一括でAI処理を実行させることができます。

```sql
-- テーブル内の「review_text（顧客の生の声）」カラムをLLMに読ませて、
-- それがポジティブかネガティブか、あるいは特定の課題かを一瞬で判定させる！
SELECT 
    customer_id,
    review_text,
    ai_analyze_sentiment(review_text) AS sentiment,
    ai_generate_text(
        "以下のレビューから、最も不満に思っている箇所を10文字以内で抽出して: " || review_text
    ) AS problem_summary
FROM gold_customer_reviews;
```
> [!TIP]
> **実務での破壊力**
> コールセンターの通話録音の文字起こしデータなどを、パイプライン（Silver層 -> Gold層）の途中でAI Functionsを通すだけで、**「不満カテゴリ分類」や「要約」といった高度なAI処理済みのGoldテーブル**が、SQLエンジニア単独で数十分で構築できてしまいます。

## 2. Mosaic AI Vector Search (ベクトル検索) と RAG
企業内で「社内規程PDFや過去のトラブル報告書を読み込ませた、社内専用のChatGPT（RAGシステム）」を作る機運が高まっています。しかし通常、ベクトルデータベース（Pinecone等）を外部に別途契約して連携させるのは、セキュリティ審査や運用コストの壁がありました。

Databricksには **Mosaic AI Vector Search** という「Unity Catalog上に存在するフルマネージドのベクトルDB」が内蔵されています。
*   **特徴:** Unity Catalog上のDeltaテーブルと同期し、PDFテキストなどを自動的にベクトル化（埋め込み）して一元管理します。
*   **実務の強み:** データが自社のLakehouse基盤（VPC等）から外部へ一切漏れないため、機密情報を扱う社内RAGの構築に最適です。「Models in UC」で管理されている自社製の埋め込みモデル等を使うことも可能です。

## 3. Databricks Genie（データ非専門家向けの自然言語BI）
これまでは、どんなに完璧なGold層を作っても、ビジネス側（営業担当者など）はBIツール（TableauやPowerBI）の決まったダッシュボードのグラフしか見ることができませんでした。「ちょっと違う切り口（例：先週の関東地方の特定商品の店舗別売上）が見たい」と思っても、データアナリストに依頼してSQLを書いてもらうまで数日待つ必要がありました。

**Databricks Genie** は、この溝を埋める「チャット型のエージェント」機能です。
*   営業担当者がチャット画面で「先週の関東地方の、商品Aの売上を店舗別に棒グラフで出して」と自然言語（日本語・英語）で打ち込みます。
*   Genieエージェントが、Unity Catalogに登録されているメタデータ（テーブルとカラムの意味）を理解し、**自律的にSQLを生成して基盤にクエリを投げ、結果の表やグラフを数秒で返します。**

> [!IMPORTANT]
> **アーキテクトとしての総括**
> Databricksが目指す究極の世界は、
> 「エンジニアがAuto LoaderとDLTで**堅牢なパイプライン(SSOT)**を作り」
> 「Unity Catalogで**誰もが使えるように安全にカタログ化**し」
> 「ビジネスサイドがGenieやAI Functionsで**自由にデータを引き出して価値に変える**」
> という、エコシステム全体の民主化です。ここまで設計できれば、あなたは真のDatabricksアーキテクトです！
