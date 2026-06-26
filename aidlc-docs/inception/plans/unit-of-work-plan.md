# Unit of Work Plan — ontology-agent (Mini AIP)

**Purpose**: システムを開発単位（ユニット）へ分解。ストーリーをユニットに割当。
**前提**: Greenfield / ヘキサゴナル / 単一プロセス（プレリミナリ 6 ユニット: U1-U6）。

> 質問はチャットで収集し、本ファイルの [Answer]: に記録。

---

## Decomposition Questions

### Q-U1: デプロイモデル
A) モジュラーモノリス（単一デプロイ可能物。論理モジュールで分割）— 最小・運用簡単
B) マイクロサービス（ユニットごとに独立デプロイ）— 過剰になりがち
X) Other

[Answer]: A) モジュラーモノリス（単一デプロイ可能物）

### Q-U2: ディレクトリ構成（Greenfield）
A) レイヤ別（domain / ports / services / adapters）— ヘキサゴナルの定石。共有ポートを一箇所に
B) ユニット別（features/<unit>/ 各々に domain+service）— per-unit 開発に直感的だが共有が散る
C) ハイブリッド（トップはレイヤ別 + services/adapters 内をユニットで分割）
X) Other

[Answer]: A) レイヤ別

### Q-U3: ユニット粒度
A) 6 ユニットを維持（U1 Ontology / U2 Permission / U3 Retrieval・RAG / U4 Action / U5 Audit / U6 MCP・API）
B) 集約して 3〜4 に（例: Core[Ontology+Permission] / Retrieval / Action+Audit / MCP）
X) Other

[Answer]: A) 6 ユニット維持

### Q-U4: ユニット開発順序（依存上の優先）
A) 依存順（U1 Ontology → U2 Permission → U5 Audit → U3 Retrieval → U4 Action → U6 MCP）
B) ユーザー価値順（まず検索系を縦に通す）
X) Other

[Answer]: A) 依存順

---

## Mandatory Artifacts (this stage)
- [x] `application-design/unit-of-work.md`（ユニット定義 + コード組織戦略[Greenfield]）
- [x] `application-design/unit-of-work-dependency.md`（依存マトリクス）
- [x] `application-design/unit-of-work-story-map.md`（ストーリー→ユニット）

## Execution Checklist (Part 2)
- [x] 1. 承認されたモデル/構成/粒度/順序を反映
- [x] 2. unit-of-work.md 生成
- [x] 3. unit-of-work-dependency.md 生成
- [x] 4. unit-of-work-story-map.md 生成（全ストーリー割当を検証）
- [x] 5. aidlc-state.md 更新
