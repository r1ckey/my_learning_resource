# 第2週③：実務で必須となる高度なデータ変換技術

実際のETL現場では、「ただ単純にFILTERしてSELECTするだけ」の綺麗なデータパイプラインは稀です。JSONが混じった非構造化ログのパース、数億行同士の結合（Join）の最適化など、データエンジニアが息を吸うように書かなければならない3つの高度な処理について解説します。

## 1. 構造化データの中に潜む「非構造化配列（JSON列）」の展開

WebサーバーのログやAPI連携などにおいて、「1つのカラムの中に、さらに巨大なJSON文字列がそのまま放り込まれている」というケース（セミ構造化データ）が実務では多発します。
PySparkでは `from_json` と `explode` を組み合わせて、これらのJSONネストをフラットな綺麗なテーブル（Silver層データ）へと展開します。

```python
import pyspark.sql.functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# 例： 'payload' というカラムに {"user_name": "Ken", "age": 30} という文字列が入っている場合
# 1. 中身のスキーマを定義する
json_schema = StructType([
    StructField("user_name", StringType(), True),
    StructField("age", IntegerType(), True)
])

# 2. 文字列を構造化データ(Struct)にパースし、親のDataframeのカラムとして展開する
df_parsed = df.withColumn("parsed_payload", F.from_json(F.col("payload"), json_schema)) \
              .select(
                  "id",
                  "timestamp",
                  F.col("parsed_payload.user_name").alias("name"), # 中身を直接抽出
                  F.col("parsed_payload.age")
              )
```

## 2. 結合（Join）戦略とデータの偏り（Data Skew）の回避

ビッグデータにおいて、10億行のテーブル(Fact)と、別の100万行のテーブル(Dimension)を普通にJoinすると、ネットワークを介した膨大なデータのシャッフル（再配置交換）が発生し、ジョブが数時間終わらないかOOM（メモリ不足）でクラッシュします。

### 実務での判断：Broadcast Hash Join (BHJ) への強制
片方のテーブルが比較的小さい（設定の目安は10MB以内だが、実務では数百MBまで引き上げることが多い）場合、わざわざネットワーク越しに対向データをシャッフルして交換するのではなく、**「小さなテーブルを、全てのワーカーマシンのメモリ（Executor）に事前にコピー（Broadcast）してバラ撒いておき、巨大テーブルは一切動かさずに各ノード内でローカル結合させる」** というのがビッグデータ処理の定石です。

```python
# Databricks(Spark)に「department_dfは小さいから全ノードにBroadcastしろ」とヒントを与える
df_joined = huge_sales_df.join(
    F.broadcast(department_df), # ← これだけで数時間のジョブが数分で終わることがある
    "department_id",
    "left"
)
```

> [!WARNING]
> **Data Skew（データの偏り）への警戒**
> 「特定の商品（例：年末の福袋）だけが極端に売れすぎて、ログの90%が `item_id = 9999` に偏っている」といった場合、通常の手法でJoinをかけると、特定の1台のワーカーノードだけに処理が集中し、そこだけがパンクしてクラッシュします（Data Skew）。
> DatabricksのPhotonエンジンや最新のDatabricks Runtime上では、こうしたSkewを自動検知して分離する機能（AQE: Adaptive Query Execution）がデフォルトで働きますが、根本的なアーキテクチャ設計として「偏りがひどい列はJoinのキー単体にしない」などの考慮が必要です。

## 3. Window関数による強力な集計と重複排除

RDBの世界でもおなじみですが、データ内の特定のキー（例：顧客ID）ごとに区画（Window）を作り、その「区画内での順位」や「移動平均」「直前の行との差分」などを計算する機能が Window関数 です。
実務で最も使われるのが**「最新の更新レコードだけを残して重複排除（Deduplication）する」**処理です。

```python
from pyspark.sql.window import Window

# 顧客IDごとに区画を作り、更新日時(updated_at)の新しい順(desc)に並べるルールを定義
window_spec = Window.partitionBy("customer_id").orderBy(F.desc("updated_at"))

# 各区画（各顧客）の中で1位（つまり一番新しい更新レコード）のみを残す
df_latest = raw_df.withColumn("row_num", F.row_number().over(window_spec)) \
                  .filter(F.col("row_num") == 1) \
                  .drop("row_num")
```
このWindow関数による処理は、単純な `dropDuplicates` や `groupBy` では対応できない「どの行を優先して残すか」というビジネス要件に応えるための、Silver層構築における最重要テクニックです。
