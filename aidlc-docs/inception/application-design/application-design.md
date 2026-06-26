# Application Design (Consolidated) — ontology-agent (Mini AIP)

統合ドキュメント。詳細は各専門ドキュメント参照:
[components.md](components.md) / [component-methods.md](component-methods.md) /
[services.md](services.md) / [component-dependency.md](component-dependency.md)

## 設計判断（承認済）
| # | 決定 | 理由 |
|---|---|---|
| D1 | **ヘキサゴナル**（Ports & Adapters） | store/vector/audit/auth を差し替え可能に。段階的 A→B、テスト容易 |
| D2 | **ハイブリッド型方式** | 汎用データ駆動レジストリで題材追加にコード不要 + 任意の Pydantic 検証で安全性 |
| D3 | **中央集権 PermissionGateway**（fail-closed） | 権限漏れ防止・監査一元化。実PII を扱うため最重要 |
| D4 | **ポート抽象化**（ObjectStore/VectorStore 他） | pgvector→他へ差し替え、モックでテスト |

## レイヤ構成（依存は内向き）
1. **Inbound Adapters**: MCPServerAdapter（主）, RESTAdapter（任意）
2. **Application/Services**: PermissionGateway, OntologyService, RetrievalService, ActionService, AuditService
3. **Domain (core)**: Ontology / Query / Permission / Action / Audit モデル（純粋・フレームワーク非依存）
4. **Ports**: ObjectStore / VectorStore / PolicyStore / TypeRegistry / AuditSink / Authenticator
5. **Outbound Adapters**: Postgres 各実装, PgVectorStore(phase2), TokenAuthenticator

## ストーリー → コンポーネント対応
| Story | 主担当コンポーネント |
|---|---|
| US-A1/A2 構造化検索・探索 | RetrievalService + PermissionGateway + ObjectStore |
| US-B1/B2/B3 集計 | RetrievalService.aggregate + PermissionGateway |
| US-C1/C2 権限境界 | PermissionGateway（中央）+ Permission Model |
| US-D1/D2 アクション | ActionService + ActionType（OntologyService） |
| US-E1/E2 監査 | AuditService + AuditSink(append-only) |
| US-F1 型登録 | OntologyService + TypeRegistry |
| US-G1 MCP | MCPServerAdapter + Authenticator |

## ユニット分解（Units Planning で最終確定）
U1 Ontology Core / U2 Permission / U3 Retrieval・RAG / U4 Action / U5 Audit / U6 MCP・API
→ ヘキサゴナルにより、各ユニットは「ドメイン + ポート定義 + サービス」を持ち、アダプタは共有。

## セキュリティ整合（設計レベル, 詳細は NFR Design）
- SECURITY-08 アプリ層認可 → PermissionGateway + Authenticator（deny-by-default）
- SECURITY-05 入力検証 → Query Model 検証 + パラメタライズドクエリ
- SECURITY-11 セキュア設計 → 認可ロジックを単一モジュールに分離（defense in depth）
- SECURITY-14 監査改ざん耐性 → AuditSink を append-only に
- SECURITY-15 fail-closed → INV-4
- SECURITY-01/07 暗号化・ネットワーク → Infrastructure Design（lean）で具体化

## PBT 整合（Partial, 詳細は Functional Design / PBT-01）
- PBT-03 invariant: `decide()` 明示deny → 必ず拒否（US-C1-AC4）
- PBT-02 round-trip: 型定義 serialize/deserialize（US-F1-AC3）
- PBT-07 generator: Principal/Policy/ObjectType のドメインジェネレータ
