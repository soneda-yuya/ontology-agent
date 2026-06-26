# U1 Ontology Core — Business Rules & Testable Properties

## Business Rules

### 型定義の妥当性（validate_type_def）
- BR-1 `name` は非空・グローバル一意（種別内）。命名は識別子規則（英数 + `_`）。
- BR-2 ObjectType は `properties` に少なくとも `id_property` を含む。
- BR-3 `title_property` / `text_properties` は `properties` に存在するもののみ。
- BR-4 PropertyType: `data_type=ENUM` なら `enum_values` 非空。`data_type=REFERENCE` なら `ref_object_type` 必須。
- BR-5 LinkType: `source_type`/`target_type` は登録済 ObjectType。`inverse_name` は source 側の他リンク名/プロパティ名と衝突しない。
- BR-6 ActionType: `target_type` 登録済、`input_schema` の各 PropertyType が BR-4 を満たす。

### オブジェクト整合（validate_object, 書き込み時のみ）
- BR-7 `object_type` は登録済。
- BR-8 全 `required` プロパティが存在し非 null。
- BR-9 値は `data_type` に整合（STRING:str, INTEGER:int, FLOAT:int|float, BOOLEAN:bool, DATE/DATETIME:ISO8601 文字列, ENUM:enum_values 内, REFERENCE:文字列 id）。
- BR-10 余剰プロパティ（型定義にない）は拒否（推測で通さない）。

### PII / セキュリティ
- BR-11 `is_pii=True` のプロパティ値はログ・エラーメッセージに出力しない（SECURITY-03）。
- BR-12 検証失敗時は保存・実行しない（fail-closed, SECURITY-15）。

## Testable Properties（PBT-01 識別 / Partial で PBT-02・07 は enforced）

| ID | カテゴリ | プロパティ | 対応ルール |
|---|---|---|---|
| TP-1 | Round-trip (PBT-02) | `deserialize_type(serialize_type(t)) == t` 全 valid TypeDef t | L4 |
| TP-2 | Round-trip (PBT-02) | `deserialize_object(serialize_object(o)) == o` 全 valid OntologyObject o | L4 |
| TP-3 | Invariant (PBT-03, advisory@U1) | `validate_object` は BR-10 違反（余剰プロパティ）を常に拒否 | BR-10 |
| TP-4 | Invariant | 登録成功した型は直後に `get_type` で同一取得できる | L1/L2 |

### Generators（PBT-07, enforced）
- `gen_property_type()` — data_type に応じ enum_values/ref_object_type を整合生成。
- `gen_object_type()` — 1+ プロパティ、id_property を含む整合生成。
- `gen_ontology_object(object_type)` — 型に整合する値を生成（境界値含む: 空文字、最大長、Unicode）。

> 注: U1 で enforced な PBT は PBT-02（round-trip: TP-1/TP-2）と PBT-07（generators）。
> PBT-03 invariant の主対象は U2 Permission（`decide()`）。

## Compliance Summary (Functional Design — U1)
- **PBT-01**（プロパティ識別, advisory@Partial）: 実施済（上表）。
- **PBT-02/07**（enforced）: 設計に Testable Properties / generators を明記 → Code Generation で実装。✅ 非ブロッキング。
- **Security**: SECURITY-03（PII 非ログ, BR-11）, SECURITY-05（書き込み検証, BR-7〜10）, SECURITY-15（fail-closed, BR-12）を設計に反映。暗号化/ネットワーク等は Infra Design で評価（現時点 N/A）。ブロッキング所見なし。
