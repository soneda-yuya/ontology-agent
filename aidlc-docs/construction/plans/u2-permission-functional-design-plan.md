# Functional Design Plan — U2 Permission

**Unit**: U2 Permission（中央集権 PermissionGateway, 行レベル権限, deny-by-default）
**割当ストーリー**: US-C1（全結果の権限フィルタ）, US-C2（越境防止/IDOR）, 横断的に全検索/アクション。
**接続**: U1 の OntologyService の `authorize` フックに実装を注入。

> 質問はチャットで収集し [Answer]: に記録。確定済み: ヘキサゴナル, object-type + 行レベル, fail-closed, PBT-03 invariant 対象。

---

## Functional Design Questions

### Q-P1: 行レベル条件の表現方法
A) 属性マッチ述語 — 「オブジェクトの属性 X が principal の属性 Y に含まれる」（例: object.department ∈ principal.departments）。最小で実用的
B) 所有フィールド方式 — 各 ObjectType に owner 的フィールドを1つ決め、principal と一致で許可
C) 式 DSL — 任意のブール式を評価（強力だが複雑・安全性検討増）
X) Other

[Answer]: A) 属性マッチ述語

### Q-P2: 権限解決の優先順位
A) deny-by-default + 明示deny最優先（明示deny > ロール許可 > 既定拒否）— 推奨
B) 単純許可リスト（許可があれば許可、なければ拒否。deny なし）
X) Other

[Answer]: A) deny-by-default + 明示deny最優先

### Q-P3: 「コンテキスト系は既定共有・業務系は行制限」の表現（Context Hub 要件）
A) ObjectType に共有レベル属性（shared / restricted）を持たせ、shared は行制約なし・restricted は Q-P1 の述語を適用
B) すべて明示ポリシー（共有も restricted も同じ仕組みでポリシーを書く）
X) Other

[Answer]: A) ObjectType に sharing_level（shared/restricted, 既定=restricted）。U1 へ後方互換の追加変更。

### Q-P4: principal（呼び出し主体）の属性源
A) 認証時に解決した属性を principal に載せる（roles + attributes 例: departments/territories）。U6 認証が供給、U2 は受け取って評価
B) U2 が DB から principal 属性を都度引く
X) Other

[Answer]: A) 認証時に principal に載せる

---

## Mandatory Artifacts
- [ ] `construction/u2-permission/functional-design/domain-entities.md`
- [ ] `construction/u2-permission/functional-design/business-logic-model.md`
- [ ] `construction/u2-permission/functional-design/business-rules.md`

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. domain-entities.md（Principal/Role/PermissionPolicy/AccessDecision/AccessConstraint）
- [x] 3. business-logic-model.md（decide / row_constraint / gateway フロー）
- [x] 4. business-rules.md（precedence・fail-closed + Testable Properties: PBT-03 invariant）
- [x] 5. aidlc-state.md 更新
