# Azure Week 3②：Synapse StudioとPipelinesの微妙な立ち位置

前章（Week 2）で「最強の運び屋はAzure Data Factory (ADF)」だと明言しました。
しかし、Synapse Analyticsを作ると、その管理画面（Synapse Studio）の中に **「Synapse Pipeline (パイプライン)」という、ADFと見た目もボタンも全く同じクローン機能**が搭載されています。
この「マイクロソフトの社内政治が生んだ重複機能」をどう整理して設計するかが重要です。

## 1. Synapse Studio（巨大な統合管理画面）

AzureポータルからSynapseを開き、「Synapse Studioを開く」をクリックすると、専用のWeb画面に飛びます。
この画面一つで、データエンジニアリングの全てが完結するようにデザインされています。

*   **データ (Data):** ADLS内の生のCSVファイルや、専用SQLプール内のテーブルをツリー状に閲覧できます。
*   **開発 (Develop):** ここでSQLスクリプトを書いたり、Sparkクラスター上で動く『Synapse Notebook（裏側はSpark）』を書いたりします。（※Databricksの劣化版と言われることも…）。
*   **統合 (Integrate):** ここにあるのが **『Synapse Pipelines』** （つまりADFの双子の兄弟）です。

## 2. ADF vs Synapse 統合パイプラインの違いを覚える

> [!WARNING]
> **🚨 Exam Trap (何が同じで、何が違うのか)**
> 「ADFとSynapse Pipelineは機能が完全に同じだから、どちらを使っても良い」
> ➡️ **[不正解！] 微妙に異なる機能（制限）があります。**
> 
> *   **【同じこと】**: Copy Data、Mapping Data Flows、Webアクティビティ、Foreachループなどの機能やアイコンは**全く同じ**。裏のエンジン（Integration Runtime）も共通です。
> *   **【ADFにはあって、Synapseには【無い】もの】**:
>     1.  **SSIS Integration Runtime**: 古いSQL Serverパッケージをクラウドで動かす機能はSynapseの中にはありません（新規のモダン基盤だから）。
>     2.  **他のGitリポジトリの大規模連携機能の一部制限**。
> *   **【Synapse Pipeline にしかない特権】**:
>     1.  **「専用SQLプール」への中身のロード・連携がシームレス**。同じ空間（Synapse Studio内）にあるため、設定が異常に簡単。

### 🚀 アーキテクトの決断（実務の正解）

現状の巨大なシステム開発におけるベストプラクティスは以下の通りに収束しつつあります。

1.  「全社をまたぐ巨大なデータ移動」や「旧システム（オンプレ）からの複雑な泥臭いデータ移行」は、**Azure Data Factory (ADF)** の強力な統合・監視機能に任せる。
2.  「ADFが集めてきたキレイなデータ（Silver/Gold）」を、夜中の3時に「Synapseの専用SQLプールへロードして集計する最後の1歩」だけを **Synapse Pipeline** に任せる（もしくはADFからADLS経由で直接ロードする）。

全てを無理にSynapse Studioの中に詰め込もうとすると、数年後に限界が来るということを、アーキテクトとして頭に入力しておいてください。
