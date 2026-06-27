# NFR Requirements Plan — U2 Permission

**Unit**: U2 Permission（PermissionGateway, 行レベル, deny-by-default）
**継承**: 多くは U1 / shared-infrastructure に準拠（PostgreSQL, in-memory レジストリ方針, p95<100ms, Hypothesis）。
未確定点のみ質問。

> 質問はチャットで収集し [Answer]: に記録。

---

## NFR Questions

### Q-N2P1: ポリシーのロード戦略（PolicyStorePort）
A) 起動時全ロード + 変更時インメモリ更新（U1 TypeRegistry と同方針）— 推奨
B) 都度 DB 参照
X) Other

[Answer]: A) 起動時ロード + 変更時更新

### Q-N2P2: 権限判定のレイテンシ目標（authorize は全リクエストの critical path）
A) 純関数・インメモリで p95 < 5ms（実質オーバーヘッド無視できる）— 推奨
B) p95 < 50ms で十分
X) Other

[Answer]: A) 純関数・インメモリ p95 < 5ms

---

## 継承（質問不要・記録のみ）
- データ: PostgreSQL（policies テーブル）。shared-infrastructure に準拠。
- セキュリティ: SECURITY-08（deny-by-default/IDOR）, 15（fail-closed）, 03/09（PII/詳細非漏洩）。
- テスト: Hypothesis（PBT-03 invariant が U2 の主対象）。
- 規模: 小規模（ロール/ルール数は限定的）。

## Mandatory Artifacts
- [ ] `construction/u2-permission/nfr-requirements/nfr-requirements.md`
- [ ] `construction/u2-permission/nfr-requirements/tech-stack-decisions.md`

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. nfr-requirements.md
- [x] 3. tech-stack-decisions.md
- [x] 4. aidlc-state.md 更新
