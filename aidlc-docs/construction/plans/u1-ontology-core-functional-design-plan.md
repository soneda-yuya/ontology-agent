# Functional Design Plan — U1 Ontology Core

**Unit**: U1 Ontology Core（型システム・レジストリ・OntologyObject・ハイブリッド検証）
**割当ストーリー**: US-F1（型登録）, US-D2（ActionType 定義）, および全 Retrieval/Action の基盤。

> 質問はチャットで収集し、[Answer]: に記録。

---

## Functional Design Questions

### Q-F1: PropertyType がサポートするデータ型の範囲
A) 基本型のみ（string, integer, float, boolean, date, datetime）
B) 基本型 + enum + reference（他オブジェクトへの参照）
C) 上記 + リッチ型（list, json/struct, geo など）
X) Other

[Answer]: B) 基本型 + enum + reference

### Q-F2: 型定義のバージョニング / スキーマ進化
A) バージョニングなし（MVP）— 型は上書き更新。既存オブジェクトとの整合は運用で担保
B) バージョン付き — 型に version を持ち、進化を追跡（複雑だが安全）
X) Other

[Answer]: A) バージョニングなし（MVP）

### Q-F3: LinkType の意味論
A) 単純な有向リンク + cardinality（one-to-one / one-to-many / many-to-many）
B) A + 逆方向ナビゲーション名（例: Flight→Aircraft を Aircraft→Flights からも辿る）
C) B + リンク自身のプロパティ（例: 関係の有効期間）
X) Other

[Answer]: B) 有向リンク + cardinality + 逆方向ナビゲーション名

### Q-F4: ハイブリッド検証（Pydantic）の適用タイミング
A) 書き込み/登録時のみ検証（読み取りは信頼）— 最小・高速
B) 書き込み + 読み取り時も検証（防御的だがコスト増）
X) Other

[Answer]: A) 書き込み/登録時のみ検証

---

## Mandatory Artifacts
- [ ] `construction/u1-ontology-core/functional-design/domain-entities.md`
- [ ] `construction/u1-ontology-core/functional-design/business-logic-model.md`
- [ ] `construction/u1-ontology-core/functional-design/business-rules.md`

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. domain-entities.md（型システムのエンティティ・関係）
- [x] 3. business-logic-model.md（レジストリ・検証・シリアライズのロジック）
- [x] 4. business-rules.md（妥当性・制約 + Testable Properties: PBT-02 round-trip）
- [x] 5. aidlc-state.md 更新
