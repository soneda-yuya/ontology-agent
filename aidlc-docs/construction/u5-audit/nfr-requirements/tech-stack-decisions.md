# U5 Audit & Activity — Tech Stack Decisions

U1/U2/shared を継承。U5 固有のみ。

| 項目 | 決定 | 理由 |
|---|---|---|
| 言語/FW | Python + Pydantic v2（共通） | AuditEvent/ActivityEvent を Pydantic で表現（round-trip） |
| ストア | PostgreSQL（共有）`audit_events` / `activity_events` の2テーブル | Audit と Activity を分離 |
| 追記 | 同期 INSERT（追記専用） | INV-2 / fail-closed |
| ポート | `AuditSinkPort`（append/query）, `ActivityLogPort`（append/query） | 差し替え/モック可 |
| サービス | `AuditService`, `ActivityService`, `AuditAdapter`（audit_hook 提供） | U1/U2 に注入 |
| PBT | Hypothesis（共通） | round-trip / generators |

## スキーマ（U5, 概略）
```sql
CREATE TABLE audit_events (
  id TEXT PRIMARY KEY, ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor TEXT, roles JSONB, operation TEXT NOT NULL,
  object_type TEXT, object_id TEXT,
  decision TEXT NOT NULL, outcome TEXT NOT NULL, reason TEXT
);
CREATE INDEX idx_audit_actor ON audit_events(actor);
CREATE INDEX idx_audit_type  ON audit_events(object_type);
CREATE INDEX idx_audit_ts    ON audit_events(ts);

CREATE TABLE activity_events (
  id TEXT PRIMARY KEY, ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  actor TEXT NOT NULL, action TEXT NOT NULL,
  object_type TEXT, object_id TEXT, visibility TEXT NOT NULL DEFAULT 'shared'
);
CREATE INDEX idx_activity_actor ON activity_events(actor);
CREATE INDEX idx_activity_ts    ON activity_events(ts);
-- 改ざん耐性: アプリ DB ユーザに UPDATE/DELETE を付与しない（SECURITY-14）
```

## 後方互換 / 影響
- U1/U2 への破壊的変更なし。`OntologyService(audit=...)` に AuditAdapter.audit_hook を注入（既定 no-op から置換）。
- ActivityEvent/AuditEvent は SHARED/RESTRICTED の擬似型として PermissionGateway 検索に用いる（型登録 or 規約で対応。Code Generation で確定）。
