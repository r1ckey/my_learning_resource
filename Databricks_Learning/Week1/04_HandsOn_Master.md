# 第1週④：週次ハンズオン・マスターコード

今週の資料（アーキテクチャ、スキーマ管理、パフォーマンス最適化）で学んだ概念を、**約30分で一気に全て体感できるPython & SQLのハイブリッドコード**です。文章で読んだものを実際に動かして「体感」へ落とし込んでください。
Databricks Community Editionで新規ノートブックを作成し、以下のコードを上から順番にセルへ貼り付けて実行（Shift+Enter）してください。

---

### Step 1: データの投入とDeltaテーブル化（Bronze相当）
```python
# 1. 組み込みのサンプルCSVデータセットを読み込み、Dataframeとしてメモリに展開
df = spark.read.csv("/databricks-datasets/flights/", header=True, inferSchema=True)

# 2. "delta"フォーマットを指定して上書き保存し、データレイクをLakehouseの世界へ持ち上げる
table_name = "practice_flights_delta"
df.write.format("delta").mode("overwrite").saveAsTable(table_name)

print("✅ Data successfully loaded into Delta Lake!")
```

### Step 2: DWHライクなACID操作 (UPDATE / DELETE) の体感
```sql
%sql
-- ノートブックで %sql を使うと、そのセルは純粋なSQLセルに切り替わります
-- 1. まず現在の「遅延(delay)がNULL」の状況（更新前）を確認します
SELECT delay, count(*) as count FROM practice_flights_delta GROUP BY delay ORDER BY delay ASC LIMIT 5;

-- 2. ★トランザクション処理：遅延がNULLのものをすべて "0" に一括更新（S3上のログ更新）
UPDATE practice_flights_delta SET delay = 0 WHERE delay IS NULL;

-- 3. ★データクレンジングとして、originが特定の空港('ORD')のレコードを削除
DELETE FROM practice_flights_delta WHERE origin = 'ORD';
```

### Step 3: タイムトラベルと、誤操作からの劇的ロールバック
```sql
%sql
-- 1. ここまでの基盤操作履歴を確認。先ほどのUPDATEやDELETEがどのようにロギング(_delta_log)されているか見ます。
DESCRIBE HISTORY practice_flights_delta;

-- 2. 失敗した！やっぱり先程のDELETEを取り消したい！ -> 「RESTORE」コマンドで初期バージョン（version 0）にロールバックします。
-- （※ 出力された履歴の一番古いversionが0であることを前提としています）
RESTORE TABLE practice_flights_delta TO VERSION AS OF 0;

-- 確認: 削除されたはずの 'ORD' 空港のレコードが復活しているはずです
SELECT count(*) FROM practice_flights_delta WHERE origin = 'ORD';
```

### Step 4: スキーマエボリューション（進化）の実践
```python
# 1. 本番環境で「いきなり上流システムから全く知らない『system_info』などのカラムが増えたデータが送られてきた」と仮定します。
df_new_schema = spark.sql("SELECT *, 'System_A' as source_system FROM practice_flights_delta LIMIT 10")

# 2. そのまま mode("append") すると通常はエラーになりますが、 option("mergeSchema", "true") を付けることで、基盤側が柔軟にテーブル定義を受け入れて拡張します。
df_new_schema.write.format("delta").mode("append").option("mergeSchema", "true").saveAsTable("practice_flights_delta")

# 確認：最後に「source_system」カラムが空値（NULL）あるいは値ありで追加構成されているのを確認
display(spark.sql("SELECT * FROM practice_flights_delta LIMIT 5"))
```

### Step 5: ファイルの一本化と検索の高速化チューニング (OPTIMIZE & ZORDER)
```sql
%sql
-- 実務で頻繁に検索される "destination" (目的地) と "origin" (出発地) をキーとして指定し、ファイルを多次元ソート・再編成(コンパクション)する
OPTIMIZE practice_flights_delta ZORDER BY (destination, origin);

-- 最後にVACUUMでゴミ掃除
-- （※DRY RUNオプションは：実際には消さず、対象となる古ぼけたファイルのリストだけ表示する「安全モード」です）
VACUUM practice_flights_delta RETAIN 0 HOURS DRY RUN;
-- ※セーフティガード設定により、0時間の即時VACUUMはエラーになることがあります。実務では通常実行コマンド "VACUUM practice_flights_delta;" (デフォルト7日残しで掃除) をスケジューリングします。
```

> [!TIP]
> 上記のコードを動かしながら、「ああ、ここを実行した瞬間、裏では新しいParquetファイルと、JSONの_delta_logが書かれたんだな」「OPTIMIZEが走って小さなゴミファイルが一つに固められたんだな」と視覚的に思い描きながら実行できるようになれば、あなたはすでに**優れたデータエンジニアとしての解像度**を獲得しています！
