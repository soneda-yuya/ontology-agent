# Code Generation Plan — U3 Retrieval / RAG

**Unit**: U3（構造化検索・集計・リンク探索・File index。phase2 ベクトル interface）
**Workspace root**: アプリコードは root、docs は aidlc-docs。Greenfield / モジュラーモノリス / レイヤ別。
**この計画が唯一の正。**

## 実装スコープ
- domain/query: `Operator` / `FieldFilter` / `ObjectQuery` / `Granularity` / `AggregateQuery` / `AggregateRow` / `AggregateResult` / `FileMatch` / `SqlSpec` / `AggregateSpec` + **`SqlSpecBuilder`（純関数: filters + AccessConstraint(+principal) → SqlSpec / AggregateSpec）**。
- ports: `ObjectStorePort` 拡張（`query` / `aggregate` 追加, U1 後方互換）、新規 `FileIndexPort`、`VectorStorePort`（phase2 interface のみ）。
- adapters/outbound/postgres: `PostgresObjectStore` に query/aggregate 実装追加、新規 `PostgresFileIndex`（tsvector）。
- services: `RetrievalService`（search_objects / get_object / traverse_link / aggregate / file_search）。
- migrations: `0004_u3_file_index.sql`。
- config: 共通土台を `_build_core` に切り出し、`build_secured_ontology_service` と新規 `build_retrieval_service` で共有（gateway/audit 共用）。
- tests: unit（SqlSpecBuilder 純関数 / RetrievalService フェイク+gateway / IDOR get None / 集計母集団）+ pbt（query round-trip, generators, constraint→SQL）+ integration（query/aggregate/file search vs PostgreSQL）。

## 重要な実装方針
- **Permission-before-IO**（INV-1）: 取得前に authorize_query/authorize_object。
- **Constraint→SQL**: `SqlSpecBuilder` が AccessConstraint を `properties->>'p' = ANY(%s)`（param=principal の属性配列）へ。NONE は service で空返し。
- **IDOR-hide**: get 不許可は None（BR-R3）。
- **集計母集団 = 権限通過行**（BR-R2）。期間は `date_trunc(granularity, (properties->>'t')::timestamptz)`。
- **traverse_link**: LinkType に基づき REFERENCE 関係を辿る（forward=source の REFERENCE プロパティ、reverse=target を search）。各到達を権限フィルタ（BR-R4）。MVP は単純関係を対象。
- **パラメタライズド徹底**（列名/演算子は固定集合, SECURITY-05）。
- 全操作を U5 監査（BR-R7）。
- ObjectStorePort 拡張はメソッド追加のみ（既存実装/フェイク非回帰。フェイクは未使用なら追加不要）。

## ストーリートレーサビリティ
- US-A1/A2（取得・探索）, US-B1/B2/B3（集計）, US-C1/C2（権限フィルタ・IDOR）, US-H2（ファイル/横断検索）

## 生成ステップ
- [ ] Step 1: Business Logic — domain/query モデル + SqlSpecBuilder（純関数）
- [ ] Step 2: Ports — ObjectStorePort 拡張 + FileIndexPort + VectorStorePort(phase2)
- [ ] Step 3: Service — RetrievalService（search/get/traverse/aggregate/file_search）
- [ ] Step 4: Business Logic Unit Testing — SqlSpecBuilder/Service 例示 + PBT（round-trip/generators/constraint整合）
- [ ] Step 5: Repository — PostgresObjectStore.query/aggregate + PostgresFileIndex
- [ ] Step 6: Repository Testing — integration（@integration）
- [ ] Step 7: Database Migration — `migrations/0004_u3_file_index.sql`
- [ ] Step 8: Config/DI — `_build_core` 抽出 + `build_retrieval_service`
- [ ] Step 9: Documentation — `aidlc-docs/construction/u3-retrieval/code/` サマリ
- [ ] Step 10: 回帰確認 — 全 pytest + ruff（ローカルスモーク）

## セキュリティ/PBT 順守
- SECURITY-08（権限通過/IDOR）, 05（parameterized）, 15（空/検証 fail-safe）, 03（監査 PII 非混入は U5）。
- PBT-02（query round-trip）, PBT-07（generators）, constraint→SQL 整合（TP-R2/R3）。
