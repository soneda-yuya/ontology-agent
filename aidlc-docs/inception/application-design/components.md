# Components — ontology-agent (Mini AIP)

**Architecture**: Hexagonal (Ports & Adapters)
**Type model**: Hybrid（汎用データ駆動レジストリ + 任意の Pydantic スキーマ検証）
**Permission**: 中央集権ゲートウェイ（fail-closed）
**Abstraction**: store/vector/audit/policy/auth をポートで抽象化

```
            INBOUND ADAPTERS (driving)
        +------------------------------+
        |  MCP Server Adapter          |  ← Claude 等のAIクライアント
        |  (REST Adapter: optional)    |
        +---------------+--------------+
                        |
            APPLICATION (service layer)
        +---------------v--------------+
        | OntologyService              |
        | RetrievalService             |
        | ActionService                |
        | AuditService                 |
        |   ── すべて経由 ──            |
        | PermissionGateway (central)  |
        +---------------+--------------+
                        |  (uses ports)
              DOMAIN (pure core)
        +------------------------------+
        | TypeRegistry / OntologyObject |
        | Query / Aggregate / Traversal |
        | Permission policy & decision  |
        | ActionProposal / AuditEvent   |
        +---------------+--------------+
                        |  PORTS (interfaces)
        +---------------v--------------+
        | ObjectStorePort VectorStorePort
        | PolicyStorePort TypeRegistryPort
        | AuditSinkPort   AuthenticatorPort
        +---------------+--------------+
                        |
            OUTBOUND ADAPTERS (driven)
        +------------------------------+
        | PostgresObjectStore          |
        | PgVectorStore (phase 2)      |
        | PostgresPolicyStore          |
        | PostgresTypeRegistry         |
        | PostgresAuditSink (append)   |
        | TokenAuthenticator           |
        +------------------------------+
```

## Domain (core) — フレームワーク非依存の純粋ロジック

### C-D1 Ontology Model
- **責務**: `PropertyType`, `ObjectType`, `LinkType`, `ActionType` の定義と `OntologyObject`（汎用インスタンス）。ハイブリッド型方式: 型定義はデータ、検証は任意で Pydantic。
- **インターフェース**: 型定義の妥当性検証、オブジェクトの型整合チェック。

### C-D2 TypeRegistry
- **責務**: 登録された型のインメモリ索引。題材追加 = 型登録のみ（他レイヤ不変）。
- **インターフェース**: `get_object_type`, `list_object_types`, `get_link_type`, `get_action_type`。

### C-D3 Query Model
- **責務**: `ObjectQuery`（属性フィルタ）, `TraversalSpec`（リンク探索）, `AggregateQuery`（count/group-by/期間）。権限フィルタを表現する `AccessConstraint` を保持。
- **インターフェース**: クエリの構築・検証（純関数。PBT 対象）。

### C-D4 Permission Model
- **責務**: `Principal`(ユーザー), `Role`, `PermissionPolicy`(object-type + row-level 条件), `AccessDecision`。解決アルゴリズム（deny 優先, deny-by-default）。
- **インターフェース**: `decide(principal, action, target) -> AccessDecision`, `row_constraint(principal, object_type) -> AccessConstraint`（純関数。PBT-03 invariant 対象）。

### C-D5 Action Model
- **責務**: `ActionProposal`(差分・前提条件), `ActionResult`, アクションの妥当性。
- **インターフェース**: 提案生成、前提条件評価。

### C-D6 Audit Model
- **責務**: `AuditEvent`（actor/role/timestamp/op/target/decision）の不変表現。
- **インターフェース**: イベント生成（純）。

## Application (service layer) — オーケストレーション

### C-A1 PermissionGateway（中央集権・必須通過点）
- **責務**: すべての読み取り/集計/アクションが通過。クエリに row-level 制約を注入し、型レベル可否を判定。fail-closed。判定結果を AuditService に渡す。
- **インターフェース**: `authorize_query`, `authorize_object`, `authorize_action`。

### C-A2 OntologyService
- **責務**: 型の登録・取得（C-D2 をラップ）。型変更は監査対象。
- **インターフェース**: `register_type`, `get_type`, `list_types`。

### C-A3 RetrievalService
- **責務**: `search_objects`/`get_object`/`traverse_link`/`aggregate`/`semantic_search`(phase2)。PermissionGateway で制約注入 → ObjectStore/VectorStore 実行 → AuditService 記録。
- **インターフェース**: 上記メソッド群。

### C-A4 ActionService
- **責務**: `propose_action`（実行せず提案）, `invoke_action`（承認済のみ writeback）。PermissionGateway + AuditService 必須。
- **インターフェース**: `propose_action`, `invoke_action`。

### C-A5 AuditService
- **責務**: 全操作の構造化記録、監査検索（ガバナンスロール）。アプリは自ログを改変不可（追記専用 sink）。
- **インターフェース**: `record`, `query_events`。

## Ports（インターフェース定義）
- **ObjectStorePort** — 型付きオブジェクトの CRUD・構造化クエリ・集計・リンク探索。
- **VectorStorePort** — 埋め込み登録・意味検索（phase 2）。
- **PolicyStorePort** — ロール別ポリシーのロード。
- **TypeRegistryPort** — 型定義の永続ロード/保存。
- **AuditSinkPort** — 監査イベントの追記・検索（append-only）。
- **AuthenticatorPort** — MCP トークン等から `Principal`/`Role` を解決。

## Outbound Adapters
- **PostgresObjectStore / PostgresPolicyStore / PostgresTypeRegistry / PostgresAuditSink** — PostgreSQL 実装（パラメタライズドクエリ, SECURITY-05; 暗号化/TLS, SECURITY-01）。
- **PgVectorStore** — pgvector 実装（phase 2）。
- **TokenAuthenticator** — トークン検証で Principal/Role を解決（SECURITY-08）。

## Inbound Adapters
- **MCPServerAdapter** — MCP ツールを公開し、認証 → サービス呼び出し。主インターフェース。
- **RESTAdapter (optional)** — 動作確認/管理用。
