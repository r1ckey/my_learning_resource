# Deep Dive Week 4②：SQLの壁を突破する黒魔術「dbtとJinja (メタ・プログラミング)」

「SQL（Structured Query Language）」は、データの集計のための素晴らしい言語です。しかし、ソフトウェア・エンジニアリングの観点から見ると**「圧倒的にプログラム言語としての機能（For・If・関数の再利用などの概念）」が欠落しています**。

dbt (data build tool) の最も変態的（最強）な機能である**「Jinja (ジンジャ) テンプレートによるSQLのメタ・プログラミング（マクロとループ）」**こそが、世界中のデータエンジニアを虜にしている理由です。

## 1. For文がないSQLの苦悩（100列の地獄）

データソースから「支払い方法（Cash, Credit, PayPay, Bitcoin, ...）」ごとに別々のカラム（列）に分かれている、横にとても長い（ワイドテーブル）な `raw_payments` テーブルが来たとします。
「Cashの売上」「Creditの売上」...これを、1つずつのカラムの合計値として、きれいに縦に並べたい（Pivotさせたい）。

*   **【普通のSQLエンジニアの苦行】**:
    ```sql
    SELECT
      user_id,
      SUM(CASE WHEN payment_method = 'Cash' THEN amount END) AS cash_amount,
      SUM(CASE WHEN payment_method = 'Credit' THEN amount END) AS credit_amount,
      SUM(CASE WHEN payment_method = 'PayPay' THEN amount END) AS paypay_amount,
      -- ... これをもし支払い方法が50種類あったら、50行コピペ（ハードコーディング）で手書きするか…死ぬ…
    FROM raw_payments
    GROUP BY user_id
    ```

## 2. 解決策：dbt (Jinja) による「Forループ」の黒魔術

dbtは内部にPython由来の Jinja (ジンジャ) というテンプレートエンジンを内包しています。
これにより、**「SQLファイルの中に、For文（ループ処理）を埋め込む（メタ・プログラミング）」**ことができます。

*   **【アーキテクト（dbtマスタ）が書くスマートなコード】**:
    ```sql
    -- Jinaを使った dbt SQLファイル
    
    {% set payment_methods = ['Cash', 'Credit', 'PayPay', 'Bitcoin', 'ApplePay'] %}
    
    SELECT
      user_id,
      
      -- Jinja の For ループで、SQL文字列を自動的に何度も展開（生成）させる！
      {% for method in payment_methods %}
      SUM(CASE WHEN payment_method = '{{ method }}' THEN amount END) AS {{ method | lower }}_amount
      
      -- 最後の要素以外はコンマ(,)をくっつける魔法（If文による制御）
      {% if not loop.last %},{% endif %}
      {% endfor %}
      
    FROM {{ ref('raw_payments') }}
    GROUP BY user_id
    ```

**🌟 このマジックの挙動（コンパイル）**
あなたが `dbt run` などの実行コマンドを叩く直前、dbtは裏側で**「For文の中身を高速で文字列として展開（コピペ自動生成）」**し、データベースが理解できる『完全で長大な、非常に美しい1本のSQL』へとコンパイル（翻訳・出力）してからデータベースに送信します。

## 3. 再利用の極致「dbt マクロ (Macro)」

ソフトウェア開発では「日本時間をUTC時間に直す」などの共通処理は、一度 `function convert_timezone()` のような関数を作って、全プロジェクトで使い回します（DRY原則：Don't Repeat Yourself）。
しかし、旧来のSQLではこれができず、全SQLに同じような長いキャスト関数や文字列処理のロジックがコピペされて散らかっていました。

dbtでは、これを **`Macro (マクロ)`** として定義します。

```sql
-- macros/cents_to_dollars.sql の中に定義
{% macro cents_to_dollars(column_name, scale=2) %}
    ({{ column_name }} / 100)::numeric(16, {{ scale }})
{% endmacro %}
```

一度マクロを作ってしまえば、社内の全アナリストは、どんなに複雑な計算式も、以下のようにたった一行呼び出すだけで全て解決（自動展開）できます。

```sql
-- 他の全てのSQLファイルから、魔法のように呼び出せる
SELECT 
    user_id,
    {{ cents_to_dollars('payment_amount_cents') }} AS payment_amount_dollars
FROM 
    {{ ref('stg_payments') }}
```

これこそが、**「属人化したグチャグチャのSQL（長大で読めない地獄）」を撲滅し、SQLを「美しいモジュール化されたソフトウェア・コード」へと昇華させる、dbt最大のイノベーション（モジュラーSQLアーキテクチャ）**なのです！
