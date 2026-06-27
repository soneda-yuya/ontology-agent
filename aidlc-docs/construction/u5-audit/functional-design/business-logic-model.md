# U5 Audit & Activity — Business Logic Model

技術非依存。Audit と Activity は別サービス・別ポート。

## L1. AuditService.record — US-E1
```
入力: AuditEvent（呼び出し元が組み立て or audit_hook が dict から生成）
1. PII 不混入を前提（呼び出し側が type/id/op のみ渡す。reason は PII-free）
2. AuditSinkPort.append(event)   # 追記専用（update/delete API なし）
失敗時: 例外を伝播 → 呼び出し元（U1/U2）は操作を成立させない（INV-2: 監査なきアクション不成立, fail-closed）
```

## L2. AuditService.query — US-E2（ガバナンス限定）
```
入力: principal, AuditFilter
1. PermissionGateway.authorize_object(principal, "AuditEvent", READ)  # AuditEvent は RESTRICTED → governance ロールのみ
2. AuditSinkPort.query(filter)
出力: list[AuditEvent]
```

## L3. ActivityService.record — US-H1/H4
```
入力: ActivityEvent（重要アクションのみ。visibility 既定 "shared"）
1. ActivityLogPort.append(event)   # 追記専用
※ Activity の記録失敗は Audit ほど致命ではないが、原則 fail-closed に倒す（設定で緩和可）
```

## L4. ActivityService.query — US-H4
```
入力: principal, ActivityFilter
1. PermissionGateway.authorize_query(principal, "ActivityEvent")  # ActivityEvent は SHARED → チーム広く読める
2. ActivityLogPort.query(filter)
出力: list[ActivityEvent]
```

## L5. フック適合（U1/U2 への注入）
```
audit_hook(event_dict):                      # U1 OntologyService.audit / U2 にも供給
    ev = AuditEvent(
        id=…, timestamp=…,                    # timestamp は record 時付与
        actor=principal.id, roles=principal.roles,
        operation=event_dict["op"],
        object_type=event_dict.get("type"),
        object_id=event_dict.get("id"),
        decision="allowed", outcome="ok",
    )
    AuditService.record(ev)
    if event_dict["op"] in SIGNIFICANT:       # put_object / invoke_action / register_type
        ActivityService.record(ActivityEvent(actor=…, action=summarize(event_dict), …))

deny の記録: PermissionGateway が PermissionDenied を投げる経路でも
    AuditService.record(AuditEvent(decision="denied", reason=…)) を残す（許可/拒否どちらも記録）。
```

## L6. 連携（container 配線・予定）
```
audit_service = AuditService(audit_sink, gateway)
activity_service = ActivityService(activity_log, gateway)
audit_adapter = AuditAdapter(audit_service, activity_service, ...)  # audit_hook 提供
OntologyService(..., authorize=gateway.authorize_hook, audit=audit_adapter.audit_hook)
```

## エラーハンドリング
- 追記専用：update/delete のメソッドを**提供しない**（構造的に不可）。
- PII：イベントに値を入れない（type/id/op/decision のみ）。
- 監査記録の失敗は操作失敗に倒す（INV-2 / SECURITY-14）。
