# U5 Audit & Activity — Business Rules & Testable Properties

## Business Rules
- BR-AU1 **追記専用**: Audit/Activity に update/delete API を設けない。DB ユーザにも UPDATE/DELETE を付与しない（SECURITY-14）。
- BR-AU2 **PII 非保持**: イベントは object_type / object_id / operation / decision / reason(PII-free) のみ。属性値・PII を保存しない（SECURITY-03）。
- BR-AU3 **許可も拒否も記録**: アクセスの allowed / denied 双方を Audit に残す。
- BR-AU4 **監査なきアクション不成立**: 監査記録に失敗したら操作を成立させない（INV-2, fail-closed, SECURITY-15）。
- BR-AU5 **Activity は重要アクションのみ**（put_object / invoke_action / register_type 等）。読み取りは Activity に残さない。
- BR-AU6 **Audit 検索はガバナンス限定**（AuditEvent=RESTRICTED, PermissionGateway 経由）。
- BR-AU7 **Activity 読み取りは SHARED**（ActivityEvent=SHARED, チーム広く読める, PermissionGateway 経由）。

## Testable Properties（PBT-01）
| ID | カテゴリ | プロパティ | 対応 |
|---|---|---|---|
| TP-AU1 | Round-trip (PBT-02) | `deserialize(serialize(AuditEvent)) == AuditEvent`（ActivityEvent も） | 永続/転送 |
| TP-AU2 | Invariant | 生成された AuditEvent に PII フィールドが存在しない（type/id/op/decision/reason のみ） | BR-AU2 |
| TP-AU3 | Invariant | AuditSinkPort / ActivityLogPort に mutate/delete 操作が存在しない（構造） | BR-AU1 |

### Generators（PBT-07）
- `gen_audit_event()` / `gen_activity_event()` — 型整合・PII を含まない値で生成。

> U5 で enforced な PBT は PBT-02（round-trip: TP-AU1）と PBT-07（generators）。

## Compliance Summary (Functional Design — U5)
- **Security**: SECURITY-14（追記専用/改ざん耐性/保持）, 03（PII非保持）, 15（監査なき不成立）, 08（検索の認可）を反映。ブロッキングなし。
- **PBT**: round-trip / generators を設計。
- **連携**: U1/U2 の `audit` フックに `AuditAdapter.audit_hook` を注入。許可/拒否双方を記録。
