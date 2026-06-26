# Application Design Plan — ontology-agent (Mini AIP)

**Purpose**: コンポーネント責務・インターフェース・サービス層・依存関係の高レベル設計。
（詳細ロジックは Functional Design で実施）

> 質問はチャットで収集し、本ファイルの [Answer]: に記録。

---

## Design Questions

### Q-D1: アーキテクチャスタイル
A) レイヤード/DDD 風（domain / service(usecase) / repository / presentation）
B) ヘキサゴナル（Ports & Adapters）— store/vector/LLM/MCP をポートで抽象化し差し替え容易
C) シンプルなモジュール分割（最小レイヤ）
X) Other

[Answer]: B) ヘキサゴナル（Ports & Adapters）

### Q-D2: Ontology 型の定義方式（最重要）
A) データ駆動レジストリ — 型定義を DB/設定に保存し、オブジェクトは汎用表現。型追加でコード変更不要
B) コード定義 Pydantic 型 — 各 ObjectType を Pydantic クラスで定義しレジストリ登録（型安全だが追加にコード必要）
C) ハイブリッド — コアは汎用データ駆動 + 任意で Pydantic スキーマ検証を重ねる
X) Other

[Answer]: C) ハイブリッド

### Q-D3: 権限の強制ポイント
A) 中央集権ゲートウェイ — すべての検索/取得/集計/アクションが単一の Permission モジュールを必ず通過（fail-closed）
B) 各コンポーネントが個別に権限チェック
X) Other

[Answer]: A) 中央集権ゲートウェイ（fail-closed）

### Q-D4: ストア/ベクトルの抽象化
A) ポートで抽象化（ObjectStore / VectorStore インターフェース）— pgvector→他へ差し替え可、テストでモック容易
B) PostgreSQL に直接結合（最小・素朴）
X) Other

[Answer]: A) ポートで抽象化

---

## Mandatory Artifacts (this stage)
- [x] `application-design/components.md`
- [x] `application-design/component-methods.md`
- [x] `application-design/services.md`
- [x] `application-design/component-dependency.md`
- [x] `application-design/application-design.md`（統合）

## Execution Checklist
- [x] 1. 承認されたスタイル/型方式/権限/抽象化を反映
- [x] 2. components.md 生成
- [x] 3. component-methods.md 生成
- [x] 4. services.md 生成
- [x] 5. component-dependency.md 生成（依存マトリクス + データフロー）
- [x] 6. application-design.md に統合
- [x] 7. aidlc-state.md 更新
