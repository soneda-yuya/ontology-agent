# U5 Audit & Activity — Code Summary

## 生成 / 変更ファイル
```
# U5 新規
src/mini_aip/domain/audit/models.py        # AuditEvent/ActivityEvent/フィルタ + SIGNIFICANT_OPS
src/mini_aip/ports/audit_sink.py           # AuditSinkPort（append/query, mutate/delete なし）
src/mini_aip/ports/activity_log.py         # ActivityLogPort
src/mini_aip/services/audit_service.py     # record(同期)/query(ガバナンス)
src/mini_aip/services/activity_service.py  # record(重要)/query(SHARED)
src/mini_aip/services/audit_adapter.py     # audit_hook（allow/deny + 重要なら Activity）
src/mini_aip/adapters/outbound/postgres/audit_sink.py     # PostgresAuditSink（INSERT/SELECT）
src/mini_aip/adapters/outbound/postgres/activity_log.py   # PostgresActivityLog
migrations/0003_u5_audit.sql               # audit_events / activity_events

# 変更（後方互換）
src/mini_aip/services/permission_gateway.py  # 任意 audit フック + 拒否時記録 + set_audit_hook
src/mini_aip/config/container.py             # secured builder に audit 注入 + 擬似型登録

# テスト
tests/unit/test_audit.py                  # services/adapter/append-only/PII-free/認可
tests/pbt/audit_generators.py             # PBT-07
tests/pbt/test_audit_roundtrip.py         # TP-AU1 round-trip
tests/integration/test_postgres_audit.py  # @integration
```

## 検証結果
- `pytest -m "not integration"`: **56 passed**
- `pytest`（integration 含む・実 PostgreSQL）: **61 passed**
- `ruff check`: clean / U1・U2 非回帰

## 効いている点
- **追記専用**: ポートに mutate/delete なし + DB ユーザに UPDATE/DELETE 付与なし（SECURITY-14）。
- **fail-closed**: 監査 record 失敗は例外伝播 → 操作不成立（INV-2）。
- **許可も拒否も記録**: U1 OntologyService（成功後）と PermissionGateway（拒否時, set_audit_hook 経由）の双方から audit_hook。
- **PII 非保持**: イベントは type/id/op/decision/action 要約のみ。
- **Audit=ガバナンス限定 / Activity=SHARED**: 擬似型 AuditEvent(RESTRICTED)/ActivityEvent(SHARED) を gateway の sharing 解決に登録。
- **配線**: `build_secured_ontology_service` が U1 の audit no-op を AuditAdapter に置換（gateway<->audit の循環は set_audit_hook で解消）。

## ストーリートレーサビリティ
- US-E1（全件記録・追記専用）/ US-E2（監査検索, ガバナンス）/ US-H1・H4（Activity 記録・文脈読取）

## 未実施 / 後続
- DB を要するテストの実行は CI/Build & Test（ローカルで検証済）。
- 単一 get の行レベル enforcement・集計は U3、外部副作用アクションは U4、MCP/HTTP/CLI は U6。
- 改ざん検知強化（ハッシュチェーン）・保持/アーカイブ自動化は将来（OPERATIONS）。
