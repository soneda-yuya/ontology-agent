# U5 Audit & Activity — NFR Design Patterns

U1/U2 パターン + 共有インフラを継承。U5 固有のパターン。

## 追記・改ざん耐性パターン
- **Append-only port**: AuditSinkPort / ActivityLogPort は `append` / `query` のみ。**update/delete メソッドを構造的に持たない**（BR-AU1, SECURITY-14）。
- **DB-enforced immutability**: アプリ DB ユーザに `audit_events` / `activity_events` の UPDATE/DELETE を付与しない（Infrastructure）。

## 一貫性 / fail-closed
- **Synchronous record in critical path**: 監査追記は操作と同じ呼び出しパスで同期実行。失敗は例外で伝播し操作を不成立にする（INV-2, BR-AU4, SECURITY-15）。
- **Allow & deny 双方記録**: PermissionGateway の許可/拒否いずれも AuditEvent を残す（BR-AU3）。

## PII 安全
- **Ref-only events**: イベントは object_type / object_id / operation / decision / reason(PII-free) のみ保持（BR-AU2, SECURITY-03）。reason は固定的な安全文字列。

## 認可パターン
- **Audit query = RESTRICTED**（ガバナンス限定, PermissionGateway 経由, BR-AU6）。
- **Activity query = SHARED**（チーム広く読める, PermissionGateway 経由, BR-AU7）。

## 性能
- 追記は単純 INSERT。検索索引（actor/object_type/ts）。ホットパスは追記のみで軽量。

## テスト性
- **Pure event models** → round-trip（PBT-02, TP-AU1）。
- **Generators**（PBT-07）。ポートに mutate/delete が無いこと（TP-AU3）を構造テスト。

## マッピング
| NFR | パターン |
|---|---|
| U5-1/6/7 fail-closed | Synchronous record + 例外伝播 |
| U5-8 追記専用 | Append-only port + DB grant 制限 |
| U5-9 PII | Ref-only events |
| U5-10 認可 | Audit=RESTRICTED / Activity=SHARED via gateway |

## Compliance Summary (NFR Design — U5)
- Security: SECURITY-14/03/15/08 をパターン化。暗号化/NW は shared。ブロッキングなし。
- PBT: round-trip / generators / 構造不変。✅
