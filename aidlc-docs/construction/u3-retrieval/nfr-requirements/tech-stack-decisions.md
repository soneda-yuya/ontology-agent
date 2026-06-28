# U3 Retrieval / RAG — Tech Stack Decisions

U1/U2/U5/shared 継承。U3 固有のみ。

| 項目 | 決定 | 理由 |
|---|---|---|
| 言語/FW | Python + Pydantic v2（共通） | クエリモデル round-trip |
| 構造化検索 | JSONB + GIN（U1 の objects） | 型追加に DDL 不要 |
| 全文検索 | **PostgreSQL tsvector + GIN**（拡張不要） | ファイル本文検索（Q-R3=A） |
| 集計 | SQL GROUP BY + `date_trunc`（期間） | count/group_by/トレンド |
| ベクトル（phase2） | pgvector（拡張）interface のみ今回 | A→B 段階 |
| ポート | ObjectStorePort 拡張（query/aggregate）, 新規 FileIndexPort, VectorStorePort(phase2) | 検索能力を追加 |
| PBT | Hypothesis（共通） | round-trip / generators |

## スキーマ（U3, 概略）
```sql
CREATE TABLE file_index (
  path    TEXT PRIMARY KEY,
  content TEXT NOT NULL,
  tsv     tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED
);
CREATE INDEX idx_file_tsv ON file_index USING GIN (tsv);
-- objects の GIN は U1 で作成済（属性/集計に利用）
```

## ObjectStorePort 拡張（U1 への後方互換追加）
- `query(spec: SqlSpec) -> list[OntologyObject]`
- `aggregate(spec: AggregateSpec) -> list[AggregateRow]`
- 既存（get/exists/write/list_by_type）は不変。PostgresObjectStore に実装追加。テスト用フェイクは構造的に未使用メソッドは追加任意。

## 新規ポート / 実装
- `FileIndexPort`（search/ index）+ `PostgresFileIndex`（tsvector, parameterized）。
- `VectorStorePort`（phase2, interface のみ）。
