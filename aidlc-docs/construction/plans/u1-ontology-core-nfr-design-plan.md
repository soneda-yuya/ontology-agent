# NFR Design Plan — U1 Ontology Core

**目的**: U1 の NFR 要件をパターン + 論理コンポーネントへ落とす。
NFR 要件（nfr-requirements.md）は確定済み。残る設計選択のみ質問。

> 質問はチャットで収集し [Answer]: に記録。

---

## NFR Design Questions

### Q-ND1: DB 一時エラー（接続断・デッドロック等）の回復性パターン
A) 限定リトライ + 指数バックオフ（一時エラーのみ。上限超過で fail-closed）— 実用的
B) リトライなし・即 fail-closed（最小。PoC 向け）
X) Other

[Answer]: B) リトライなし・即 fail-closed（将来 A へ拡張可）

### Q-ND2: オブジェクト読み取りキャッシュ
A) なし（小規模・p95<100ms は DB+GIN で達成可能。premature optimization 回避）— 推奨
B) ホットオブジェクトの短TTLキャッシュ（将来の最適化として枠だけ用意）
X) Other

[Answer]: A) なし

---

## Mandatory Artifacts
- [ ] `construction/u1-ontology-core/nfr-design/nfr-design-patterns.md`
- [ ] `construction/u1-ontology-core/nfr-design/logical-components.md`

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. nfr-design-patterns.md（回復性/性能/セキュリティ/検証パターン）
- [x] 3. logical-components.md（接続プール・トランザクション境界・レジストリキャッシュ等）
- [x] 4. aidlc-state.md 更新
