# 認定対策 Week 4①：Auto Loader（cloudFiles）とレスキューカラム

クラウドに届き続ける生データを「増分」だけで取り込むストリーミング機能「Auto Loader」。
試験ではその超強力な**「スキーマ変更への耐性（エラーを出さずにゴミデータを隔離する機能）」**の設定（オプション引数）が問われます。

## 1. cloudFiles の基本フォーマット暗記
「Data Engineerが、S3ディレクトリから新しく追加されるJSONファイルだけを増分処理で読み込みたい。どのSpark `format` を呼び出すべきか？」
*   ❌ `format("streaming")` 
*   ❌ `format("json")` (これはただの1回限りのバッチ読み込みになってしまいます)
*   ⭕️ **`format("cloudFiles")`** (これが Auto Loader の起動呪文です)

## 2. schemaLocation による「成長の記憶」

Auto Loaderは、最初のファイルから列の情報（スキーマ）を推論してくれます。しかし、将来列が増えたり減ったりした時のために、その「スキーマの履歴」をどこかのフォルダにファイルとして退避・保存しておく必要があります。

```python
# 試験で絶対に入れないと動かないと言われるオプション
df = spark.readStream.format("cloudFiles") \
  .option("cloudFiles.format", "json") \
  .option("cloudFiles.schemaLocation", "/path/to/schema_storage_dir") \
  .load("/path/to/raw/data")
```
> [!IMPORTANT]
> **🚨 Exam Focus (`schemaLocation` の役割)**
> なぜ `cloudFiles.schemaLocation` を必ず指定しなければならないのでしょうか？
> **[絶対の正解]**: 後から「新しい未知のカラム」が追加されたJSONが届いた時に、Auto Loaderが過去のスキーマ設定と照らし合わせて**「どうスキーマエボリューション（進化）させるか」を自動判断するため**です。

## 3. レスキューカラム（_rescued_data）の巨大な罠

実務で、ある日突然、上流のシステムがバグって「Age（年齢）」のINT型のカラムに、間違えて「"Twenty"」という文字列（String型）を送信してきたとします。
通常のETLパイプラインはここで「型が違う！」とパニックになり（AnalysisException）、データ基盤全体が停止します。

Auto Loaderは、この最悪の事態を防ぐ **レスキュー機能 (Rescued Data Column)** を備えています。

*   **動作**: 型が合わなかったり、不正なJSONフォーマットだったデータ（ゴミ）を**エラーにして止めるのではなく、そのまま `_rescued_data` という特殊な文字列カラムの中に一旦格納し、その他の正常なカラムのデータだけは通常通り取り込み続ける** という挙動です。

> [!WARNING]
> **🚨 Exam Trap (レスキューカラムのデフォルト挙動)**
> 試験で問われるのは、「この `_rescued_data` カラムを使うためにはどれだけ複雑なオプション指定が必要か？」という問題です。
> 
> *   ❌ `.option("cloudFiles.schemaEvolutionMode", "rescue")` を付ける
> *   ❌ `.option("rescueData", "true")` を付ける
> *   ⭕️ **何も指定しなくても、Auto Loaderを使えばデフォルトで自動的に `_rescued_data` に隔離されます**。
>   
> つまり、「Data Engineerが、予期せず型が変わったカラムのデータを見捨てず（破棄せず）に特定のカラムに退避させたい場合、追加で設定しなければならないオプションは何か？」と聞かれたら、答えは「追加オプションは何もいらない（デフォルト機能である）」です。
