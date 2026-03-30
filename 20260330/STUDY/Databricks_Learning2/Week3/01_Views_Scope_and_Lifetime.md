# 認定対策 Week 3①：一時ビュー（Temp View）の「スコープ」と「寿命」

データマート等の開発で誰もが当たり前に作成している「仮想のテーブル（ビュー）」。
試験領域の「Spark SQL」パートでは、**「そのビューは誰（どのノートブック）から見えて、いつ消滅するのか？」** という可用性とスコープの違いが百発百中で問われます。

以下の3種類の「短命なビュー」を完璧に切り分けてください。

## 1. 共通テーブル式 / CTE (WITH句) のスコープ

```sql
WITH regional_sales AS (
    SELECT * FROM raw_sales WHERE region = 'US'
)
SELECT SUM(amount) FROM regional_sales;
```
*   **寿命・見え方:** **その1つのSQLステートメント内だけ** で生き続けます。
*   次のセル（SQL文）で `SELECT * FROM regional_sales` と叩いても即座に「そんなテーブルはない」とエラーになります。

## 2. Temporary View (テンポラリ・ビュー) のスコープ

PySparkでは `df.createOrReplaceTempView("my_temp_view")`、SQLでは `CREATE TEMP VIEW my_temp_view` で作られる最も一般的な仮テーブルです。

*   **寿命:** **そのノートブックの「Sparkセッション」が生きている間**。つまり、ノートブックを開いてクラスターに最初につながった瞬間から、クラスターが停止（Auto-terminateなど）するか、ノートブックの接続を切断（Detach）するまでです。
*   **見え方（The Catch）:** **作った本人の「その1つのノートブック」からしか絶対に見えません。**
*   **🚨 Exam Trap**: 「別のデータサイエンティストが、同じクラスター上で全く別のノートブックを開きました。彼女はあなたの作ったTemp Viewにアクセスしてクエリを投げられるか？」
    ➡️ **[絶対の正解]: できません。** セッション（ノートブックの空間）ごとに完全にアイソレーション（隔離）されているため、共有は不可能です。

## 3. Global Temporary View (グローバル・テンポラリ・ビュー) 

前述の「Temp View」を、**「同じクラスター上で動いている別のノートブック同士で共有できるようにしたい」**（でも本物のテーブルとして保存はしたくない）というニッチな要求に応えるのが Global Temp View です。

```python
# PySparkでの作成
df.createOrReplaceGlobalTempView("shared_sales")
```

*   **寿命:** **クラスターのアプリケーションが生きている間**。つまり、クラスターがシャットダウンされるまでです。
*   **見え方（The Catch）:** 同じクラスターに接続している限り、**誰でも・どのノートブックからでも参照できます。**
    
> [!IMPORTANT]
> **🚨 Exam Trap (Global Temp View の呼び出し方構文)**
>  この機能には、試験で絶対に問われる「独特な暗記ルール」があります。
> グローバルな一時ビューは、`global_temp` という「システムが隠し持っている専用の仮想データベース（スキーマ）」の中に強制保存されます。
> 
> そのため、「さっき私が作った `shared_sales` からデータをSELECTして」と問題文で書かれている場合、呼び出し方は以下のどれが正しいでしょうか？
> 
> *   ❌ `SELECT * FROM shared_sales`
> *   ❌ `SELECT * FROM global.shared_sales`
> *   ⭕️ **`SELECT * FROM global_temp.shared_sales`**
> 
> このように、必ず頭に **`global_temp.`** を付けてアクセスしなければならないルールがあります。このキーワードを見つけたらノータイムでチェックを入れてください。
