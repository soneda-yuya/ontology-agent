# U3 Retrieval / RAG — Infrastructure Design (lean)

[shared-infrastructure.md](../../shared-infrastructure.md) を継承。U3 固有はデータ1テーブルと索引のみ。

## U3 固有差分
- **新テーブル `file_index`**（path, content, tsv tsvector GENERATED, GIN）。マイグレーション `0004_u3_file_index.sql`（Code Generation）。
- **拡張不要**: 全文検索は PostgreSQL 組み込み（tsvector/to_tsvector/GIN）。pgvector はベクトル検索（phase2）導入時のみ。
- objects の GIN 索引は U1 で作成済（属性検索/集計に利用）。
- DB 権限: file_index の CRUD（最小権限, SECURITY-06）。
- コンピュート/ネットワーク/TLS の追加なし（shared 継承）。

## Compliance Summary (Infrastructure Design — U3)
- Security: shared 継承（SECURITY-01/07/12/14）+ SECURITY-06（file_index 最小権限）。ブロッキングなし。
- 注: phase2 のベクトル検索で pgvector 拡張・埋め込み生成のインフラ検討（将来）。
