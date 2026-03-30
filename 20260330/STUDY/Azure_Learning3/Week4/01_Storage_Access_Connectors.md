# Part 5 Week 4①：Unity Catalog とADLSの「見えない接着剤」

いよいよ、データガバナンスの中核である **Unity Catalog** が、実際にデータをどのように保存しているのか（その裏のセキュリティ配線）の秘密に迫ります。

## 1. Unity Catalog（メタストア）を作る時の疑問
「Unity Catalogを立ち上げる時、Azureの画面で『保存場所としてADLS Gen2のパス（URL）』を指定しました。でも、Unity Catalogのシステム側は、どうやってそのADLS Gen2の硬い扉の鍵を開けて、データを読み書き（Read/Write）しているのでしょうか？」

一昔前なら、「Unity Catalogに、ADLSの『アクセスキー（長ったらしい暗号パスワード）』や『SAS（Shared Access Signature）トークン』をコピーして貼り付けて保存させておく」というのが常識的なSaaSの手法でした。

しかし、それでは「そのトークンが漏れたら誰でもアクセスできてしまう」という致命的な脆弱性が残ります。

## 2. 接着剤：Access Connector for Azure Databricks

Azure環境下のUnity Catalogにおいて「パスワード文字列（SASトークン等）」を使うことは今やご法度（禁止）です。
代わりに使う特注の接着剤が、**Access Connector for Azure Databricks (Azure Databricks用アクセス・コネクタ)** と呼ばれるAzure専用のリソースです。

### ⚙️ セキュアな配線（アーキテクチャの全貌）

これこそが、アーキテクトがホワイトボードに描くべき**「資格情報（Credential）を一切コードに書かない、ゼロトラストなデータ連携図」**です。

1.  **コネクタの作成:** Azureポータル（AZ-104の世界）を開き、「Access Connector for Azure Databricks」というリソースをポチッと作成します。
    *   この瞬間、このコネクタに対して **システム割り当てのマネージドID（System Assigned Managed Identity）** が自動的に付与されます。（※前章で学んだ、パスワードを持たない『顔パス』のロボットです）。
2.  **ADLS (ストレージ) に「通行証」を渡す:** ADLS Gen2の設定（IAM・RBAC）を開き、いま作ったばかりの『Access Connectorの顔パスロボット』に対して、**`Storage Blob Data Contributor（ストレージ BLOB データ共同作成者）`** という「データの読み書き全権限」を付与します。
3.  **Unity Catalog にコネクタを教える:** Databricksの画面（DP-203の世界）を開き、Storage Credential（保存場所の資格情報）を設定する際、パスワードを入れる欄に「先ほど作ったAccess Connectorの **Resource ID（リソースID：`/subscriptions/xxxx/resourceGroups/yyyy/...`）というただのアドレス文字列**」を貼り付けます。

> [!IMPORTANT]
> **🚀 この設計がなぜ「最強」なのか？（What is the magic?）**
> *   私たちがDatabricks側に教えたのは『ただのアドレス（あのコネクタを使え）』だけであり、パスワードは一文字も記憶させていません。
> *   Databricks上で、ユーザーが `SELECT * FROM sales` というSQLを叩いた瞬間、Unity Catalogは「あ、Access Connector経由で入ればいいんだな」と判断し、Azureの裏の専用線を通り、Access Connector（顔パスロボット）に変装します。
> *   ADLS Gen2は、やってきた顔パスロボットを見て「あ、君は `Storage Blob Data Contributor` の権限を持ってるね。どうぞ入って！」と扉を開けます。
> 
> **パスワードの漏洩リスク、有効期限切れ（ローテーション忘れ）、アクセス権の管理地獄... これらすべてのエンタープライズの悩みを、たった一つのマネージドIDベースのコネクタで完全に解決するこの仕組みこそが、Azure Databricksが世界の頂点に立つ理由です。**
