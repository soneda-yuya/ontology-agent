# U3 Retrieval / RAG — Business Rules & Testable Properties

## Business Rules
- BR-R1 **権限フィルタ徹底**: search/aggregate/traverse/file は必ず PermissionGateway を通過し、通過分のみ返す（US-C1, INV-1）。
- BR-R2 **集計母集団 = 権限通過行のみ**（US-B1-AC2 / US-B2-AC2）。権限外は count に含めない。
- BR-R3 **IDOR 秘匿**: 単一 get が行レベルで不許可なら None（存在を漏らさない, US-C2, R4）。
- BR-R4 **traverse 除外**: 探索経路上の不許可オブジェクトは結果から除外し経路を破綻させない（US-A2-AC2）。
- BR-R5 **空権限 = 空結果**: AccessConstraint=NONE は空（エラーにしない, US-A1-AC3）。
- BR-R6 **パラメタライズド徹底**: フィルタ値・制約値はすべてバインド（SECURITY-05）。
- BR-R7 **全操作を監査**: 取得/検索/集計/ファイルは U5 に記録（許可/空/拒否含む）。
- BR-R8 **不正な期間/入力は安全に検証エラー**（US-B3-AC2, SECURITY-05/15）。

## Testable Properties（PBT-01。Partial で PBT-02/07 enforced。整合は PBT-03 系）
| ID | カテゴリ | プロパティ | 対応 |
|---|---|---|---|
| TP-R1 | Round-trip (PBT-02) | ObjectQuery / AggregateQuery の serialize/deserialize 一致 | 永続/転送 |
| TP-R2 | Invariant | build_sql は AccessConstraint=NONE のとき常に「空集合」を意味する（呼び出しは空返し） | BR-R5 |
| TP-R3 | Invariant | PREDICATES 制約下で生成 SQL は、いずれの述語も満たさない行を選ばない（モデル検証 = decide 整合, TP-P4 と接続） | BR-R1/R2 |
| TP-R4 | Consistency | get_object: 権限不許可 → None（許可 → 同一オブジェクト） | BR-R3 |

### Generators（PBT-07）
- `gen_object_query()` / `gen_aggregate_query()` / `gen_field_filter()` — 型整合・演算子に応じた値。

> 注: 権限 invariant の中核（明示deny→拒否 / decide↔constraint）は U2 で検証済。U3 は「constraint を SQL に正しく反映」する整合（TP-R2/R3）と round-trip（TP-R1）を担う。

## Compliance Summary (Functional Design — U3)
- **Security**: SECURITY-08（権限通過必須/IDOR: BR-R1/R3）, 05（パラメタライズド: BR-R6）, 15（空/検証の fail-safe: BR-R5/R8）, 03（監査に PII 非混入は U5 準拠）。ブロッキングなし。
- **PBT**: round-trip（TP-R1）/ generators / constraint 反映の整合（TP-R2/R3）。
- **統合**: U2 row_constraint→SQL、U1 ObjectStore.query 拡張、U5 監査、（phase2）VectorStorePort。
