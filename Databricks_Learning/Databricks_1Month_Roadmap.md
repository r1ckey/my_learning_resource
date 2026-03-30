# Databricks 1ヶ月集中学習ロードマップ

**目標**: 1ヶ月以内で実務レベルのLakehouse構築スキル習得 ＆ Data Engineer Associate 試験合格レベルへ
**現在のスキル**: Python（通常レベル）、Spark SQL（少し）、Delta/UC/MLflow（未経験）
**環境**: Databricks Community Edition（無料枠）※一部機能制限あり

> [!WARNING]
> **Community Editionの制限事項**
> Community Editionでは、**Unity Catalog、Delta Live Tables (DLT)、Databricks SQLのレイクハウス（SQLウェアハウス）、高度なWorkflows（Jobs）** は利用できません。
> これらの機能（特に認定試験で最重要のUnity CatalogとDLT）については「公式ドキュメント・座学＋Geminiでの概念理解」を中心に進めるか、可能であれば実務環境やAzure/AWS上での14日間無料トライアル（クラウド側の従量課金は発生）の利用を検討してください。

---

## 🗺️ 1ヶ月の学習スケジュール目安（週10〜15時間想定）

初心者が迷わないよう、優先度順（基礎→データエンジニアリング→ガバナンス/AI）に構成しています。

| 週 | 優先度 | メイントピック | 学習の目的 | 所要時間 | 進捗チェックポイント |
|:---|:---|:---|:---|:---|:---|
| **第1週** | 高 | **環境構築 ＆ Delta Lakeの基礎** | レイクハウス・アーキテクチャの理解とDelta形式でのデータ操作 | 約12時間 | Community EditionでDeltaテーブルを作成し、Time TravelやUPDATEを実行できる |
| **第2週** | 高 | **PySparkとSpark SQLによるETL** | 実務で不可欠なデータ加工・再利用可能なパイプライン処理の習得 | 約15時間 | Python/PySparkを用いて、CSV等の生データをクレンジングし集計できる |
| **第3週** | 高〜中 | **メダリオンアーキテクチャ & 増分処理** | Bronze→Silver→Goldのパイプライン設計とAuto Loader基礎 | 約12時間 | 複数ノートブックを連携させ、擬似的なメダリオン構造のデータを構築できる |
| **第4週** | 中 | **Unity Catalog, MLflow, 生成AI機能** | データガバナンスと最新AI機能のキャッチアップ、試験対策 | 約12時間 | UCの3層構造を説明でき、MLflowでモデルを記録するコードが書ける |

---

## 🛠️ 週別アクションプラン＆ハンズオン課題

### 第1週：LakehouseとDelta Lakeの基礎
まずはDatabricksの根幹である「Delta Lake」の強力な機能を体験します。

*   **具体的な学習トピック**:
    *   Databricks Community Editionの登録とクラスター起動
    *   データレイクとデータウェアハウスの違い、レイクハウスの概念
    *   Delta Lakeの基本動作 (ACIDトランザクション、Time Travel、Z-Order、Optimize)
*   **推奨公式ドキュメント**:
    *   [Databricks チュートリアル: 初めてのDelta Lake](https://docs.databricks.com/ja/delta/tutorial.html)
*   **Geminiに聞くべき質問例**:
    *   「Delta LakeとParquetの具体的な違いを初心者向けに例え話で教えて」
    *   「VACUUMコマンドのリテンション期間（デフォルト7日）の理由と、実務での注意点は？」
*   **ハンズオン課題**:
    ```python
    # 1. サンプルデータの読み込みとDelta形式での保存
    df = spark.read.csv("/databricks-datasets/flights/", header=True, inferSchema=True)
    df.write.format("delta").mode("overwrite").saveAsTable("flights_delta")

    # 2. Time Travelの確認（履歴・バージョンの確認）
    spark.sql("DESCRIBE HISTORY flights_delta").show(truncate=False)

    # 3. データの更新 (データレイクなのにUPDATEができる体験)
    spark.sql("UPDATE flights_delta SET delay = 0 WHERE delay IS NULL")
    
    # 4. 古いバージョンへの復元（Time Travel）
    # df_v0 = spark.read.format("delta").option("versionAsOf", 0).table("flights_delta")
    ```

### 第2週：PySparkとSpark SQLの実践ETL
Pythonの基礎知識を活かして、PySpark DataFrame APIでのデータ変換をマスターします。

*   **具体的な学習トピック**:
    *   PySpark DataFrame API (Select, Filter, GroupBy, Join, Window関数)
    *   Spark SQLとPySparkの使い分け・混在テクニック
    *   UDF (ユーザー定義関数) のパフォーマンスへの影響とPandas UDF
*   **推奨公式ドキュメント**:
    *   [PySpark DataFrame チュートリアル](https://spark.apache.org/docs/latest/api/python/getting_started/quickstart_df.html)
*   **Geminiに聞くべき質問例**:
    *   「以下のSQLクエリを同等のPySpark DataFrame APIのコードに書き換えて： `SELECT dest, avg(delay) FROM table WHERE origin = 'JFK' GROUP BY dest`」
    *   「PySparkでSpark SQLのサブクエリと同じことをするにはどうすればいい？」
*   **ハンズオン課題**:
    ```python
    from pyspark.sql.functions import col, avg, desc
    
    # 1. 欠損値の処理とデータ型の変換
    cleaned_df = spark.table("flights_delta").dropna(subset=["destination"])
    
    # 2. GroupByと集計・ソート (DataFrame API)
    summary_df = cleaned_df.groupBy("destination") \
        .agg(avg("delay").alias("avg_delay")) \
        .filter(col("avg_delay") > 15) \
        .orderBy(desc("avg_delay"))
    
    # 3. Silver層のテーブルとして保存
    summary_df.write.format("delta").mode("overwrite").saveAsTable("flights_silver")
    ```

### 第3週：メダリオンアーキテクチャと増分処理
実務でのETLパイプライン設計のデファクトスタンダードを学びます。

*   **具体的な学習トピック**:
    *   メダリオンアーキテクチャ (Bronze / Silver / Gold の役割)
    *   Auto Loader (`cloudFiles`) による効率的な増分データの取り込み（試験用・知識として）
    *   Delta Live Tables (DLT) の基本構文と概念（試験にも頻出）
*   **推奨公式ドキュメント**:
    *   [メダリオンアーキテクチャとは](https://www.databricks.com/jp/glossary/medallion-architecture)
    *   [Auto Loader とは何か](https://docs.databricks.com/ja/ingestion/auto-loader/index.html)
*   **Geminiに聞くべき質問例**:
    *   「Auto Loaderを使うメリットを、通常の `spark.read.stream` と比較して教えて」
    *   「Data Engineer Associate試験対策として、Delta Live Tables (DLT) でよく出るキーワードや制約事項を5つ教えて」
*   **ハンズオン課題**（バッチ処理によるメダリオン構造のシミュレーション）:
    ```python
    # Bronze処理 (生データの取り込み - 履歴を全て保持)
    df_raw = spark.read.json("/databricks-datasets/structured-streaming/events/")
    df_raw.write.format("delta").mode("append").saveAsTable("bronze_events")

    # Silver処理 (フィルタリングとクレンジング - 分析可能な形に)
    df_silver = spark.table("bronze_events").filter(col("action") == "Open").dropDuplicates(["id"])
    df_silver.write.format("delta").mode("overwrite").saveAsTable("silver_events")

    # Gold処理 (ビジネスサマリー - BIやダッシュボード向け)
    df_gold = spark.table("silver_events").groupBy("deviceType").count()
    df_gold.write.format("delta").mode("overwrite").saveAsTable("gold_device_summary")
    ```

### 第4週：Unity Catalog, MLflow, 生成AI (Mosaic AI) と試験対策
モダンなデータ基盤に不可欠なガバナンスと、AI連携の基礎を押さえます。

*   **具体的な学習トピック**:
    *   Unity Catalogによる3層名前空間 (メタストア -> カタログ -> スキーマ -> テーブル)
    *   アクセスコントロール戦略 (GRANT / REVOKE)
    *   MLflowによるエクスペリメントトラッキング（Community EditionでもUIタブから確認可）
    *   Databricks Mosaic AI (AI関数・Genie等の概念)
*   **推奨公式ドキュメント**:
    *   [Unity Catalog の概要](https://docs.databricks.com/ja/data-governance/unity-catalog/index.html)
*   **Geminiに聞くべき質問例**:
    *   「Unity Catalogの『外部ロケーション (External Location)』と『マネージドテーブル』の違いを、図解するように分かりやすく説明して」
    *   「Databricks Data Engineer Associate試験の模擬問題を3問作成して」
*   **ハンズオン課題**（MLflowのトラッキング体験）:
    ```python
    import mlflow

    # MLflowを使ったパラメータとメトリクスのトラッキング
    # 注: Community Editionでは画面右上の "Experiment" アイコンから結果を確認できます
    with mlflow.start_run(run_name="My First MLflow Run"):
        mlflow.log_param("data_version", "v1.0")
        mlflow.log_metric("row_count", spark.table("gold_device_summary").count())
        
        # 実際の運用ではここで機械学習モデルを学習させ、mlflow.spark.log_model() 等で保存します
        print("Logged metadata to MLflow!")
    ```

---

## 🤖 [超重要] 強力なAIアシスタントの使い分け戦略

実務スピードを最速にするには、2つのAIの「使い分け」が鍵です。

### 1. Databricks Assistant (ワークスペース内蔵AI)
**【役割】** コーディングの相棒、ローカルデバッガー、コードジェネレーター
*   **得意なこと**：ノートブック内のコンテキスト（今読み込んでいるDataFrameのスキーマ名など）を把握した上でのコード生成。
*   **使い方**：
    *   エラーが出たら、セルの中で `/fix` を入力して自動修正させる。
    *   セルにコメントで `# 〇〇を抽出して、Window関数で累積和を出して` と書き、`Cmd + Enter` (または自動保管) でコードを書かせる。
    *   既存の複雑なコードに `/explain` を適用し、一行ずつ解説させる。

### 2. Gemini Advanced (Gemini Web UI / Antigravity)
**【役割】** アーキテクト、メンター、試験対策コーチ
*   **得意なこと**：深い概念の説明、アーキテクチャの比較検討、エラーの背景となる知識の補完、学習プランの軌道修正。
*   **使い方**：
    *   **エラーの根本解決**：「Databricks Assistantに `/fix` を頼んでも直らないエラーがあるんだけど、設定レベルで何か間違ってる？ トレースログはこれ：...」
    *   **アーキテクチャ相談**：「来月から実務で『一晩で50GB増えるログデータ』を処理する。今の知識だとAuto Loader＋DLTが良い気がするけど、この設計の穴はある？」
    *   **試験対策**：「Data Engineer Associate向けに、Incremental Processing（増分処理）の分野の知識をクイズ形式で出題して。一つ回答するごとにフィードバックをちょうだい。」
