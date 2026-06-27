# U2 Permission — Business Rules & Testable Properties

## Business Rules
- BR-P1 **deny-by-default**: 適用される ALLOW が無ければ拒否。
- BR-P2 **明示 DENY 最優先**: 一致する DENY があれば、他の ALLOW より優先して拒否（P2）。
- BR-P3 **SHARED バイパス（READ のみ）**: `sharing_level == SHARED` の型は READ で行制約なし許可。WRITE/ADMIN は通常評価。
- BR-P4 **行述語**: `object[object_property] ∈ principal.attributes[principal_attribute]`。principal に当該属性が無ければ不成立（→その ALLOW は効かない）。
- BR-P5 **principal 欠落は拒否**: principal が None は常に DENY（SECURITY-08 deny-by-default）。
- BR-P6 **fail-closed**: 型不明・評価例外・属性欠落時は拒否（SECURITY-15）。
- BR-P7 **reason に PII 非混入**: AccessDecision.reason / 例外メッセージに属性値や PII を含めない（SECURITY-03/09）。
- BR-P8 **decide と row_constraint の整合**: ある object が READ で `decide`=ALLOW ⇔ その object が `row_constraint` の条件を満たす（同一ポリシーで矛盾しない）。

## Testable Properties（PBT-01。Partial で PBT-03 invariant が enforced）

| ID | カテゴリ | プロパティ | 対応 |
|---|---|---|---|
| TP-P1 | Invariant (PBT-03) | 明示 DENY が適用される (principal, op, type) は、いかなる ALLOW・SHARED 設定でも常に `decide.allowed == False` | BR-P2 |
| TP-P2 | Invariant (PBT-03) | ALLOW ルールが一切無く SHARED でもない型は、任意の principal で `decide` が DENY（deny-by-default） | BR-P1 |
| TP-P3 | Invariant | principal=None は任意入力で常に DENY | BR-P5 |
| TP-P4 | Consistency | READ について、`decide(principal, READ, type, attrs)`=ALLOW ⇔ attrs が `row_constraint(...)` を満たす | BR-P8 |
| TP-P5 | Invariant | reason 文字列に principal.attributes の値が出現しない | BR-P7 |

### Generators（PBT-07）
- `gen_principal()` — roles 0..3、attributes（キー集合からランダム、値は識別子）。None も混ぜる。
- `gen_rule()` / `gen_policy()` — role/object_type/operation/effect/row_predicate を整合生成（DENY と ALLOW を混在）。
- `gen_object_attrs()` — 述語評価対象の属性辞書。

> U2 で enforced な PBT は PBT-03 invariant（TP-P1/P2/P3）と PBT-07 generators。round-trip 対象があれば PBT-02 も（PermissionPolicy serialize）。

## Compliance Summary (Functional Design — U2)
- **PBT-01**: 実施（上表）。PBT-03 invariant（TP-P1/P2/P3）を Code Generation で実装。
- **Security**: SECURITY-08（deny-by-default/IDOR: BR-P1/P5）, SECURITY-15（fail-closed: BR-P6）, SECURITY-03/09（PII/詳細非漏洩: BR-P7）を反映。ブロッキングなし。
- **U1 への影響**: `ObjectType.sharing_level` 追加（後方互換・既定 RESTRICTED）。round-trip 維持。
