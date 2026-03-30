# Part 4 Week 4①：AIとSQLの融合「AI Functions」

「AIが使えるのはPython（LangChain）を書けるデータサイエンティストだけ」という時代は終わりました。

もし社内に「Pythonは一切書けないが、SQLなら呼吸するように書ける凄腕のデータアナリスト」がいるとします。彼らに巨大な「Amazonのカスタマーレビュー数千万件の生テキスト」を渡し、「これを全部日本語に翻訳して、ポジティブかネガティブか感情分析を付けて」と依頼したら、どうやって解くでしょうか？

**Databricksの「AI Functions (SQL向けAI関数)」** を使えば、アナリストが慣れ親しんだ普通の `SELECT` 文の中に、直接LLM（生成AI）の能力を埋め込むことができます。

## 1. 組み込みのAI関数群

Databricksには、よくあるAIタスク向けに「最初からSQL関数として用意されている魔法の関数」が存在します。これらは裏側で、Databricksがホストしている強力な基盤モデルが自動で動いて処理します。

*   **`ai_analyze_sentiment()`**: 感情分析 (Positive / Negative / Neutral)
*   **`ai_extract()`**: 長文のテキストから、特定の単語（会社名、製品名、人名など）をピンポイントで抽出する
*   **`ai_translate()`**: 多言語の翻訳
*   **`ai_mask()`**: クレジットカード番号やマイナンバーなどを検知して自動で `***` に伏せ字化する

### 🎯 アナリストの最強SQL
```sql
-- カスタマーレビューテーブルから、商品名と感情（Positive/Negative等）をAIに判定させて抽出！
SELECT
    review_id,
    review_text,
    ai_extract(review_text, ARRAY("product_name")) AS extracted_product,
    ai_analyze_sentiment(review_text) AS emotion_score
FROM
    raw_customer_reviews;
```
※このように通常のSQLとして実行するだけで数百万件のテキストデータがLLMに並列で送られ、感情スコアのついたキレイな構造化テーブル（Delta Table）になって返ってきます。

## 2. 万能関数 `ai_gen()` / `ai_query()` の暴暴力

もし「翻訳」や「感情分析」といった既製の関数枠に収まらない、「完全に独自の自由な指示」をLLMに出したい場合はどうするのでしょうか？
そのために用意されているのが、**ユーザーが自作のプロンプトをそのまま叩き込める汎用API関数 `ai_gen()` と `ai_query()` です。**

```sql
-- SQLの列ごとに、完全に自由なRAGやプロンプト生成をLLMにやらせる
SELECT
    product_name,
    customer_age,
    ai_gen(
        CONCAT('あなたは敏腕の営業マンです。この ', product_name, ' という商品を、', customer_age, '歳の顧客が絶対買いたくなるような短いキャッチコピーを考えてください。')
    ) AS marketing_copy
FROM
    target_customers_table;
```

> [!WARNING]
> **💰 注意事項：コンピュートの罠**
> 非常に強力で便利なこれらのSQL関数群ですが、「何百万行」もあるテーブルに対して `ai_gen()` 等を何も考えずに `SELECT` して実行してしまうと、**数百万回LLMにAPIリクエスト（推論）を投げることになり、クラウド課金額が一瞬で急騰する** リスクがあります。
> 利用の際は、必ず 事前に `LIMIT` をかけたり、`WHERE` 句で「新しい差分データだけ」に絞るなどの配慮を忘れないでください。
