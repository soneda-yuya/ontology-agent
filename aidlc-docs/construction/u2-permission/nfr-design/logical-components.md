# U2 Permission — Logical Components

| コンポーネント | 役割 | 配置 |
|---|---|---|
| **Decision functions** | `decide` / `row_constraint`（純関数） | domain/permission |
| **PolicyRegistry** | ポリシーのインメモリ索引（role/type で引く）。起動時ロード + 変更時更新 | domain/permission or services |
| **PermissionGateway** | 中央通過点。判定を包み fail-closed。authorize_object/query/action | services |
| **AuthorizeHookAdapter** | gateway を U1 OntologyService の `authorize(operation, context)` 署名に適合 | services（gateway 内メソッドでも可） |
| **PolicyStorePort** | ポリシーの load_all / save | ports |
| **PostgresPolicyStore** | policies テーブル実装（パラメタライズド, JSONB） | adapters/outbound/postgres |

## 統合パターン
```
起動:
  PolicyStorePort.load_all() → PolicyRegistry.load()

判定（read 系）:
  PermissionGateway.authorize_query(principal, type)
     → row_constraint(principal, READ, type, sharing_level)  # 純関数
     → AccessConstraint（U3 が SQL 化）

判定（単一/write/admin）:
  PermissionGateway.authorize_object/action(...)
     → decide(...)  # 純関数
     → DENY なら PermissionDenied（fail-closed, 監査へ）

U1 連携:
  container: OntologyService(authorize=gateway.authorize_hook)  # no-op を実権限へ置換
```

## DI（container 追記予定）
- `PolicyStorePort = PostgresPolicyStore(provider)`
- `PolicyRegistry` ← load_all
- `PermissionGateway(policy_registry, type_registry)`
- `OntologyService(..., authorize=gateway.authorize_hook, audit=...)`（audit は U5 で）

## 将来拡張（インターフェース不変）
- マルチプロセス時のポリシー無効化（LISTEN/NOTIFY、U1 と同）。
- 行述語の表現拡張（現在は属性マッチ。将来 DSL 等）。
