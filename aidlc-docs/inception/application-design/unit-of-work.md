# Unit of Work — ontology-agent (Mini AIP)

- **Deployment model**: モジュラーモノリス（単一デプロイ可能物 = 1 つの Python アプリ/MCP サーバープロセス）
- **Terminology**: 各ユニット = 単一サービス内の「論理モジュール」
- **Directory organization**: レイヤ別（ヘキサゴナル）。ユニットはレイヤ内のモジュールとして現れる。

## ユニット定義（6）

### U1 Ontology Core
- **責務**: 型システム（PropertyType/ObjectType/LinkType/ActionType）、`OntologyObject`、`TypeRegistry`、ハイブリッド検証。
- **公開**: OntologyService（register/get/list）、TypeRegistryPort、ObjectStorePort（オブジェクト永続）。
- **基盤ユニット**（他が依存）。

### U2 Permission
- **責務**: Principal/Role/PermissionPolicy、解決アルゴリズム（deny優先・deny-by-default）、行レベル制約生成。中央 PermissionGateway。
- **公開**: PermissionGateway、PolicyStorePort。
- **PBT**: `decide()` invariant（PBT-03）。

### U3 Retrieval / RAG
- **責務**: search/get/traverse/aggregate（phase1）、semantic_search（phase2）、**file search（Context Hub 拡張）**。クエリ構築（パラメタライズド）。
- **公開**: RetrievalService、VectorStorePort、**FileIndexPort**。
- 依存: U1（型）、U2（認可）、U5（監査）。

### U4 Action
- **責務**: propose/invoke、承認フロー、前提条件評価、writeback。
- **公開**: ActionService。
- 依存: U1（ActionType）、U2、U5、ObjectStore.write。

### U5 Audit & Activity（Context Hub 拡張で Activity を追加・分離）
- **責務**:
  - Audit: 全イベント構造化記録、監査検索、追記専用（改ざん耐性, ガバナンス閲覧）。
  - **Activity（分離）**: 作業履歴の記録・検索。AIが文脈として読める共有履歴。別ストア・別API・広く読めるポリシー。
- **公開**: AuditService、AuditSinkPort、**ActivityService、ActivityLogPort**。
- 依存: U2（認可）。

### U6 MCP / API / CLI（Context Hub 拡張で 3 経路を一級化）
- **責務**: **MCP + HTTP API + CLI** の3経路を公開、認証（Authenticator: AI=ユーザー代理）、サービスへのディスパッチ。
- **公開**: MCPServerAdapter、**HTTPApiAdapter、CLIAdapter**、AuthenticatorPort。
- 依存: U2〜U5 のサービス。

## 開発順序（依存順）
```
U1 Ontology → U2 Permission → U5 Audit → U3 Retrieval → U4 Action → U6 MCP
```

## コード組織戦略（Greenfield, レイヤ別）
```
ontology-agent/
├── pyproject.toml                 # 依存ピン留め + lock (SECURITY-10)
├── src/mini_aip/
│   ├── domain/                    # 純粋core（U1-U6 のモデル）
│   │   ├── ontology/              # U1
│   │   ├── permission/            # U2
│   │   ├── query/                 # U3 のクエリモデル
│   │   ├── action/                # U4
│   │   └── audit/                 # U5
│   ├── ports/                     # Protocol 群（ObjectStore/Vector/Policy/TypeRegistry/AuditSink/Authenticator）
│   ├── services/                  # アプリ層
│   │   ├── permission_gateway.py  # U2 中央ゲート
│   │   ├── ontology_service.py    # U1
│   │   ├── retrieval_service.py   # U3
│   │   ├── action_service.py      # U4
│   │   └── audit_service.py       # U5
│   ├── adapters/
│   │   ├── inbound/
│   │   │   ├── mcp/                # U6 MCP サーバー
│   │   │   └── rest/              # 任意
│   │   └── outbound/
│   │       ├── postgres/          # ObjectStore/Policy/TypeRegistry/AuditSink 実装
│   │       └── pgvector/          # VectorStore（phase2）
│   └── config/                    # 設定・DI 組み立て
├── migrations/                    # DB スキーマ
└── tests/
    ├── unit/                      # 例示テスト
    ├── pbt/                       # property-based（Hypothesis）
    └── integration/               # store/MCP 結合
```

- **DI**: `config/` で Port 実装を組み立て（テストではモック注入）。
- **ユニット境界**: ドメインは domain/<unit>、サービスは services/、ポートは ports/。ユニット間はサービス/ポート interface 経由のみ（直接 import 制限）。
