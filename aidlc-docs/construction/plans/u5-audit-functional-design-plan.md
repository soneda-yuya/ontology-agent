# Functional Design Plan — U5 Audit & Activity

**Unit**: U5（Audit=改ざん不可の証跡 / Activity=共有作業履歴。2つを分離）
**割当ストーリー**: US-E1（全件記録・追記専用）, US-E2（監査検索）, US-H1/H4（Activity 追記・文脈読取）。
**接続**: U1 OntologyService / U2 PermissionGateway の `audit` フックに実装を注入。

> 確定: Audit と Activity は別ストア・別API。PII 値は記録しない（object_type/id/op 等の参照のみ, SECURITY-03/14）。
> 質問はチャットで収集し [Answer]: に記録。

---

## Functional Design Questions

### Q-A1: Audit の改ざん耐性レベル
A) アプリ追記専用（record のみ。update/delete API なし）+ DB 権限で UPDATE/DELETE を付与しない — 実用的な最小
B) A + ハッシュチェーン（各レコードに前レコードのハッシュ。改ざん検知可能）
X) Other

[Answer]: A) 追記専用 + DB 権限

### Q-A2: Activity log に記録する範囲
A) 重要アクションのみ（作業内容の保存・状態変更・アクション実行など「文脈として有用」なもの）
B) 全操作（読み取り含む全て）— Audit とほぼ同内容になり冗長
X) Other

[Answer]: A) 重要アクションのみ

### Q-A3: Activity の読み取り可視性
A) PermissionGateway 経由（Activity 対象型を SHARED 扱い＝チーム既定共有で広く読める。機微は除外）— 推奨
B) 認証済みなら無制限（権限を通さない）
X) Other

[Answer]: A) PermissionGateway 経由（SHARED 扱い）

---

## Mandatory Artifacts
- [ ] `construction/u5-audit/functional-design/domain-entities.md`
- [ ] `construction/u5-audit/functional-design/business-logic-model.md`
- [ ] `construction/u5-audit/functional-design/business-rules.md`

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. domain-entities.md（AuditEvent / ActivityEvent / フィルタ）
- [x] 3. business-logic-model.md（record / query / フック適合・PII除外）
- [x] 4. business-rules.md（追記専用・改ざん耐性・PII + Testable Properties）
- [x] 5. aidlc-state.md 更新
