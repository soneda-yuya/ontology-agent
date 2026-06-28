# U3 Retrieval / RAG — Deployment Architecture (lean)

U1 / shared-infrastructure を継承。**新しいデプロイ構成要素はない**。

- U3 は同一プロセス（モジュラーモノリス）内の論理モジュール。
- 追加は共有 PostgreSQL 内の `file_index` テーブル（tsvector + GIN）。
- 全文検索は組み込み機能（拡張不要）。ベクトル検索（phase2）導入時に pgvector 拡張を追加。
- TLS / ネットワーク / シークレット / VM 構成は U1・shared と同一。
