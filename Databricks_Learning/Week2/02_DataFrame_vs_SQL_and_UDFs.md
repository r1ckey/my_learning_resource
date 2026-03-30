# 第2週②：DataFrame APIとSQLの実務的な使い分けとUDFの罠

このドキュメントでは、実際のETLパイプライン開発において「いつPython (DataFrame API) を使い、いつSQLを使うべきか」という設計判断基準と、データエンジニアが絶対に避けるべきパフォーマンスの地雷「Python UDF」について解説します。

## 1. 実務における「SQL」と「DataFrame API」の使い分け戦略

前章の通り、SQLとPySpark (DataFrame) はCatalyst Optimizerによって同じ実行計画に変換されるため、「速度」を理由に使い分ける必要はありません。**「保守性」「可読性」「動的処理」の観点で使い分けます。**

### 🟢 Spark SQL を採用すべきケース
*   **単純明快なデータ集計や抽出**：アナリストや他部門の人が見てもすぐに理解できるため、BI的な集計ロジック（`GROUP BY`, `CASE WHEN` など）はSQL（`%sql` または `spark.sql("SELECT ...")`）で書く方がチーム全体の保守性が高まります。
*   **MERGE INTO（アップサート）処理**：Delta Lakeへの複雑なインサート/アップデート処理は、Pythonのメソッドチェーンで書くよりSQLの `MERGE INTO` 構文で書いたほうが圧倒的に直感的で読みやすいです。

### 🔵 PySpark (DataFrame API) を採用すべきケース
*   **動的なETLパイプライン構築**：例えば「数十個のカラム名の空白をすべてアンダースコア `_` に一括置換したい」場合、SQLでは全カラムを手打ちする必要がありますが、PySparkならPythonの `for` ループを使って動的にメタプログラミングが可能です。
*   **モジュール化と再利用**：複雑な変換ロジックを関数化し、別ファイル（他のノートブックやPythonスクリプト）に切り出して、複数のジョブから `import` して使い回したい（テストコードも書きたい）場合は、PythonベースのDataFrame APIが必須となります。

> [!IMPORTANT]
> **実際の現場でのベストプラクティス**
> Databricks上ではノートブック環境を活かし、**ハイブリッドアプローチ**を取るのが主流です。
> 生データの複雑なクレンジングやループ処理はPySparkで実装し、最終的にクリーンになったデータフレームを一時ビューとして登録（`df.createOrReplaceTempView("temp_silver")`）してから、集計やMERGE部分は `%sql` マジックコマンドを使ってスッキリと表現する、という棲み分けが非常に強力です。

---

## 2. 最悪のパフォーマンス地雷「Python UDF」とその回避策

PySparkには、標準のSQL関数セット（`pyspark.sql.functions`内にある何百ものビルドイン関数）で表現しきれない「独自の複雑な処理」をユーザーが自作のPython関数で実装できる **UDF（User Defined Function: ユーザー定義関数）** という機能があります。

しかし、**通常のPython UDFは「パフォーマンスの絶対的アンチパターン」です。**

```python
# 🚫 現場でやってはいけない最悪のアプローチ（通常のPython UDF）
from pyspark.sql.functions import udf
from pyspark.sql.types import IntegerType

# 独自の複雑(？)なPythonロジック
def complex_math(salary):
    return salary * 2 + 100

# UDFの登録
bad_udf = udf(complex_math, IntegerType())

# 適用（激遅になる）
df.withColumn("new_salary", bad_udf("salary"))
```

### なぜ通常のPython UDFは遅いのか？（アーキテクチャの壁）
Sparkのデータ処理エンジンの中核は**JVM言語（Scala/Java）**で動いています。
標準のビルドイン関数を使えば全てJVM内で超高速に並列処理されますが、通常のPython UDFを使った瞬間、以下の悲劇（シリアライズ・オーバーヘッド）が全レコードに対して1行ずつ発生します。

1. C++で書かれたSparkのメモリ領域からデータを取り出す。
2. データを「JVMが理解できる形（Javaオブジェクト）」に変換する。
3. さらにそれを「Pythonプロセスが理解できる形（Pickle等）」に直列化（シリアライズ）して、ワーカーマシン上のPythonプロセスへ送る。
4. Python上で1行だけ処理を行う。
5. 全く逆の順序でJVMに戻す。

このデータの行ったり来たり（シリアライズ/デシリアライズ）に膨大な時間がかかり、処理は通常の組み込み関数の数万倍遅くなることがあります。

### ✅ 実務での回避策
1. **第一選択：なんとかして標準の `pyspark.sql.functions` を組み合わせて実現する。**
   Gemini Advanced等に「このPython処理のロジックを、PySparkの組み込み関数だけで表現して」と頼むのが最も賢い選択です。
2. **第二選択：Pandas UDF (Vectorized UDF) を使う**
   どうしても独自のPythonライブラリ（自然言語処理用のspaCyモジュール等）を使う必要がある場合は、Apache Arrow（高速なインメモリカラムフォーマット）を利用して、数十万行を一括配列としてシリアライズなしでPythonプロセスへ渡せる **Pandas UDF** を利用します。これならパフォーマンスの低下を最小限に抑えられます。
