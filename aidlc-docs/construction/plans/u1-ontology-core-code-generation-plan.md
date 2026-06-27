# Code Generation Plan — U1 Ontology Core

**Unit**: U1 Ontology Core
**Workspace root**: `/Users/y.soneda/projects/yuya/ontology-agent`（アプリコードは root。docs は aidlc-docs のみ）
**Project type**: Greenfield / モジュラーモノリス / レイヤ別（`src/mini_aip/...`）
**この計画が Code Generation の唯一の正（single source of truth）。**

## 実装スコープ（U1 が提供）
- 型システム（PropertyType/ObjectType/LinkType/ActionType/OntologyObject/enums）
- serialize/deserialize（PBT-02 round-trip）
- 検証（型定義検証・動的Pydanticでのオブジェクト検証・余剰拒否）、PiiRedactor、例外
- TypeRegistry（インメモリ：起動時ロード + register 時更新）
- Ports: ObjectStorePort / TypeRegistryPort
- Outbound adapters: PostgresObjectStore / PostgresTypeRegistry + 接続/UnitOfWork
- OntologyService（register_type / get_type / list_types / put_object / get_object）
  - 権限(U2)・監査(U5)は未実装のため**注入フック（既定 no-op）**を設け、後でワイヤリング
- DB マイグレーション（type_defs / objects + GIN）
- テスト: 例示（unit）+ PBT（Hypothesis: round-trip / generators）
- 設定/DI 雛形、ローカル開発用 deploy 雛形（docker-compose / Dockerfile / .env.example）

## 依存・前提
- 依存ユニット: なし（U1 は基盤）。U2/U5 は未実装のため OntologyService は no-op フックで自立。
- 設計参照: functional-design / nfr-requirements / nfr-design / infrastructure-design（U1）。

## ストーリートレーサビリティ
- US-F1（ObjectType/LinkType 登録）→ Steps 2,3,4,7,9,10
- US-D2（ActionType 定義）→ Steps 2,3,9（定義のみ。実行は U4）
- US-F1-AC3 / TP-1/TP-2（round-trip, PBT-02）→ Steps 2,6
- US-H1 の保存基盤（put_object）→ Steps 9,7（共有メモリ型も型登録のみで成立）

## 生成ステップ（番号順）
- [x] Step 1: Project Structure Setup — `pyproject.toml`（依存ピン留め/lock方針, Hypothesis/pytest/pydantic/psycopg）、`src/mini_aip/` 雛形、`.env.example`、`README` は後回し
- [x] Step 2: Business Logic — domain/ontology モデル + enums + serialize/deserialize（`src/mini_aip/domain/ontology/`）
- [x] Step 3: Business Logic — 検証（DynamicModelFactory・validate_type_def・validate_object）、PiiRedactor、例外（`domain/ontology/`）
- [x] Step 4: Business Logic — TypeRegistry（インメモリ）（`domain/ontology/registry.py`）
- [x] Step 5: Ports — `ObjectStorePort` / `TypeRegistryPort`（`src/mini_aip/ports/`）
- [x] Step 6: Business Logic Unit Testing — 例示テスト + PBT（round-trip TP-1/TP-2, generators PBT-07）（`tests/unit/`, `tests/pbt/`）
- [x] Step 7: Repository Layer — `PostgresObjectStore` / `PostgresTypeRegistry` + 接続/UnitOfWork（`src/mini_aip/adapters/outbound/postgres/`）
- [x] Step 8: Repository Layer Unit Testing — リポジトリのテスト（DB 接続が要るものは Build&Test/integration で実行する旨を明記）
- [x] Step 9: Service Layer — `OntologyService`（register/get/list/put/get_object、権限・監査は注入フック既定no-op）（`src/mini_aip/services/ontology_service.py`）
- [x] Step 10: Database Migration — `migrations/0001_u1_ontology.sql`（type_defs / objects / GIN）
- [x] Step 11: Config/DI — `src/mini_aip/config/`（ポート実装の組み立て、env 読み込み）
- [x] Step 12: Deployment Artifacts — `docker-compose.yml`（dev PostgreSQL）, `Dockerfile`, `.env.example`
- [x] Step 13: Documentation — `aidlc-docs/construction/u1-ontology-core/code/` に実装サマリ（markdown）

## セキュリティ/PBT 順守（生成時）
- パラメタライズドクエリ（SECURITY-05）、PII 非ログ（SECURITY-03）、fail-closed（SECURITY-15）、例外は内部詳細を出さない（SECURITY-09）、依存ピン留め（SECURITY-10）。
- PBT: round-trip（PBT-02）、generators（PBT-07）、shrinking/seed（PBT-08）。例示テストと分離（PBT-10）。

## 注記
- テストの「実行」は Build & Test フェーズ。本ステージは生成まで。
- 権限/監査の実ワイヤリングは U2/U5 実装時に OntologyService へ注入。
