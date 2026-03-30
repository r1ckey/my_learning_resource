# Part 3 Week 2②：CDC (変更データキャプチャ) の完全自動化構成

本番のデータ基盤において、メダリオンアーキテクチャの Silver層・Gold層を作る上で最も苦労するのが **「CDC: Change Data Capture（変更履歴の同期）」** です。
Part 1で学んだ単純な `MERGE INTO` コマンドの手書きから卒業し、Delta Live Tables (DLT)の最強機能である `APPLY CHANGES INTO` （宣言的CDC）を使ったシニアクラスの実装へ引き上げます。

## 1. 現場のCDC（変更同期）のリアルな泥臭さ
会社の基幹DB（MySQLやOracle）などで商品マスター（`Products` テーブル）が「更新」や「削除」されたとします。
多くの場合、AWSのDMS等を通じて、S3のブロンズ層には以下のような「履歴のJSONログ」がストリーミングで届き続けます（*Append-only*）。

| 操作タイプ (Op) | 商品ID | 商品名 | 価格 | タイムスタンプ |
| :--- | :--- | :--- | :--- | :--- |
| `INSERT` | P-01 | マウス | 3000 | 10:00 (1行目:作成) |
| `UPDATE` | P-01 | マウス(白) | 3500 | 11:30 (2行目:価格と名前変更) |
| `DELETE` | P-01 | None | None | 15:00 (3行目:商品廃番で削除) |

これを読んで現在の完全な状態（Silverテーブル）を維持したい場合、昔は「IDごとにグループ化して最新状態を取って（Window関数）、OpがDELETEなら本番テーブルからもDELETEし、UPDATEならレコードを書き換える MERGE構文を数百行書く...」という地獄の運用がありました。

## 2. DLT `APPLY CHANGES INTO` による一発解決

DatabricksのDLTを使えば、この複雑なCDC同期パイプライン（遅延処理、順序の追い越し対策、削除フラグの適用）を、**たった一つの宣言構文**に丸投げできます。

```sql
-- ① Silver層の「空のターゲットテーブル」を宣言する
CREATE OR REFRESH STREAMING LIVE TABLE silver_products_master;

-- ② CDC(変更キャプチャ)の自動処理ルールを宣言する
APPLY CHANGES INTO LIVE.silver_products_master
FROM stream(LIVE.bronze_product_cdc_logs)  -- 履歴ログが追記され続けるブロンズから読み込み
KEYS (product_id)                          -- 一意となる主キーを教える（これで重複排除とUPDATEが行われる）
SEQUENCE BY timestamp                      -- レコードの「新しさ」はどの列で判断するか教える（古いイベントが遅延で遅れて到着しても、履歴が先祖返りしないように保護）
APPLY AS DELETES WHEN op_type = 'DELETE'   -- ログの「op_typeカラム」が『DELETE』という文字だった場合、実体のSilverテーブルから本当にその行を消去（Drop）する
IGNORE NULL UPDATES                        -- （オプション）更新ログにNULLが混ざっていても、元のデータを維持する
;
```

> [!TIP]
> **🌟 デクララティブ（宣言型）アーキテクチャの究極系**
> ここには「`MERGE INTO`」も「`WHEN MATCHED THEN`」といった処理手順（How）は一切書かれていません。
> **「主キーはこれ」「削除条件はこれ」「タイムスタンプ順で正として」** というWhat（定義）を宣言するだけで、Databricksが裏側で勝手に最適なMERGE構文のSparkジョブに変換し、ストリーミング増分で全自動更新してくれます。
> 
> このコードが書ける（アーキテクチャが描ける）ようになれば、レガシーな夜間全件洗い替えバッチ運用を、極小コストの無停止（リアルタイム）CDCアーキテクチャへと自信を持ってリプレイスできます！
