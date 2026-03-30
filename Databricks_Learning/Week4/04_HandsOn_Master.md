# 第4週④：週次ハンズオン・マスターコード (MLflowとガバナンス編)

1ヶ月のDatabricks学習の最終週です。ここでは、データエンジニアリングの「その先」にある、MLflowによるモデルの実験記録（ロギング）と、Unity Catalogの概念を疑似体験するPySparkコードを実行します。

Databricks Community Editionで新規ノートブックを作成し、以下のコードを上から順に実行（Shift+Enter）してください。これを終えれば、1ヶ月プログラムは完走です！

---

### Step 1: 機械学習用の擬似データ（Gold層の集計結果）の準備
実務において、「過去の広告費用（X）」から「来月の売上（Y）」を予測するモデルを作るための綺麗なデータセットが、すでにメダリオンアーキテクチャのGold層に存在していると仮定します。

```python
from pyspark.ml.linalg import Vectors
from pyspark.ml.regression import LinearRegression
import mlflow
import mlflow.spark

# ダミーの「広告費 vs 売上」データを作成
# (広告費(特徴量), 売上(ラベル)) の形式でベクトル化してSpark DataFrameにします
data = [
    (100.0, Vectors.dense([10.0])),  # 広告費10なら売上100
    (150.0, Vectors.dense([15.0])),  # 広告費15なら売上150
    (200.0, Vectors.dense([22.0])),  # 広告費22なら売上200
    (300.0, Vectors.dense([28.0])),
    (400.0, Vectors.dense([45.0]))
]

gold_df = spark.createDataFrame(data, ["label", "features"])
print("✅ 学習用データ (Gold層) の準備完了！")
display(gold_df)
```

### Step 2: MLflow トラッキングの魔法（自動ロギング）を体験
MLflowを使って、「単なるPythonでの機械学習モデルの訓練」から「エンタープライズレベルでのモデルとパラメータの【記録】業務」へと昇華させます。

```python
# 👉 PySpark MLlib用のオートロギング機能（これ一行でパラメータ・精度・モデル実体が全て記録される）
mlflow.pyspark.ml.autolog()

print("🚀 MLflow実験スタート...")

# 「my_first_experiment」という名前の空間に、この学習の全てを封じ込める
with mlflow.start_run(run_name="my_first_experiment"):
    
    # 1. アルゴリズム（線形回帰）の定義。ハイパーパラメータを設定（例: 正規化パラメータ = 0.1）
    lr = LinearRegression(maxIter=10, regParam=0.1, elasticNetParam=0.5)
    
    # 2. モデルの学習（Fit） ※通常はここで数時間かかったりする
    model = lr.fit(gold_df)
    
    print("🎯 学習完了！ モデルの重み・パラメータ・RMSEなどの誤差精度がMLflowへ自動送信されました。")
```

> [!TIP]
> **🚀 体感ポイント**
> 上のセルの実行が終わったら、**ノートブック画面の右上にある「フラスコアイコン（Experiment / 実験）」** をクリックして引き出してみてください！
> そこに `my_first_experiment` という行があり、クリックするとMLflowの美しいUI管理画面へ遷移します。
> スクリプト内には一切「この数値を記録して」と書いていないのに、`regParam=0.1` という設定値や、モデルそのもの（アーティファクト）が安全に保管されているのが確認できるはずです！

---

### Step 3: Unity Catalog (UC) の3層名前空間・権限付与の概念（コードリーディング）
※ *注意: Community EditionではUnity Catalogの中核機能は無効化されているため、以下のSQLはエラーになる可能性がありますが、「実務現場でアーキテクトが何を書いているか」を理解するための読み物として実行・確認してください。*

```sql
%sql
-- 1. カタログ (最上位階層) を作成（例：本番環境）
-- CREATE CATALOG IF NOT EXISTS prod_catalog;

-- 2. その中にスキーマを作成（例：マーケティング部）
-- CREATE SCHEMA IF NOT EXISTS prod_catalog.marketing;

-- 3. （仮想）作成したテーブルに対して、権限を与える（GRANT）
-- 以下のコマンドで、"data_analyst_group" に所属する全社員に、該当テーブルの「SELECT（読み取り）」権限だけを与えます
-- GRANT SELECT ON TABLE prod_catalog.marketing.gold_sales_summary TO `data_analyst_group`;

-- 4. 逆に、データサイエンティストには「モデルの作成と管理」権限を与える
-- GRANT CREATE MODEL ON SCHEMA prod_catalog.marketing TO `data_scientist_group`;
```

---
🎉 **祝！Databricks 1ヶ月プログラム完走！** 🎉

あなたは今、単に「PySparkが書ける人」ではなく、
「**なぜDelta Lakeでトランザクションが担保されるのか**」
「**なぜZ-Orderや_delta_logの仕組みがパフォーマンスを向上させるのか**」
「**なぜメダリオン構造とUCによるガバナンスが必要なのか**」
というアーキテクチャの根幹を語れる、**実務レベルのデータエンジニア／アーキテクト**へと成長しました！

実務で壁にぶつかったら、いつでもまたこの資料（Antigravity・Gemini）に戻ってきて壁打ちをしてください。お疲れ様でした！
