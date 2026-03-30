# 第4週②：MLflowによる機械学習とメタデータ管理の自動化

データ基盤（メダリオンアーキテクチャとUnity Catalog構成）がクリーンになり、高い品質のGold層データが完成しました。次に行うべきは、そのデータを用いたAI／機械学習（ML）の実装です。
ここでは、Databricksが買収・統合した世界最強のML運用ツール「**MLflow**」の実務的な使い方を学びます。

## 1. モデル開発における「属人化とカオスの歴史」
データサイエンティストがモデル（例：来月の売上予測モデル）を作る時、Pythonノートブック上で「パラメータAを0.01、パラメータBを100にして...」と何度も学習（実験）をぶん回します。
*   **問題点:** 「1週間前に作った、あの『一番精度が良かった時のモデル』って、パラメータいくつで回したやつだっけ？」「そのモデルの重みファイル（pklファイル）、どこに保存した？」
*   **結果:** エクセルに手書きでパラメータと精度をメモし、ファイル名が `sales_model_v3_final_final2.pkl` といった形になり収拾がつかなくなりました。

## 2. MLflowによる「実験トラッキング（Experiment Tracking）」
このカオスを解決するのがMLflowのトラッキング機能です。コードに数行足すだけで、毎回の学習(Run)の「パラメータ（設定値）」「メトリクス（精度や誤差）」「アーティファクト（出来上がったモデルのファイルやグラフ画像）」を一元的に自動記録します。

### 実務での最も強力な機能：オートロギング（Auto-logging）
かつては `mlflow.log_param("learning_rate", 0.01)` のように一つ一つ手書きしていましたが、現在は主要なフレームワーク（scikit-learn, XGBoost, PyTorch等）に対して、**一行書くだけで全てのパラメータと結果を自動記録**してくれます。

```python
import mlflow
import mlflow.sklearn

# これを1行書くだけで、以降のsklearnによる学習の裏側を全て自動記録！
mlflow.sklearn.autolog()

# 「experiment_v1」という名前の実験空間で記録を開始
with mlflow.start_run(run_name="experiment_v1"):
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)
    
    # 📝 画面右上のアイコン（Experiment）をクリックすると、
    # 決定木の深さ、使用したデータセット、MAE・RMSEなどの各種誤差メトリクスが
    # 全て美しいUI（グラフ）にまとめられ、過去の実験との比較が一瞬で可能になります！
```

## 3. Unity Catalogと統合された「モデルレジストリ（Model Registry）」
MLflowの「Model Registry」は、**「完成した学習済みモデルを、データテーブルと同じようにカタログ管理・共有する」**機能です。

> [!IMPORTANT]
> **実務でのアーキテクチャ（Models in Unity Catalog）**
> 最新のDatabricksでは、機械学習モデルもUnity Catalogの一部として、テーブルと同様の「3層構造（カタログ・スキーマ・モデル）」で保存します。
>
> 例えば、データサイエンティストが頑張って精度99%の売上予測モデルを作り、それを `prod.sales.sales_forecasting_model` という名前でUCに登録（Register）したとします。
> 別の部署のエンジニアは、Pythonから `mlflow.pyfunc.load_model("models:/prod.sales.sales_forecasting_model/1")` と呼び出すだけで、すぐに本番システムへそのモデルをデプロイして予測を実行できます。
>
> テーブルと同様に「誰にこのモデルを使わせるか（GRANT EXECUTE ON MODEL...）」という権限設定ができるため、企業全体でのAIの使い回し（MLOps推進）が圧倒的に加速します。
