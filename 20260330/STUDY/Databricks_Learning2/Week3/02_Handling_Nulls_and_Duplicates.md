# 認定対策 Week 3②：欠損値 (NULL) と重複排除の厳密なメソッド挙動

PySpark DataFrame API における基礎的なデータプレパレーション（加工）の操作について、試験では**「関数の正確な名前」と「引数の意味」**が問われます。
特に「NULLの処理」と「重複の削除」は超がつくほどの頻出項目です。

## 1. 欠損値（NULL）の除去 `na.drop()`
DataFrameの中から、NULLが入っている汚い行（Row）を「ポイ捨て」するメソッドが `dropna()` または短縮形の `na.drop()` です。

> [!WARNING]
> **🚨 Exam Trap (dropの引数 "any" と "all" の違い)**
> これが頻出のひっかけ問題です。
> 
> *   `df.na.drop("any")` または単に `df.na.drop()` の意味
>     ➡️ その行の **どこか1つのカラムでもNULLがあれば、その行全体を容赦なく消去します**。（例：Emailアドレスだけ不明な人のデータも、全体が消えます）。
> *   `df.na.drop("all")` の意味
>     ➡️ その行の **すべてのカラムが完全にNULL（真っ白な空行）の場合だけ消去します**。（例：IDも名前もEmailも全部NULLという、完全に壊れたゴミ行だけをお掃除します）。
> 
> 試験で「レコード内のすべてのフィールドが欠損している行だけを安全に削除したい（I want to drop only the rows where every field is missing）」と聞かれたら、答えは **`.na.drop("all")`** です！

## 2. 欠損値（NULL）への埋め合わせ `na.fill()`
こちらはNULLを消すのではなく、「仮の値（例えば0や、"Unknown"）」で置換して埋める処理です。

*   **構文の暗記**: `df.na.fill(0)`、または `df.fillna(0)`（どちらも完璧に同じ挙動です）。
*   **特定のカラムだけを埋めたい場合（試験頻出）**:
    辞書型（Dictionary）を渡すか、リストを渡す構文がテストされます。
    ```python
    # 悪い例（これだと全部のStringカラムのNULLが文字で埋まってしまう）
    df.na.fill("Not Provided")
    
    # [正解] 辞書を使って「emailカラムのNULLだけを埋める」
    df.na.fill({"email": "Not Provided", "age": 0})
    ```

## 3. 重複の排除 `dropDuplicates()`
テーブル内に完全に同じ行が2つあった場合、どちらか片方だけを残してもう片方を消し去る処理です。

*   **基本構文**: `df.dropDuplicates()`。これは表全体を見て、すべてのカラムの値が完全に一致する「100%のクローン行」を探して削除します。
*   **特定カラムでの一意判定**: `df.dropDuplicates(["user_id"])` のようにカラム名をリスト形式で渡すと、「user_id」さえ被っていれば、他のカラムがどうであれ重複とみなして消滅させます。

> [!IMPORTANT]
> **🚨 Exam Focus (distinct() との違い)**
> *   PySparkに存在する `df.distinct()` は、引数を一切取ることができないため、「テーブル全体の完全一致」の重複排除しかできません。
> *   一方で `df.dropDuplicates(["colA"])` は、特定のカラムだけを見て排除できます。
> *   試験で「特定のキー（CustomerIDだけ）を見て重複を弾きたい」と言われたら、正解の選択肢は絶対に `distinct()` ではなく **`dropDuplicates()`** のみとなります。
