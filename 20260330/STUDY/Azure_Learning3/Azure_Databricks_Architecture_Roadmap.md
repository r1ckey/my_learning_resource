# Azure Databricks アーキテクチャ設計・完全攻略ロードマップ

ここから先は、Databricks上の「NotebookでPythonが書ける」段階から、Azure環境下で**「数千人が利用するデータ基盤全体のネットワークとセキュリティを設計・構築する（Platform Architect）」** 段階へと昇華します。

実際の「エンタープライズ（大企業向け）データ基盤構築案件」において、最も単価が高く、最も炎上しやすく、しかし最も価値のある「インフラとデータエンジンの結合部分」の秘密を解き明かします。

## 🎯 このコース（Part 5）の目的
Databricks という強力なエンジンが、裏側にある Azure の VNet や Entra ID とどう連携し、どう権限をやり取りしているのか（**Black Boxの解明**）を目的とします。

1. **Week 1: コントロールプレーンとデータプレーンの分離構造**
   * 「DatabricksはSaaSかPaaSか？」アーキテクチャの根幹と、自社LAN（VNet）にエンジンをねじ込む `VNet Injection`。
2. **Week 2: 究極のネットワーク・セキュリティ**
   * ハッカーの侵入窓を物理的に塞ぐ `No Public IP (NPIP)` と、Azure専用線を通す `Private Link` のフロント・バックエンド構成。
3. **Week 3: Entra ID連携とアクセス制御**
   * 入退社時のアカウント自動同期 `SCIM` と、システム間の顔パス認証 `Managed Identity / Service Principal`。
4. **Week 4: Unity Catalogの「裏側」と Key Vault**
   * Unity CatalogがどうやってADLSの鍵を開けているのか（`Access Connectors`）と、『Azure Key Vault』から自動でパスワードを読むシークレットスコープ。

> [!TIP]
> **🚀 アーキテクトへの道**
> このPart 5の知識があれば、「社内ネットワーク規定が異常に厳しい銀行のインフラ担当者」との要件定義ミーティングで、「Databricksはこういう通信経路を取り、ユーザーデータは御社のVNetから一歩も外に出ません」と、ホワイトボードに図を描いて完璧に説明できるようになります！
