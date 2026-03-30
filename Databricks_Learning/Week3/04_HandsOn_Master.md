# 第3週④：週次ハンズオン・マスターコード (ストリーミング＆メダリオン編)

今週学んだメダリオンアーキテクチャ（Bronze -> Silver -> Gold）の全体像と、「Auto Loaderによるストリーミング処理（Trigger availableNowの強さ）」を、約30分で一気に構築・体感できるPySparkのマスターコードです。

ノートブックをひとつ用意し、以下の3ステップを順に実行してください。（※ 実際のDLTの構文はCommunity Editionで実行制限があるため、ここでは同等の効果を持つPySparkの**構造化ストリーミング（Structured Streaming）**を用いて再現します。）

---

### 事前準備：ダミーのファイル（生データ）を置く疑似S3の作成
```python
# 1. 疑似的なクラウドストレージの着信フォルダ（Landing Zone）をDBFS上に作成
landing_zone = "/tmp/learning_week3/landing/"
dbutils.fs.rm(landing_zone, True) # 初期化
dbutils.fs.mkdirs(landing_zone)

# 2. ダミーのJSONファイルを到着させます
dbutils.fs.put(landing_zone + "file1.json", '{"id": 1, "action": "click", "user_id": 100}', True)
dbutils.fs.put(landing_zone + "file2.json", '{"id": 2, "action": "login", "user_id": 101}', True)

print("✅ Landing Zone (S3相当) に新しいJSONファイルが2つ到着しました！")
```

---

### Step 1: 【Bronze層】Auto Loaderによる生データのストリーミング取り込み
```python
# Auto Loader (cloudFiles) を使って、指定フォルダに「新しく到着したファイル」だけを追跡して取得
bronze_df = spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", "/tmp/learning_week3/schema/bronze/") \
    .load(landing_zone)

# 取得した生データを、加工せずに「Bronzeテーブル」へ書き込む
# ★重要: trigger(availableNow=True) により、「今溜まっている未処理分」だけを処理してピタッと終了する（バッチ処理として機能）
checkpoint_path_bronze = "/tmp/learning_week3/checkpoints/bronze/"

query_bronze = bronze_df.writeStream.format("delta") \
    .option("checkpointLocation", checkpoint_path_bronze) \
    .trigger(availableNow=True) \
    .toTable("bronze_user_events")

query_bronze.awaitTermination() # 処理の完走を待つ

print("🥉 Bronze Table created! 生データが履歴として保存されました。")
display(spark.table("bronze_user_events"))
```

---

### Step 2: 【Silver層】クリーンな共有データ (SSOT) への変換
Bronzeに変更（新しいレコード）があった場合のみ、それを読み込んでフィルタリング処理（クレンジング）を行います。今回は「IDが1のデータは不正なので削除する」という疑似ルール(DLTのDrop Row相当)を実装します。

```python
import pyspark.sql.functions as F

# Bronzeテーブルの更新分をストリームとして読み込む (これも増分処理)
stream_bronze = spark.readStream.format("delta").table("bronze_user_events")

# クレンジング処理 (ID=1を除外 = 不正パケットのフィルタリング)
silver_df = stream_bronze.filter(F.col("id") != 1)

# Silverテーブルとして出力
checkpoint_path_silver = "/tmp/learning_week3/checkpoints/silver/"

query_silver = silver_df.writeStream.format("delta") \
    .option("checkpointLocation", checkpoint_path_silver) \
    .trigger(availableNow=True) \
    .toTable("silver_user_events")

query_silver.awaitTermination()

print("🥈 Silver Table created! (クレンジング完了・分析可能な美しいデータ)")
display(spark.table("silver_user_events"))
```

---

### Step 3: 【Gold層】ビジネス用の高度な集計結果の作成
Gold層への更新は、ストリーミングで行うかバッチ(全件書き換え)で行うかは要件次第ですが、基本的にはダッシュボードが見に来るための完全切り離し・読み取り専用のバッチ集計でOKなケースが多いです。

```python
# Silver層からデータをバッチで読み込み、ビジネス要件（Actionごとの回数集計）を行う
gold_df = spark.table("silver_user_events") \
               .groupBy("action").count()

# 重い集計結果を計算し終えた状態で、Goldテーブルへ上書き（上流からの再作成）保存
gold_df.write.format("delta").mode("overwrite").saveAsTable("gold_action_summary")

print("🥇 Gold Table created! (ダッシュボード表示用の爆速集計テーブル)")
display(spark.table("gold_action_summary"))
```

> [!TIP]
> **追加ハンズオン（Auto Loaderの破壊力を知る）**
> 1. 上記のStep3まで完了したら、もう一度一番上の「事前準備のセル」に行き、新しいファイル (`file3.json`) だけをLanding Zoneに投下（追加でput）してみてください。
> 2. その後、Step 1〜3 をもう一度実行させます。
> 3. ブロンズ・シルバーのストリーミングは「file1, file2」はすでに処理済み(Checkpointに記載済み)であることを知っているため、完全に無視し、**数百万ファイルの海の中から「新しく置かれたfile3」だけの数バイト分を極少リソースでスキャンして追記します**。これを体感できたとき、ストリーミング増分処理の本当の価値が理解できるはずです。
