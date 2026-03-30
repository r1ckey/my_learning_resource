# 第2週④：週次ハンズオン・マスターコード (PySpark実践ETL編)

今週学んだ「Sparkの最適化機構を信じること」「UDFを避け組み込み関数を活用すること」「Window関数やJSONパース」といった実学を、約30分で一気に体験できる強力なPySparkマスターコードです。

Databricks Community Editionで新規ノートブックを作成し、言語を「Python」に設定の上、以下のコードを順に実行（Shift+Enter）して、洗練されたデータエンジニアリングの世界を体感してください。

---

### Step 1: 疑似的な汚い生データ (RAW JSON) の作成
実環境でよくある、「JSONフォーマットでログが飛んでくる」状況を再現します。
```python
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import pyspark.sql.functions as F

# 意図的にネスト（入れ子）になり、かつ重複を含む汚いテストデータの作成
data = [
    (1, '{"user": "Alice", "score": 85, "device": "iOS"}', "2024-03-01 10:00"),
    (2, '{"user": "Bob", "score": null, "device": "Android"}', "2024-03-01 10:05"),
    (1, '{"user": "Alice", "score": 90, "device": "iOS_Update"}', "2024-03-02 11:00"), # Aliceの最新の更新
    (3, '{"user": "Charlie", "score": 75, "device": "Web"}', "2024-03-02 12:00")
]

columns = ["log_id", "json_payload", "updated_time"]
raw_df = spark.createDataFrame(data, columns)

print("--- 元の汚いデータ（Bronze相当） ---")
display(raw_df)
```

### Step 2: 組み込み関数を駆使したJSONのパースと展開
Pythonの標準ライブラリ(`json`)やUDF（自作関数）は決して使わず、すべてPySparkのネイティブ（JVM上で爆速に動く）関数だけで処理します。
```python
# 1. 文字列の中にあるJSONの構造（スキーマ）を定義
payload_schema = StructType([
    StructField("user", StringType(), True),
    StructField("score", IntegerType(), True),
    StructField("device", StringType(), True)
])

# 2. `from_json`関数で構造化し、`select`の中で `.*` を使って全カラムを一気にフラットに展開
parsed_df = raw_df.withColumn("parsed", F.from_json(F.col("json_payload"), payload_schema)) \
                  .select(
                      "log_id", 
                      "updated_time",
                      "parsed.*" # これで user, score, device カラムが一気に生成されます
                  ) \
                  .withColumn("updated_time", F.to_timestamp("updated_time", "yyyy-MM-dd HH:mm"))

display(parsed_df)
```

### Step 3: Window関数を用いた重複排除（最新データのみ残す）
ユーザーID (log_id) が被っているレコード（Aliceのもの）のうち、更新日時(updated_time)が最も新しいものを「真のレコード」として採用します。
```python
from pyspark.sql.window import Window

# log_idごとに区画を作り、日時が新しい順に並べる
window_spec = Window.partitionBy("log_id").orderBy(F.desc("updated_time"))

# 各区画で「1位（＝最新）」の連番を振り、1のものだけをフィルタリング
latest_df = parsed_df.withColumn("row_rank", F.row_number().over(window_spec)) \
                     .filter(F.col("row_rank") == 1) \
                     .drop("row_rank")

print("--- Aliceの古いログが消え、最新のレコードだけになることを確認 ---")
display(latest_df)
```

### Step 4: JOIN戦略と、遅延評価(Lazy Evaluation)の確認
マスタテーブル（ごく小さい）を作成し、先ほどのデータと結合(Join)します。
```python
# ごく小さいマスタデータの作成
master_data = [("iOS_Update", "Mobile"), ("Android", "Mobile"), ("Web", "Desktop")]
master_df = spark.createDataFrame(master_data, ["device_name", "category"])

# ※ ここまで全くデータそのものの計算・結合は走っていません（遅延評価）！設計図が作られているだけです。

# Broadcastのヒントをエンジンに与え、全てのノードのメモリにマスタデータをバラ撒いて最強の最適化を引き出す
final_silver_df = latest_df.join(
    F.broadcast(master_df), 
    latest_df["device"] == master_df["device_name"], 
    "left"
).drop("device_name") # 不要な重複キーを最後に削除

# 欠損値(scoreがnullなBob)にデフォルト値0を埋める
final_silver_df = final_silver_df.fillna({"score": 0, "category": "Unknown"})

print("--- 完成した綺麗なデータ（Silver相当） ---")
# 💡 display() (アクション) が呼ばれたこの瞬間に、これまでの Step 2〜4 の全ての変換設計図が
# Catalyst Optimizerによって最善の手順に並べ替えられ、一気に実行計算されます。
display(final_silver_df)
```

> [!TIP]
> 泥臭いクレンジング処理をこれだけスマートかつ宣言的に（HowではなくWhatだけを関数につなげて）記述できるのが、PySpark DataFrameの最大の魅力です。
> このノートブックコードの処理の流れ（JSON展開 -> 重複排除 -> マスタBroadcast Join -> NULL埋め）は、そのまま実務の現場のSilver層パイプラインとして即戦力で使える設計になっています！
