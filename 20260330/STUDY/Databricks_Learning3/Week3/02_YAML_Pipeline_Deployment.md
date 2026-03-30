# Part 3 Week 3②：YAMLによるIaC（インフラのコード化）実践

DABsの実体は、**`databricks.yml`** というたった1つのYAMLファイルです。
この中に「クラスターの種類」「Jobの依存関係（タスク設定）」「デプロイする先（Dev/Prod）」のすべてを記述可能であり、属人化を防ぐ強力なアーキテクチャとなります。

## 1. 宣言的デプロイメント（databricks.ymlの基本）

典型的な日次バッチ処理（Job）の定義は、以下のように直感的で人間が読めるYAMLで記述されます。

```yaml
# databricks.yml の一例

# バンドルの名前
bundle:
  name: my_etl_pipeline

# カスタム変数の設定（開発と本番で動的に変えるため）
variables:
  table_name:
    description: ターゲットテーブル名

# 作成するリソース（JobsやDLT等）の定義
resources:
  jobs:
    daily_sales_job: # このJobのおおもとの名前
      name: "Daily Sales ETL Job"
      tasks:
        # タスク1 (データ準備)
        - task_key: prepare_data
          notebook_task:
            notebook_path: ./src/prepare.py
          job_cluster_key: cheap_cluster
          
        # タスク2 (データ結合・タスク1の完了に依存する)
        - task_key: join_and_load
          depends_on:
            - task_key: prepare_data
          notebook_task:
            notebook_path: ./src/load.py
          job_cluster_key: cheap_cluster
```
※このように書くだけで、「`prepare_data` タスクが終わったら `join_and_load` タスクを動かす」というWorkflowsの依存関係のDAGが、デプロイ時にDatabricksの画面上に「絵」として全自動で描画・構築されます。

## 2. 環境（Target）の華麗な切り替え
DABsが優れているのは、「個人のテスト環境（Dev）」と「本番環境（Prod）」を、このファイルの中で美しく切り替えられる点です。

```yaml
# 環境ごとのデプロイ先（Target）の定義
targets:
  # ------ 開発環境用 ------
  dev:
    workspace:
      host: https://adb-xxxxx.azuredatabricks.net # Dev用のワークスペースURL
    default: true
    # 変数の書き換え
    variables:
      table_name: dev_catalog.sales.temp_table

  # ------ 本番環境用 ------
  prod:
    workspace:
      host: https://adb-yyyyy.azuredatabricks.net # Prod用のワークスペースURL
    variables:
      table_name: prod_catalog.sales.golden_table
```

### 🎯 魔法のコマンド
*   **私（ユーザーID: jordaさん）が、ローカルPCから開発環境にデプロイする時：**
    `databricks bundle deploy -t dev` を叩きます。
    するとDatabricksは気を利かせて、他の開発者と名前が被って喧嘩しないように、クラウド上のJob名を自動的に **「`[jorda] Daily Sales ETL Job`」** のように、デプロイした本人の名前付き（プレフィックス）で隔離されたJobとして構築してくれます。これにより「おまえが俺のテストジョブを上書きして壊しただろ！」という争いが永遠に消滅します。

*   **GitHubが、承認を経て本番環境に自動デプロイする時（本番CD）：**
    `databricks bundle deploy -t prod` が実行されます。本番用のテーブル名（Prod）が差し込まれ、今度は誰の名前も付いていない、綺麗な **「`Daily Sales ETL Job`」** という正式名称で本番ワークスペースに鎮座します。

> [!TIP]
> 複雑なUI操作を排除し、**「手元のコードエディタとターミナルだけですべてを完結させる」**。これが、高給取りのデータエンジニアたちがDABsをこぞって採用している唯一の理由です。
