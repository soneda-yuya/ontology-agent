# Code Generation Plan — U2 Permission

**Unit**: U2 Permission
**Workspace root**: `/Users/y.soneda/projects/yuya/ontology-agent`（アプリコードは root、docs は aidlc-docs）
**Project type**: Greenfield / モジュラーモノリス / レイヤ別
**この計画が Code Generation の唯一の正。**

## 実装スコープ（U2）
- domain/permission: モデル（Principal, Operation, Effect, AttributePredicate, PermissionRule, AccessDecision, AccessConstraint）+ 純関数 `decide` / `row_constraint` + 例外 `PermissionDenied` + PolicyRegistry（インメモリ）
- **U1 後方互換変更**: `SharingLevel`(SHARED/RESTRICTED) を U1 に追加し、`ObjectType.sharing_level = RESTRICTED`（既定）。round-trip 維持、既存テスト不変。
- ports: `PolicyStorePort`
- adapters/outbound/postgres: `PostgresPolicyStore`
- services: `PermissionGateway`（authorize_object/query/action + `authorize_hook`）
- migrations: `0002_u2_policies.sql`（policies テーブル）
- config: `build_secured_ontology_service`（gateway を U1 OntologyService の authorize に注入）。既存 `build_ontology_service`(no-op) は bootstrap 用に維持。
- tests: unit（decide/row_constraint/gateway/sharing/hook）+ pbt（TP-P1..P4 invariants, generators）+ integration（PostgresPolicyStore）

## 重要な設計判断（実装方針）
- **authorize_hook は型レベルゲート**: operation 写像（register_type→ADMIN, put_object→WRITE, get_object→READ）。principal=None は拒否。deny-by-default + 明示deny。
  - 単一オブジェクト get の**行レベル(IDOR)は U3 RetrievalService が fetch 後に `authorize_object(attrs)` で実施**（U1 の get_object は基盤プリミティブのため）。本ユニットは gateway と純関数を提供。
- **DENY ルールは無条件（型+op レベル）** として実装（TP-P1 を明快に保証）。ALLOW は row_predicate 任意。
- **decide と row_constraint の整合**（TP-P4）を満たすアルゴリズムで実装。
- **bootstrap**: 空 policies では deny-by-default で register_type 不可。`build_secured_ontology_service` 利用時の初期 admin ポリシー投入手順を summary に明記（seed）。既定の no-op ビルダーは維持。

## ストーリートレーサビリティ
- US-C1（全結果の権限フィルタ）→ row_constraint, gateway, decide
- US-C2（越境/IDOR）→ authorize_object（行レベル, U3 で fetch 後適用）/ 型レベルゲート
- PBT-03 invariant（TP-P1/P2/P3/P4）→ tests/pbt

## 生成ステップ（番号順）
- [x] Step 1: U1 後方互換変更 — `SharingLevel` + `ObjectType.sharing_level`（types.py / __init__ / 必要なら generator にも反映）
- [x] Step 2: Business Logic — domain/permission モデル + 例外（`src/mini_aip/domain/permission/`）
- [x] Step 3: Business Logic — `decide` / `row_constraint`（純関数）
- [x] Step 4: Business Logic — PolicyRegistry（インメモリ）
- [x] Step 5: Ports — `PolicyStorePort`
- [x] Step 6: Business Logic Unit Testing — 例示 + PBT（TP-P1..P4, generators）
- [x] Step 7: Repository — `PostgresPolicyStore`（パラメタライズド, JSONB）
- [x] Step 8: Repository Testing — integration（@integration）
- [x] Step 9: Service — `PermissionGateway` + `authorize_hook`（`src/mini_aip/services/permission_gateway.py`）
- [x] Step 10: Database Migration — `migrations/0002_u2_policies.sql`
- [x] Step 11: Config/DI — `build_secured_ontology_service`（authorize 注入）
- [x] Step 12: Documentation — `aidlc-docs/construction/u2-permission/code/` に実装サマリ
- [x] Step 13: 回帰確認 — 既存 U1 テスト含め全 pytest + ruff（ローカルスモーク）

## セキュリティ/PBT 順守
- SECURITY-08（deny-by-default/IDOR）, 15（fail-closed）, 03/09（PII/詳細非漏洩）, 05（パラメタライズド）。
- PBT-03 invariant（TP-P1/P2/P3/P4）, PBT-07 generators, PBT-08 shrinking/seed。
