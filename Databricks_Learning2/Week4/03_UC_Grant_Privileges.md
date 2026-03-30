# 認定対策 Week 4③：Unity Catalog特権（Grants）とリネージ

Data Engineer Associate試験の総仕上げは、「Unity Catalog」のアクセス制御モデル（ガバナンス）です。
実務では「Data Steward（データスチュワード）」等の担当者がUI（Data Explorer画面）でポチポチと手動で権限を付与することが多いですが、試験では**SQLでの `GRANT` 構文とその「依存関係の階層構造」が徹底的に問われます。**

## 1. 3層名前空間と「特権の依存（USE CATALOGの罠）」

Unity Catalogのテーブルは `カタログ.スキーマ.テーブル` の3層で守られています。
「あるデータ・アナリストに、`prod` カタログの `sales` スキーマの中にある、`revenue_table` テーブルだけを見せたい（`SELECT` させたい）」という場面を考えます。

```sql
-- 権限を渡すコマンド
GRANT SELECT ON TABLE prod.sales.revenue_table TO analyst_group;
```

> [!WARNING]
> **🚨 Exam Trap (このコマンドだけではSELECTできない理由)**
> 面白いことに、↑のコマンドを打った直後に `analyst_group` の人が `SELECT * FROM prod.sales.revenue_table` を実行しても、**「そんなテーブルはない」と弾かれて（エラーになって）しまいます。**
> 
> なぜなら、Unity Catalogの強固なセキュリティでは、最下層の「テーブルへのSELECT権限」を持っているだけでは不十分で、そこへたどり着くための「上の階層の扉を開ける鍵」もセットで持っていなければならないからです。
> 
> **[絶対の正解]**: `SELECT` を機能させるには、以下の2つの特権も、別に付与しなければなりません。
> 1.  カタログに対する **`USE CATALOG`** 権限 （`GRANT USE CATALOG ON CATALOG prod TO analyst_group;`）
> 2.  スキーマに対する **`USE SCHEMA`** 権限 （`GRANT USE SCHEMA ON SCHEMA prod.sales TO analyst_group;`）
> 
> 試験で「なぜ権限があるのに読めないのか？」という問題が出たら、**「`USE CATALOG` または `USE SCHEMA` が欠如しているから」**という選択肢が100%正解です。

## 2. 権限の取り消し（REVOKE）と下位への波及
付与した権限を取り上げる（剥奪する）コマンドは `REVOKE` です。

```sql
REVOKE SELECT ON TABLE prod.sales.revenue_table FROM old_analyst;
```

試験の頻出パターンとして、「あるスキーマ全体に対する `SELECT` 権限を持っている人に、特定の1つの機密テーブルだけについて `REVOKE SELECT` を掛けたら、その人はそのテーブルを見れなくなるか？」という問題があります。
*   答えは、見られなくなります。（※明示的な拒否・剥奪が優先されます）。

## 3. Data Lineage (データ・リネージ / データの系譜) の制約

Unity Catalogの最強機能の一つが、「データの出処と行き先（どこから来て、どこに渡っているグラフを描画するか）」を自動で可視化する **Lineage (リネージ)** 機能です。

> [!IMPORTANT]
> **🚨 Exam Focus (Lineageは「何」を追跡できるのか？)**
> 試験では、「どういう条件の時にリネージ（グラフ）が正しく描画されるか」という制約が問われます。
> 
> *   ⭕️ **描画できるもの**: 「テーブル間の関係性」と「カラム（列）間の関係性」。また、これらは**「DatabricksのクラスターやSQL Warehouse等を使って実行されたクエリ」からのみ**自動抽出されます。
> *   ❌ **描画できないもの (罠)**: 
>     *   外部システム（例えば、AWS上のオンプレのSparkクラスター等）から直接API等で投げ込まれた場合の変換履歴は、UCのコンピュートエンジンを通っていないためトラッキングされません。
>     *   「特定の行（Rowレベル）」の追跡はできません。テーブル単位と列単位のみです。
