# U5 Audit & Activity — Infrastructure Design (lean)

[shared-infrastructure.md](../../shared-infrastructure.md) を継承。U5 固有はデータ2テーブルと DB 権限のみ。

## U5 固有差分
- **新テーブル**: `audit_events` / `activity_events`（マイグレーション `0003_u5_audit.sql`、Code Generation）。
- **改ざん耐性（重要）**: アプリ DB ユーザに両テーブルの **UPDATE/DELETE を付与しない**（INSERT/SELECT のみ）。SECURITY-14。
  - 保持/パージは別ロール or 運用ジョブ（OPERATIONS）で実施。アプリ自身は自ログを削除/改変できない。
- **保持**: ≥ 90 日（SECURITY-14）。アーカイブ/パージ運用は OPERATIONS。
- コンピュート/ネットワーク/TLS の追加なし（shared 継承）。

## Compliance Summary (Infrastructure Design — U5)
- Security: SECURITY-14（追記専用 DB 権限・保持）, SECURITY-06（最小権限：アプリは UPDATE/DELETE 不可）。その他は shared 継承。ブロッキングなし。
