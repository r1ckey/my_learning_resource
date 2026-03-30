# Part 4 Week 1①：世界最高峰のLLMを自社に引き込む（Foundation Model APIs）

「ChatGPTのAPI（OpenAI）を使えば簡単じゃん」と多くの中小企業が考えますが、一部の金融機関、医療機関、大企業などでは「自社の機密データを外部のSaaSベンダー（API）に送信することはコンプライアンス的に絶対に許されない」という非常に厳しい壁が存在します。

この最大の悩みを、**「Databricksの自社VPC（顧客専用の閉じたクラウド空間）内だけで、Meta社のLlama 3や、Databricksの特化型AI『DBRX』を動かしてしまう」** という技術で突破するのが、GenAI Engineeringの最初の武器です。

## 1. Foundation Model APIs とは？

Databricksが**「事前に数千億円かけて学習済みの超巨大AI（基盤モデル）」**を、あなたのワークスペース内に最初からメニューとして用意してくれている機能です。
自分でGPUクラスターを構築したり、数十GBのモデルデータをダウンロードしてくる必要は一切ありません。

### 🤖 用意されている主なモデル（Pay-per-token API）
画面の「Serving」タブを開くだけで、以下の強力なモデルがすでにAPIとしてスタンバイされています（※利用したトークン数＝文字数 に応じて数円だけ課金される超低コスト運用）。
*   **`meta-llama-3-70b-instruct`**: GPT-4クラスに匹敵するMetaの超高性能オープンモデル。
*   **`dbrx-instruct`**: Databricksが独自開発した、コーディングやデータ分析に特化した超優秀モデル。
*   **`mixtral-8x7b-instruct`**: 高速かつバランスの良いモデル。

## 2. APIの呼び出し方（OpenAI SDKと完全互換！）

「でも、今までOpenAIのAPIに合わせてアプリ作っちゃったよ…APIの書き方を全部変えるの面倒くさいな…」

> [!IMPORTANT]
> **🚀 ここが天才的！OpenAI SDKの騙し撃ち**
> Databricks Foundation Model APIは、なんと **「OpenAI APIと入力/出力の形式（インターフェース）を100%完全にパクって（準拠して）」** 作られています。
> つまり、Pythonの既存のOpenAI呼び出しコードの**「接続先URL」だけをDatabricksに書き換えるだけ**で、全くそのまま動きます。

```python
import os
from openai import OpenAI

# ⚠️ ポイント1: OpenAIのライブラリを使っているのに、接続先は自分のDatabricksワークスペース！
DATABRICKS_HOST = "https://adb-1234.azuredatabricks.net" 
DATABRICKS_TOKEN = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().get()

# openaiクライアントの向き先をDatabricksにすり替える
client = OpenAI(
  api_key=DATABRICKS_TOKEN,
  base_url=f"{DATABRICKS_HOST}/serving-endpoints"
)

# ⚠️ ポイント2: 呼び出すモデル名（Endpoint名）に 'dbrx' など指定する
chat_completion = client.chat.completions.create(
  messages=[{"role": "user", "content": "データレイクハウスのメリットを3つ教えて"}],
  model="databricks-dbrx-instruct",  # <-- ここを変えるだけ
  max_tokens=256
)

print(chat_completion.choices[0].message.content)
```

## 3. Provisioned Throughput (専用GPUの占有予約)

もう一点、エンタープライズ特有の要件が「APIのレスポンスが遅いとユーザーが離れるから、どれだけアクセスが来ても絶対に0.5秒以内で返してほしい」というパフォーマンス要件です。

Pay-per-token（従量課金）モードは、他のお客さんとGPUリソースを共有（シェア）しているため、稀に数秒待たされる（Rate Limitに引っかかる）ことがあります。

*   **解決策:** 「**Provisioned Throughput（プロビジョニングされたスループット）**」というモードを選択します。
*   **意味:** 「1時間に◯◯◯ドル払うから、このLlama 3モデルを動かすためのGPUサーバーを、**うちの会社専用に24時間貸し切らせてくれ**」というVIP契約です。これで絶対に遅延しない最強のチャットボットが完成します。
