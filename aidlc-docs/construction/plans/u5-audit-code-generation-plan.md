# Code Generation Plan — U5 Audit & Activity

**Unit**: U5（Audit=証跡 / Activity=共有履歴）
**Workspace root**: アプリコードは root、docs は aidlc-docs。Greenfield / モジュラーモノリス / レイヤ別。
**この計画が唯一の正。**

## 実装スコープ
- domain/audit: `AuditEvent` / `ActivityEvent` / `AuditFilter` / `ActivityFilter`（Pydantic, round-trip）、`SIGNIFICANT_OPS`。
- ports: `AuditSinkPort`（append/query）, `ActivityLogPort`（append/query）— **mutate/delete を持たない**。
- adapters/outbound/postgres: `PostgresAuditSink` / `PostgresActivityLog`（INSERT/SELECT のみ, parameterized）。
- services: `AuditService`（record 同期/ query=ガバナンス） / `ActivityService`（record 重要のみ / query=SHARED） / `AuditAdapter`（`audit_hook` 提供：dict→AuditEvent、重要なら ActivityEvent も）。
- migrations: `0003_u5_audit.sql`（audit_events / activity_events）。
- config: `build_secured_ontology_service` を拡張し `audit=audit_adapter.audit_hook` を注入。起動時に擬似型 `AuditEvent`(RESTRICTED) / `ActivityEvent`(SHARED) を type_registry に登録（gateway の sharing 解決用、インメモリ）。
- tests: unit（service 認可/record、adapter hook、append-only 構造、PII-free）+ pbt（round-trip TP-AU1, generators, mutate/delete 不在 TP-AU3）+ integration（Postgres sinks）。

## 重要な実装方針
- **timestamp は record 時に付与**（決定性のため domain では受け取り可、未指定なら sink/サービスで付与）。Date.now 同等はアプリ層で。
- **監査記録失敗 → 例外伝播**（呼び出し元の操作不成立, INV-2）。
- **PII 非保持**: AuditEvent/ActivityEvent は type/id/op/decision/action 要約のみ。
- **擬似型登録**: AuditEvent=RESTRICTED（→ガバナンスの allow ルールのみ読める）, ActivityEvent=SHARED（→READ 広く可）。
- U1/U2 への破壊的変更なし（audit フックは既存の注入点）。

## ストーリートレーサビリティ
- US-E1（全件記録・追記専用）→ AuditService.record / AuditAdapter / append-only ports
- US-E2（監査検索）→ AuditService.query（ガバナンス, gateway）
- US-H1/H4（Activity 記録・文脈読取）→ ActivityService

## 生成ステップ
- [x] Step 1: Business Logic — domain/audit モデル + SIGNIFICANT_OPS（`src/mini_aip/domain/audit/`）
- [x] Step 2: Ports — `AuditSinkPort` / `ActivityLogPort`
- [x] Step 3: Service — `AuditService` / `ActivityService` / `AuditAdapter`
- [x] Step 4: Business Logic Unit Testing — service/adapter 例示 + PBT（round-trip / generators / 構造）
- [x] Step 5: Repository — `PostgresAuditSink` / `PostgresActivityLog`
- [x] Step 6: Repository Testing — integration（@integration）
- [x] Step 7: Database Migration — `migrations/0003_u5_audit.sql`
- [x] Step 8: Config/DI — secured builder に audit 注入 + 擬似型登録
- [x] Step 9: Documentation — `aidlc-docs/construction/u5-audit/code/` サマリ
- [x] Step 10: 回帰確認 — 全 pytest + ruff（ローカルスモーク）

## セキュリティ/PBT 順守
- SECURITY-14（追記専用/DB権限/保持）, 03（PII非保持）, 15（監査なき不成立）, 08（検索認可）, 05（parameterized）。
- PBT-02（round-trip TP-AU1）, PBT-07（generators）, 構造不変（TP-AU3）。
