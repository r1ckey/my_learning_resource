# Part 3 Week 4①：Unity Catalog 「動的ビュー」による最強セキュリティ

Unity Catalogで「このテーブルはAさんには見せて、Bさんには見せない（GRANT SELECT）」という制御は簡単に行なえます。
しかし、大規模企業のエンタープライズ領域では、そのような「テーブル単位のざっくりとした権限」では通用しません。さらに細かく高度な以下の要求が必ず突きつけられます。

## 1. 大企業の「わがままな」データ閲覧要求

*   **要求A (行レベルの制限/Row-Level Filtering):**
    「『全社員の給与データ』という１つの大きなテーブルがあるとする。東京支社のマネージャーが見たときは**【東京の従業員の行だけ】**が表示され、大阪支社のマネージャーが見たときは**【大阪の従業員の行だけ】**が自動でフィルタリングされて表示されるようにしろ。データのコピーは許さない」
*   **要求B (列レベルの隠蔽/Column-Level Masking):**
    「同じテーブルで、平社員がアクセスした時は『給与（Salary）カラム』の中身だけが自動的に **`[*** 伏字 ***]`** になり、人事部長がアクセスした時だけホンモノの数字が閲覧できるようにしろ」

これに対し、「東京用テーブル」「大阪用テーブル」「平社員用ビュー」…とテーブル・ビューを無限に作り続けるのは、旧世代（レガシー）の設計者が陥る地獄のアンチパターンです。

## 2. Dynamic View（動的ビュー）という正解

Databricks (Unity Catalog) の標準関数である **`current_user()`** （今クエリを叩いているのは誰？）と **`is_account_group_member()`** （その人は「人事部長グループ」に所属しているか？）を組み合わせることで、**「たった1つのビュー」を定義するだけで全社員の要求を満たす自動可変セキュリティ**を実現できます。

### 🛡️ 列レベルの隠蔽（Column Masking）の実装例
```sql
-- 給与テーブル（src_salary）の上に被せるための、動的マスクをもったビューを作成
CREATE VIEW dynamic_salary_view AS
SELECT
  id,
  name,
  department,
  -- 🌟 ここが動的条件分岐（Dynamic Masking）
  CASE 
    -- 「人事グループ」に所属しているなら、生データの数字をそのまま見せる
    WHEN is_account_group_member('HR_Group') THEN salary
    -- それ以外の平社員・他部署の人間なら、強制的にゼロ（または伏せ字等）で返す
    ELSE 0 
  END AS salary_masked
FROM
  src_salary;
```

### 🛡️ 行レベルの制限（Row Filtering）の実装例
```sql
-- 自分の部署のデータ「だけ」が自動で絞り込まれるビュー
CREATE VIEW dynamic_department_view AS
SELECT * FROM src_salary
WHERE
  -- 🌟 今アクセスしているユーザーの部署IDと、データの部署IDが一致するものだけを通過させる
  department = user_department(current_user()); 
```

> [!CAUTION]
> **🚀 行フィルターと列フィルターの最新機能**
> ビュー（View）を作らなくても、Unity Catalogの新機能を使えば「元の生テーブル（Table）の構造の背後」に直接これらの動的関数（Row Filter / Column Mask）を埋め込むことも可能になっています。
> もし「テーブルを増やさずに、アクセスする人（グループ）によってデータの見え方・返す結果を動的に変えたい」という現場の要請が出た時は、**「Dynamic Views（動的ビュー） / Row & Column Filtering」**というキーワードを思い出してください。これがシニア・アーキテクトとしての答えです！
