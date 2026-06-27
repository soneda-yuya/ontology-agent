# U5 Audit & Activity — Domain Entities

Audit（改ざん不可の証跡）と Activity（共有作業履歴）は**別エンティティ・別ストア**。
いずれも **PII 値を保持しない**（参照=object_type/id と操作種別のみ, SECURITY-03/14）。

## AuditEvent（セキュリティ証跡）
| フィールド | 型 | 説明 |
|---|---|---|
| id | str | イベントID（UUID 文字列） |
| timestamp | str | ISO-8601（生成時に付与） |
| actor | str \| None | principal.id（None=未認証の試行） |
| roles | tuple[str, ...] | principal.roles |
| operation | str | register_type / put_object / get_object / search / invoke_action 等 |
| object_type | str \| None | 対象型 |
| object_id | str \| None | 対象ID（PII でない識別子） |
| decision | str | allowed / denied |
| outcome | str | ok / error |
| reason | str | PII-free（"deny-by-default" 等） |

## ActivityEvent（共有作業履歴・AIが文脈として読む）
| フィールド | 型 | 説明 |
|---|---|---|
| id | str | イベントID |
| timestamp | str | ISO-8601 |
| actor | str | principal.id（代理ユーザー） |
| action | str | 人間/AI が読む要約（例: "updated ticket status"） |
| object_type | str \| None | 関連型 |
| object_id | str \| None | 関連ID |
| visibility | str | 既定 "shared"（チーム共有）。SHARED 扱いで広く読める |

> **記録範囲（Q-A2=A）**: 重要アクションのみ（put_object / invoke_action / register_type 等）。読み取りは Activity に残さない（Audit には残す）。

## フィルタ
### AuditFilter（ガバナンス検索用）
| フィールド | 型 |
|---|---|
| actor | str \| None |
| object_type | str \| None |
| since / until | str \| None（ISO） |
| decision | str \| None |
| limit | int |

### ActivityFilter
| フィールド | 型 |
|---|---|
| actor | str \| None |
| object_type | str \| None |
| since / until | str \| None |
| limit | int |

## 関係
```
AuditSinkPort   1───* AuditEvent     （append-only）
ActivityLogPort 1───* ActivityEvent  （append-only）
AuditService  ─uses→ AuditSinkPort (+ PermissionGateway: 検索の認可)
ActivityService ─uses→ ActivityLogPort (+ PermissionGateway: SHARED 読み取り)
```
