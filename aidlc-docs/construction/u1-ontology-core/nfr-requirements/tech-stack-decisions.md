# U1 Ontology Core — Tech Stack Decisions

| 項目 | 決定 | 理由 |
|---|---|---|
| 言語 / FW | Python 3.x + Pydantic v2 | 動的 Pydantic 検証（ハイブリッド型）に最適。FastAPI と同系 |
| 永続 | PostgreSQL | プロジェクト標準。JSONB / GIN 索引 / トランザクション |
| オブジェクト格納 | **JSONB 1テーブル**（`objects(object_type, id, properties JSONB, created_at, updated_at)`）| 型追加に DDL 不要（データ駆動と整合）。属性検索は GIN 索引 |
| 型定義格納 | `type_defs(name, kind, definition JSONB, updated_at)` | 型もデータとして保存（serialize/deserialize, PBT-02） |
| TypeRegistry | **起動時全ロード + 変更時インメモリ更新** | 単一プロセス・小規模に最適。将来は LISTEN/NOTIFY へ |
| DB ドライバ | psycopg (v3) または asyncpg（設計で確定） | パラメタライズドクエリ（SECURITY-05） |
| PBT | **Hypothesis** | shrinking・seed 再現・pytest 統合（PBT-08/09） |
| テストランナー | pytest | 例示 + PBT 統合 |
| Lint/型 | ruff + mypy（任意, 推奨） | 品質・保守性 |
| 依存管理 | pyproject.toml + lock | 依存ピン留め（SECURITY-10） |

## スキーマ（U1, 概略）
```sql
CREATE TABLE type_defs (
  name        TEXT PRIMARY KEY,
  kind        TEXT NOT NULL,              -- object | link | action
  definition  JSONB NOT NULL,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE objects (
  object_type TEXT NOT NULL,
  id          TEXT NOT NULL,
  properties  JSONB NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (object_type, id)
);
CREATE INDEX idx_objects_props_gin ON objects USING GIN (properties);
-- 暗号化(SECURITY-01)/接続TLS は Infrastructure Design で確定
```

## ポート実装（U1 が提供）
- `PostgresObjectStore`（ObjectStorePort）— objects テーブル CRUD/クエリ。
- `PostgresTypeRegistry`（TypeRegistryPort）— type_defs ロード/保存。

## Open（後段で確定）
- DB ドライバ（psycopg3 vs asyncpg）と sync/async 方針 → FastAPI 統合時（U6）に整合。
- 暗号化・接続セキュリティ → Infrastructure Design。
