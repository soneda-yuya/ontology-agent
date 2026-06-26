# Component Dependencies — ontology-agent (Mini AIP)

## 依存マトリクス（行が列に依存）
| ↓依存元 \ 依存先→ | PermGateway | OntologySvc | RetrievalSvc | ActionSvc | AuditSvc | Ports |
|---|---|---|---|---|---|---|
| MCPServerAdapter | – | ✓ | ✓ | ✓ | ✓(検索) | Authenticator |
| OntologyService | ✓ | – | – | – | ✓ | TypeRegistry |
| RetrievalService | ✓ | – | – | – | ✓ | ObjectStore, VectorStore |
| ActionService | ✓ | – | – | – | ✓ | ObjectStore |
| AuditService | ✓(検索時) | – | – | – | – | AuditSink |
| PermissionGateway | – | – | – | – | – | PolicyStore, TypeRegistry |

- ドメイン core はどのサービス/アダプタにも依存しない（依存方向は内向き = ヘキサゴナルの原則）。
- アダプタはポートにのみ依存し、サービスはポート interface にのみ依存（実装非依存）。

## 通信パターン
- すべて **同一プロセス内のメソッド呼び出し**（同期）。外部 I/O は Port 実装（PostgreSQL/pgvector）に限定。
- MCP は inbound adapter としてツール呼び出しをサービス呼び出しへ変換。

## データフロー（読み取り）
```
[AIクライアント] --MCP--> [MCPServerAdapter] --auth--> [Principal]
   --> [RetrievalService] --authorize--> [PermissionGateway] --policy--> [PolicyStore]
   --constrained query--> [ObjectStorePort] --> [PostgreSQL]
   --record--> [AuditService] --> [AuditSink(append-only)]
   <-- 権限通過データ <--
```

## データフロー（書き込み/アクション）
```
[AIクライアント] --MCP propose--> [ActionService] --authorize--> [PermissionGateway]
   <-- 提案(差分・前提) -- (実行なし) --audit-->
[承認] --MCP invoke--> [ActionService] --authorize+前提再評価-->
   --> [ObjectStorePort.write] --> [PostgreSQL]
   --audit(before/after)--> [AuditSink]
```

## 重要な不変条件（設計レベル）
- INV-1: store/vector へのアクセスは必ず PermissionGateway 通過後（バイパス経路なし）。
- INV-2: 監査記録のないアクション成立は存在しない。
- INV-3: 型追加で core/サービス/アダプタのコード変更が不要（TypeRegistry 経由）。
- INV-4: 認証失敗・権限評価失敗・前提不成立は常に deny（fail-closed）。
