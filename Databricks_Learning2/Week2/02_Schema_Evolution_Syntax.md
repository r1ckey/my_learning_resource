# 認定対策 Week 2②：スキーマエボリューション（mergeSchemaとoverwriteSchema）

Delta Lakeは、データに不正なカラムが入ってくるのを防ぐ「Schema Enforcement（スキーマ強制）」がデフォルトでオンになっています。意図的にスキーマ（列の構造）を変更して書き込む場合、Data Engineer Associate試験ではその**オプションの厳密な挙動の違い**が問われます。

## 1. Schema Enforcement（デフォルトのエラー挙動）
あらかじめ「ID (Int)」「Name (String)」という2つのカラムで作られたDeltaテーブルに対して、「ID」「Name」に加えて「Age (Int)」が追加されたDataFrameを `APPEND`（追記）で書き込もうとした場合を考えます。

*   **挙動**: **`AnalysisException` というエラーが発生し、書き込みは失敗します。**
*   **理由**: 「予期しない変なゴミカラム(Age)が混ざってるよ！データ基盤が汚れるからブロックしたよ！」というDelta Lakeの防御機能です。

## 2. mergeSchema の罠（カラム追加はOK、削除や型変更はNG）

「いや、サービスがアップデートされて新しい情報(Age)が取れるようになったんだから、データパイプラインでもこの列を追加して保存したい！」という正当な理由があるときに使うのが、**Schema Evolution (スキーマエボリューション)** です。

```python
# PySparkでのオプション指定 (試験で完全暗記すべき構文)
df.write \
  .format("delta") \
  .mode("append") \
  .option("mergeSchema", "true") \
  .save("/path/to/table")
```

> [!WARNING]
> **🚨 Exam Trap (mergeSchemaの限界)**
> `mergeSchema` は万能ではありません。**できることとできないことが明確に分かれています。**
> 
> *   ⭕️ **できること**: 新しい列（Ageなど）をテーブルの末尾に**追加**すること。
> *   ❌ **できないこと1**: 既存の列を**削除**する（いらなくなったName列を消したDataframeを書き込む）こと。※エラーになります。
> *   ❌ **できないこと2**: 既存の列の**データ型を変更**する（ID列を `Int` から `String` に変えて書き込む）こと。※エラーになります。

## 3. overwriteSchema による強制書き換え

前述の通り、「不要になった列をどうしても削除したい」「型の変更（例えば `Int` の代わりに桁の大きい `Long` にしたい）を行いたい」という場合、`mergeSchema` では絶対に解決できません。

その場合に出題される正解が **`overwriteSchema`** オプションです。

```python
# 既存のカラム構成を無視して、今回のDataFrameのスキーマで「テーブルそのものを強制上書き」する
df.write \
  .format("delta") \
  .mode("overwrite") \
  .option("overwriteSchema", "true") \
  .save("/path/to/table")
```

> [!IMPORTANT]
> **🚨 Exam Focus (キーワードの回収)**
> **[問題文]**: 「データエンジニアが、既存のDeltaテーブルからパスワード列を含むいくつかの**列を削除（Drop/Remove）したい**と考えています。どのように新しいDataFrameを書き込むのがよいですか？」
> **[引っかけの選択肢]**: `.option("mergeSchema", "true")` とする。 (←罠です。列の削除はできません)
> **[絶対の正解]**: `.mode("overwrite").option("overwriteSchema", "true")` とする。
