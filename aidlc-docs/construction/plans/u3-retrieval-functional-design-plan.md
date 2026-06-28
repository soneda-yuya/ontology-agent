# Functional Design Plan — U3 Retrieval / RAG

**Unit**: U3（構造化検索・集計・リンク探索・File index。phase2 でベクトル）
**割当ストーリー**: US-A1/A2（取得・探索）, US-B1/B2/B3（集計）, US-C1/C2（権限フィルタ・IDOR）, US-H2/H3（横断検索・ファイル）。
**統合**: U1 ObjectStore、U2 PermissionGateway（row_constraint→SQL / authorize_object）、U5 監査記録。

> 質問はチャットで収集し [Answer]: に記録。確定: A→B 段階（phase1=構造化+集計、ベクトルは後段）。

---

## Functional Design Questions

### Q-R1: 検索フィルタの表現範囲（属性フィルタ）
A) 等価のみ（property == value / property ∈ values）— 最小
B) 等価 + 比較/範囲（>, <, between）+ 部分一致（contains）— 実用的
C) B + 複合論理（AND/OR ネスト）
X) Other

[Answer]: B) 等価 + 比較/範囲 + 部分一致

### Q-R2: 集計（aggregate）の範囲
A) count + group_by（プロパティ別件数）— 最小
B) A + 期間バケット（日/週/月の時系列）— PM/Sales のトレンド対応（US-B3）
X) Other

[Answer]: B) count + group_by + 期間バケット

### Q-R3: File index の方式
A) 専用 FileIndexPort + file_index テーブル（PostgreSQL 全文検索 tsvector）— ファイル本文検索に最適化
B) ファイルを Ontology オブジェクト（File 型）として登録し ObjectStore で扱う — 権限/検索を再利用、ただし本文検索は簡易
X) Other

[Answer]: A) 専用 FileIndexPort + 全文検索

### Q-R4: 単一 get で権限違反（行レベル）時の挙動（US-C2 IDOR）
A) None を返す（存在を秘匿。「無い」と区別不能）— 推奨（情報漏洩防止）
B) PermissionDenied を投げる（明示的に拒否）
X) Other

[Answer]: A) None を返す

---

## Mandatory Artifacts
- [ ] `construction/u3-retrieval/functional-design/domain-entities.md`
- [ ] `construction/u3-retrieval/functional-design/business-logic-model.md`
- [ ] `construction/u3-retrieval/functional-design/business-rules.md`

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. domain-entities.md（ObjectQuery / AggregateQuery / AggregateResult / FileMatch / SqlSpec）
- [x] 3. business-logic-model.md（search/get/traverse/aggregate/file-search、row_constraint→SQL、監査）
- [x] 4. business-rules.md（権限フィルタ徹底・IDOR・集計母集団 + Testable Properties）
- [x] 5. aidlc-state.md 更新
