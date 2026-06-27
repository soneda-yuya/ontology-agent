# U5 Audit & Activity — Logical Components

| コンポーネント | 役割 | 配置 |
|---|---|---|
| **AuditEvent / ActivityEvent** | 不変イベントモデル（Pydantic, round-trip） | domain/audit |
| **AuditService** | record（同期・追記） / query（ガバナンス, gateway 経由） | services |
| **ActivityService** | record（重要アクション） / query（SHARED, gateway 経由） | services |
| **AuditAdapter** | U1/U2 の `audit(event_dict)` フックに適合。AuditEvent 化 + 重要なら ActivityEvent も | services |
| **AuditSinkPort** | append / query（mutate/delete なし） | ports |
| **ActivityLogPort** | append / query（mutate/delete なし） | ports |
| **PostgresAuditSink / PostgresActivityLog** | 追記専用実装（parameterized） | adapters/outbound/postgres |

## 統合パターン
```
書き込み/アクション（U1 put_object / U4 invoke_action 等）:
  ... 操作実行 ...
  audit=AuditAdapter.audit_hook(event_dict)         # 同期
     → AuditService.record(AuditEvent)              # 失敗→例外→操作不成立 (INV-2)
     → if significant: ActivityService.record(ActivityEvent)

権限拒否（U2 PermissionGateway）:
  PermissionDenied 経路でも AuditService.record(decision="denied")

監査検索（ガバナンス）:
  AuditService.query → gateway.authorize_object(principal,"AuditEvent",READ) → AuditSinkPort.query

Activity 参照（AI/チーム）:
  ActivityService.query → gateway.authorize_query(principal,"ActivityEvent") → ActivityLogPort.query
```

## DI（container 追記予定）
```
audit_sink = PostgresAuditSink(provider)
activity_log = PostgresActivityLog(provider)
audit_service = AuditService(audit_sink, gateway)
activity_service = ActivityService(activity_log, gateway)
audit_adapter = AuditAdapter(audit_service, activity_service)
OntologyService(..., authorize=gateway.authorize_hook, audit=audit_adapter.audit_hook)
```

## 擬似型 "AuditEvent" / "ActivityEvent"
- PermissionGateway は sharing_level を型から引く。Audit/Activity 用に
  RESTRICTED("AuditEvent") / SHARED("ActivityEvent") を**規約 or 型登録**で用意（Code Generation で確定）。

## 将来拡張（インターフェース不変）
- ハッシュチェーン（改ざん検知強化）、非同期バッファ（性能要件が出た場合）、保持/アーカイブ（OPERATIONS）。
