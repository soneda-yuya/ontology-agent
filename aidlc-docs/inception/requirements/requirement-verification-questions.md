# Requirements Clarification Questions — ontology-agent (Mini AIP)

> 回答はユーザーとの対話（チャット）で収集し、以下に記録。

> 確定済み前提:
> - スコープ: `Mini AIP = Ontology + RAG + Permission + Action execution + Audit log`
> - スタック: Python (FastAPI + Pydantic)、LLM = Claude
> - ゴール: 設計ドキュメント先行

---

## Question 1
最初に作る Ontology の題材（ドメイン）は？

[Answer]: X) 実ドメイン — 複数運用サービスに対し、CS が自然言語で情報取得。さらに PM / Sales も「プロダクトの方向性・売り方を決める」目的で利用（集計・分析クエリを含む）。題材が増えてもアーキは不変（型はレジストリ登録）。

---

## Question 2
最小データ層には何を使うか？

[Answer]: B) PostgreSQL

---

## Question 3
RAG（検索）の方式はどこまで作るか？

[Answer]: A→B 段階的（設計ゴールは B = 構造化検索 + ベクトル検索。まず構造化、テキスト属性が出たらベクトル追加）

---

## Question 4
権限（Permission）モデルの粒度は？（データ集約前提）

[Answer]: B) オブジェクトタイプ + 行レベル（ロールごとに見える範囲が変わる）

---

## Question 5
Action execution をどこまで実行するか？

[Answer]: A) 読み取り中心 + 提案（ActionType の枠組みは設計するが、実行は人間承認 or 軽い writeback のみ）

---

## Question 6
エージェント層のインターフェースは？

[Answer]: X) MCP サーバーとして公開し、Claude（Code/Desktop）等の AI クライアントから利用。自前のチャット UI / エージェントループは作らない。権限・監査はサーバー側で強制。

---

## Question 7
監査ログの保存先と対象は？

[Answer]: A) PostgreSQL に構造化保存。対象 = クエリ/検索/権限判定/アクションすべて（誰がどの顧客データを見たか追跡可）

---

## Question 8 — Security Extensions
Should security extension rules be enforced for this project?

[Answer]: A) Yes — enforce all SECURITY rules as blocking constraints

---

## Question 9 — Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

[Answer]: B) Partial — pure functions（権限解決・クエリ構築）と serialization round-trip に限定（有効ルール: PBT-02/03/07/08/09）

---

## Supplementary
集計・分析系クエリ（機能別要望件数、セグメント別解約率など）は最初から必要。
→ Ontology の検索に集約（count / group by / 期間集計）を含めて設計する。
