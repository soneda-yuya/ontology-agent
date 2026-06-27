# U5 Audit & Activity — Deployment Architecture (lean)

U1 / shared-infrastructure を継承。**新しいデプロイ構成要素はない**。

- U5 は同一プロセス（モジュラーモノリス）内の論理モジュール。
- 追加は共有 PostgreSQL 内の `audit_events` / `activity_events` の2テーブル。
- 改ざん耐性のため、アプリ DB ユーザはこれらに INSERT/SELECT のみ（UPDATE/DELETE なし）。
- TLS / ネットワーク / シークレット / VM 構成は U1・shared と同一。

将来: ハッシュチェーン・保持/アーカイブ自動化（OPERATIONS）、必要なら追記の非同期化。
