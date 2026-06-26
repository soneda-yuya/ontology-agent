# Story Generation Plan — ontology-agent (Mini AIP)

**Role**: Product Owner
**Purpose**: requirements.md をロール中心のユーザーストーリー（受け入れ基準付き）に変換する方法論と計画。

> 質問はユーザー希望によりチャットで収集し、本ファイルの [Answer]: に記録する。

---

## Planning Questions

### Q-S1: ストーリー分割アプローチ
A) Persona-Based（CS/PM/Sales ごとにグループ化）
B) Feature-Based（Ontology/RAG/Permission/Action/Audit/MCP の機能ごと）
C) Hybrid（Persona × Feature: ロール別ニーズを機能ストーリーにマップ）
D) User Journey-Based（問い合わせ→検索→権限→結果→（提案）の流れ）
X) Other

[Answer]: C) Hybrid（Persona × Feature）

### Q-S2: 受け入れ基準（Acceptance Criteria）の形式
A) Given / When / Then（Gherkin 風。テスト・PBT に落としやすい）
B) チェックリスト（箇条書きの達成条件）
X) Other

[Answer]: A) Given / When / Then

### Q-S3: 含めるペルソナ
A) CS / PM / Sales の3つ
B) 上記 + 運用・ガバナンス担当（Ontology 型登録、権限設定、監査閲覧）
X) Other

[Answer]: B) CS / PM / Sales + 運用・ガバナンス担当

### Q-S4: ストーリーの粒度
A) 中粒度（1ストーリー=1つの明確な価値。設計・テストに十分）
B) エピック+サブストーリー（階層化）
X) Other

[Answer]: A) 中粒度

---

## Mandatory Artifacts (this stage)
- [x] `aidlc-docs/inception/user-stories/personas.md` — ペルソナ（特徴・目的・権限境界）
- [x] `aidlc-docs/inception/user-stories/stories.md` — INVEST 準拠のストーリー + 受け入れ基準
- [x] 各ストーリーにペルソナをマップ
- [x] 行レベル権限・集計・アクション提案のシナリオを網羅

## Execution Checklist (Part 2: Generation)
- [x] 1. 承認された分割アプローチ・形式・ペルソナ・粒度を読み込む
- [x] 2. personas.md を生成（ロールごとの目的・閲覧境界）
- [x] 3. stories.md を生成（ペルソナにマップ、受け入れ基準付き、INVEST 準拠）
- [x] 4. セキュリティ/権限・集計・アクション提案の各シナリオを網羅確認
- [x] 5. aidlc-state.md を更新
