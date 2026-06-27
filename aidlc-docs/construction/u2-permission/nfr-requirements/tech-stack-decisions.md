# U2 Permission — Tech Stack Decisions

U1 / shared-infrastructure を継承。U2 固有のみ記載。

| 項目 | 決定 | 理由 |
|---|---|---|
| 言語 / FW | Python + Pydantic v2（U1 共通） | Principal/Rule/Policy を Pydantic で表現 |
| 判定ロジック | **純関数**（decide / row_constraint） | テスト容易・高速・PBT 対象 |
| ポリシー格納 | PostgreSQL `policies` テーブル（JSONB ルール） | shared PostgreSQL を共有 |
| ポリシーロード | **起動時 load_all + 変更時インメモリ更新** | U1 TypeRegistry と同方針 |
| PBT | Hypothesis（共通） | PBT-03 invariant / PBT-07 generators |

## スキーマ（U2, 概略）
```sql
CREATE TABLE IF NOT EXISTS policies (
  id          TEXT PRIMARY KEY,         -- ルールID
  role        TEXT NOT NULL,
  object_type TEXT NOT NULL,            -- '*' 可
  operation   TEXT NOT NULL,            -- read | write | admin
  effect      TEXT NOT NULL,            -- allow | deny
  row_predicate JSONB,                  -- {object_property, principal_attribute} | null
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## ポート / 新規
- `PolicyStorePort`（load_all / save）— outbound adapter は PostgresPolicyStore。
- `PermissionGateway`（services）— decide/row_constraint を包み、U1 へ `authorize_hook` を供給。

## U1 への後方互換変更（NFR 観点）
- `ObjectType.sharing_level: SharingLevel = RESTRICTED` 追加。既定値ありで round-trip 維持、既存データは RESTRICTED 扱い（安全側）。

## Open（後段）
- principal の属性供給（U6 認証）。U2 は受領して評価。
