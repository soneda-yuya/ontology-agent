# U2 Permission — Infrastructure Design (lean)

U2 は新たなインフラ要素を持たず、[shared-infrastructure.md](../../shared-infrastructure.md) を**完全継承**する。
追加はデータストアの 1 テーブル（`policies`）のみ。

## 継承（shared-infrastructure）
- デプロイ: クラウド VM 単一インスタンス上のモジュラーモノリス（U2 は同一プロセス内モジュール）。
- データ: 共有 PostgreSQL。U2 は `policies` テーブルを利用。
- 暗号化/ネットワーク/シークレット/ログ: shared と同一（SECURITY-01/06/07/12/14）。

## U2 固有のインフラ差分
- **新テーブル `policies`**（JSONB ルール）。マイグレーション `migrations/0002_u2_policies.sql` を追加（Code Generation で作成）。
- **DB 権限**: アプリの DB ユーザに `policies` への CRUD を付与（最小権限, SECURITY-06）。
- ネットワーク/コンピュート/TLS の追加要素なし。

## Compliance Summary (Infrastructure Design — U2)
- Security: shared-infrastructure を継承（SECURITY-01/06/07/12/14）。U2 固有のブロッキングなし。
- 注: 認証（principal 供給）・CORS・レート制限は U6。
