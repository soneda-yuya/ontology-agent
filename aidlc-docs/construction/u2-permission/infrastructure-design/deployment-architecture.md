# U2 Permission — Deployment Architecture (lean)

U1 の [deployment-architecture.md](../../u1-ontology-core/infrastructure-design/deployment-architecture.md) と
[shared-infrastructure.md](../../shared-infrastructure.md) を継承。**新しいデプロイ構成要素はない**。

- U2 は同一プロセス（モジュラーモノリス）内の論理モジュールとして稼働。
- 追加は共有 PostgreSQL 内の `policies` テーブルのみ。
- TLS / ネットワーク / シークレット / VM 構成は U1・shared と同一。

将来（水平スケール時）はポリシーのインメモリ無効化（LISTEN/NOTIFY）を U1 と同様に追加。
