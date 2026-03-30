# 認定対策 Week 4②：Delta Live Tables (DLT) と制約の極め方

DLT (Delta Live Tables) は、Data Engineer Associate試験の合否を左右する配点15%の重要パートです。
実務（Week 3）で学んだ通り、DLTは「デクララティブ（宣言型）パイプライン」ですが、試験ではその**「実行方法の裏ルール」と「3つの制約（Expectations）の英語の完全暗記」**が求められます。

## 1. DLTノートブックの「実行」の罠

あなたが「DLTのコード（`CREATE LIVE TABLE ...`）」を書いたノートブックを共有され、それを実行してテーブルを作りたいとします。

> [!WARNING]
> **🚨 Exam Trap (DLTはどうやって起動するか？)**
> ノートブックを開いて、右上の「Run All（すべて実行）」ボタンを押すか、セルで `Shift + Enter` を叩きました。どうなるでしょうか？
> 
> **[絶対の正解]**: **エラーになり、実行に失敗します。**
> DLTは「通常のノートブックのようには実行できない」という決定的な仕様があります。
> DLTのコードを動かすには、ノートブック自体を実行するのではなく、Databricksの左メニューから「**Workflows > Delta Live Tables**」を開き、**「DLTパイプライン（Pipeline）」という箱を作って、そこに先ほどのノートブックをソースとして登録し、Pipeline側から「Start」を押さなければ絶対に動かない** というのが試験の超頻出トラップです。

## 2. Expectations (データ品質制約) の3段活用

「データ品質（Data Quality）を保証する」というキーワードが出たら、**DLT Expectations (制約)** に関する問題です。
以下の3つのアクションによる「行の扱い」と「パイプラインの状態」の違いを完璧に暗記してください。

### ① `EXPECT` (ただ監視するだけ)
*   **構文:** `CONSTRAINT valid_id EXPECT (id IS NOT NULL)`
*   **不正な行（無効な行）の扱い:** 削除（Drop）**しません**。そのままターゲットテーブルに書き込まれます。
*   **パイプラインの扱い:** エラーにもならず、成功（Succeeded）として継続します。ただし、DLTのUI（ダッシュボード）には「何行が制約に違反したか」のメトリクスが警告として記録されます。

### ② `EXPECT ... ON VIOLATION DROP ROW` (不正行をポイ捨て)
*   **構文:** `CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION DROP ROW`
*   **不正な行の扱い:** **削除（Drop）されます。** ターゲットテーブルには綺麗な行しか届きません。
*   **パイプラインの扱い:** 不正な行があったとしてもエラーにはならず、成功（Succeeded）のまま処理を継続します。

### ③ `EXPECT ... ON VIOLATION FAIL UPDATE` (1行でもあれば即死・アボート)
*   **構文:** `CONSTRAINT valid_id EXPECT (id IS NOT NULL) ON VIOLATION FAIL UPDATE`
*   **不正な行の扱い:** （※パイプライン全体が止まるため、ターゲットへの書き込み自体が中止されます）
*   **パイプラインの扱い:** 即座にパイプライン全体が **失敗（Failed）して強制終了（ストップ）** します。

> [!IMPORTANT]
> **🚨 Exam Focus (キーワードの回収)**
> 試験で「データエンジニアは、不正な行を見つけた場合には**ターゲットテーブルへの流し込み（処理）を続行させたまま、不正な行（invalid records）だけを取り除きたい（eliminate/drop）**」と来たら、正解は必ず **`ON VIOLATION DROP ROW`** です。このキーワードのマッチングゲームに勝ってください。
