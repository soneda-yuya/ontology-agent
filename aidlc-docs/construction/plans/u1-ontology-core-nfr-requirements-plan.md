# NFR Requirements Plan — U1 Ontology Core

**Unit**: U1 Ontology Core（型システム・レジストリ・OntologyObject・永続）
**目的**: U1 の非機能要件と技術選定を確定。

> 質問はチャットで収集し、[Answer]: に記録。確定済み前提: Python/FastAPI/Pydantic, PostgreSQL, ヘキサゴナル, Security=ON(全blocking), PBT=Partial(Hypothesis)。

---

## NFR Questions

### Q-N1: 想定規模（オブジェクト件数・型数）
A) 小規模（型 〜数十、オブジェクト 〜数十万）— 単一 PostgreSQL で十分
B) 中規模（型 〜数百、オブジェクト 〜数千万）— 索引設計・パーティション考慮
C) 大規模（それ以上）
X) Other

[Answer]: A) 小規模

### Q-N2: オブジェクトの格納方式（ハイブリッド型の永続化）
A) JSONB 1テーブル（object_type + properties JSONB）— 型追加に強く最小。GIN索引で属性検索
B) 型ごとに物理テーブルを動的生成 — 型付き列で高速だが型追加で DDL
C) ハイブリッド（コアは JSONB、ホットな型のみ物理テーブル）
X) Other

[Answer]: A) JSONB 1テーブル

### Q-N3: TypeRegistry のロード戦略
A) 起動時に全ロード + 変更時リロード（インメモリ）— 最小・高速
B) 都度 DB 参照（常に最新だが遅い）
X) Other

[Answer]: A) 起動時全ロード + 変更時リロード（単一プロセス前提。将来は LISTEN/NOTIFY 無効化へ格上げ）

### Q-N4: 検索レイテンシ目標（U1 の get/簡易クエリ）
A) p95 < 100ms（対話用途として十分）
B) p95 < 500ms（緩め）
X) Other

[Answer]: A) p95 < 100ms

### Q-N5: PBT フレームワーク（PBT-09, U1 で round-trip 対象）
A) Hypothesis（Python 標準的・推奨）
X) Other

[Answer]: A) Hypothesis

---

## Mandatory Artifacts
- [ ] `construction/u1-ontology-core/nfr-requirements/nfr-requirements.md`
- [ ] `construction/u1-ontology-core/nfr-requirements/tech-stack-decisions.md`

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. nfr-requirements.md 生成（規模/性能/可用性/セキュリティ/信頼性/保守性）
- [x] 3. tech-stack-decisions.md 生成（永続方式・索引・PBT FW 等）
- [x] 4. aidlc-state.md 更新
