# Part 3 Week 3①：次世代CI/CD革命「Databricks Asset Bundles (DABs)」

ここ数年でDatabricksの開発体験（DX）を決定的に変えた大革命が、**Databricks Asset Bundles (DABs)** の登場です。
これからのモダンなデータ基盤運用において、このDABsを知らない・使えないエンジニアは「旧世代」の烙印を押されてしまいます。

## 1. これまでの「手作業デプロイ」の限界

Part 1や2で学んだ「Databricksの画面（UI）からWorkflows（Jobs）のタスクをポチポチ作って、Dastabricks Git Foldersのノートブックを指定し、Run ifの条件をマウスで設定して、毎日深夜1時に動かすスケジュールを登録する…」

⬇️
**[最悪の問題発生]**
「よし、画面から完璧に設定できたぞ！」➡️「あれ？誰かが間違えてJobの設定を削除しちゃった…また最初から一時間かけてUIポチポチで設定を作り直さないと…」➡️「しかも開発環境(Dev)と本番環境(Prod)で2回同じポチポチ作業をしないといけないの！？」

この「インフラの設定（JobsやDLTの構成）が、コードとして管理されていないため再現性がない」という問題を解決するのが「IaC（Infrastructure as Code）」です。

## 2. 旧ツール（dbx）の死と、DABsの誕生
数年前まで、これを解決するために有志が作った `dbx` という非公式寄りのツールが使われていました。しかし設定のJSONが長大で難解なため、Databricks社がついに公式に、しかも超絶使いやすく作り上げた**決定版のCLIツール**が `Databricks Asset Bundles (DABs)` です。

> [!IMPORTANT]
> **🚀 DABs (Databricks Asset Bundles) の本質**
> DABsは、「コード（Python, SQL）」と「インフラ設定（Jobs、DLT、クラスターのサイズ設定など）」を1つのYAMLファイルにまとめ、「このファイルを読み込めば、**クラスター構成からJobの定期実行スケジュールまで、ゼロから全自動でDatabricks上に構築（デプロイ）される**」という魔法のバンドル（束）です。

## 3. DABsによる開発ワークフロー

シニアエンジニアの1日は、もはやDatabricksのブラウザ画面を開くことから始まりません。
手元のVS Code等のエディターから始まります。

1. **`databricks bundle init`**: 初期設定（ひな形）の一括作成。
2. VS Code等でPythonコードと連動するYAML（設定ファイル）を編集。
3. **`databricks bundle validate`**: 「設定にミス（文法エラーやタイポ）がないか？」を事前にチェック。
4. **`databricks bundle deploy -t dev`**: ワンコマンドで、自分の開発環境のDatabricksワークスペース上に、コード・クラスター・Jobの設定一式がネットワーク越しに自動展開・構築されます。
5. **`databricks bundle run`**: 手元のターミナルから、構築されたDatabricks上のJobをリモート実行します。

これら一連のサイクルを手動ではなく、GitHub Actions等のCI/CDツールに組み込み、「`main` にPushされたら、勝手に `-t prod` (本番環境)にデプロイして！」と自動化するのが、世界の標準構成（ベストプラクティス）です。
