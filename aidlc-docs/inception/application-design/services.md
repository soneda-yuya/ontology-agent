# Services & Orchestration — ontology-agent (Mini AIP)

## サービス境界
| サービス | 責務 | 依存 |
|---|---|---|
| **PermissionGateway** | 認可の単一通過点。型可否判定 + row 制約注入。fail-closed。 | PolicyStorePort, TypeRegistry |
| **OntologyService** | 型の登録/取得（ガバナンス操作） | TypeRegistryPort, PermissionGateway, AuditService |
| **RetrievalService** | 検索/取得/探索/集計/意味検索 | PermissionGateway, ObjectStorePort, VectorStorePort, AuditService |
| **ActionService** | 提案/実行（writeback） | PermissionGateway, ObjectStorePort, AuditService |
| **AuditService** | 記録/監査検索 | AuditSinkPort, PermissionGateway(検索時) |

## 標準オーケストレーション（読み取り系の不変フロー）
```
MCPServerAdapter
  -> authenticate(credential) via AuthenticatorPort      # 誰か/ロール確定
  -> RetrievalService.search_objects(principal, query)
        -> PermissionGateway.authorize_query(principal, query)   # 型可否 + row制約注入 (fail-closed)
        -> ObjectStorePort.query(constrained_spec)               # パラメタライズド
        -> AuditService.record(query_event + decision)           # 全件記録
        <- 権限通過分のみ返す
```

## アクション系フロー（提案 → 承認 → 実行）
```
propose_action:
  authorize_action(提案権限) -> 差分/前提条件を生成（実行しない） -> audit(proposal)
invoke_action(承認付き):
  authorize_action(実行権限) -> 前提条件 再評価 -> ObjectStore.write -> audit(execution + before/after)
  権限/前提を満たさなければ deny し audit に残す（fail-closed, SECURITY-15）
```

## 型登録フロー（ガバナンス）
```
register_type:
  authorize（ガバナンスロール限定） -> 型定義検証 -> TypeRegistryPort.save -> TypeRegistry 再読込 -> audit
  => 以後、Retrieval/Permission/Audit が新型に対し汎用動作（コード変更不要）
```

## 横断方針
- **認可は必ず PermissionGateway 経由**（サービスが直接 store を権限なしに呼ばない）。
- **監査は副作用ではなく必須ステップ**（記録失敗時はアクションを成立させない/fail-closed）。
- **PII** はプロパティの PII フラグに従い、ログ出力から除外（SECURITY-03）。
- **エラー時は deny / rollback**（SECURITY-15）。
