# Requirements — ontology-agent (Mini AIP)

## 1. Intent Analysis

| 項目 | 内容 |
|---|---|
| **User request** | 企業の内部データ・業務フローに LLM/AIエージェントを安全に接続する Palantir AIP の最小版を作る。`Mini AIP = Ontology + RAG + Permission + Action execution + Audit log`。設計ドキュメント先行。 |
| **Request type** | New Project (Greenfield) |
| **Scope estimate** | System-wide（複数レイヤ: データ層・Ontology層・RAG・権限・アクション・監査・MCP I/F） |
| **Complexity estimate** | Complex（マルチペルソナ権限、意味検索、ガバナンス、MCP統合） |
| **Requirements depth** | Standard〜Comprehensive |

## 2. Product Context

複数の運用中サービスに関する情報を、**自然言語で安全に取得・分析**できる社内基盤。
LLM はクライアント側（Claude Code/Desktop 等）が担い、本システムは **MCP サーバー**として
Ontology・検索・権限・アクション・監査を提供する。

### Personas

| ロール | 主な目的 | 代表的クエリ |
|---|---|---|
| **CS** | 個別顧客・サービスの照会 | 「顧客Xの直近の問い合わせと契約状況は？」 |
| **PM** | プロダクト方向性の判断 | 「サービスAで最も要望が多い機能は？」（集計） |
| **Sales** | 売り方の判断 | 「解約率が高い顧客セグメントは？」（集計） |

→ ロールにより閲覧可能範囲が異なる（**行レベル権限**が必須）。

## 3. Architecture Overview (logical)

```
[ Claude Code / Desktop ]  ← エージェント層（LLM）。本プロジェクト範囲外
        │ MCP (tool calling) + 認証トークン（ユーザー/ロール識別）
        ▼
┌──────────────────────────────────────────────┐
│  Mini AIP (MCP Server / FastAPI)             │
│   Tools: search_objects / get_object /        │
│          traverse_link / aggregate /          │
│          propose_action / invoke_action       │
│   ── 各呼び出しで 権限チェック → 監査記録 ──    │
├──────────────────────────────────────────────┤
│  Ontology 層（ObjectType/LinkType/ActionType）│
│   型はレジストリ登録（題材追加で不変）          │
├──────────────────────────────────────────────┤
│  RAG: 構造化検索（A）→ +ベクトル検索（B）       │
├──────────────────────────────────────────────┤
│  Permission（object-type + row-level）         │
│  Audit log（全イベント構造化）                  │
├──────────────────────────────────────────────┤
│  Data 層: PostgreSQL（集約済みデータ）          │
└──────────────────────────────────────────────┘
```

## 4. Functional Requirements

### FR-1 Ontology
- FR-1.1 `ObjectType` / `LinkType` / `ActionType` / `PropertyType` を**レジストリにデータとして登録**でき、題材追加で他レイヤのコード変更が不要であること。
- FR-1.2 各 ObjectType はプロパティ（型・必須・PII フラグ）とリンク（cardinality）を持つ。
- FR-1.3 オブジェクト実体は PostgreSQL に永続化され、型定義と対応する。

### FR-2 RAG / Retrieval
- FR-2.1 **構造化検索（フェーズ1）**: 属性フィルタ・リンク探索でオブジェクトを取得。
- FR-2.2 **集計クエリ（フェーズ1から必須）**: count / group by / 期間集計（PM/Sales 向け分析）。
- FR-2.3 **ベクトル検索（フェーズ2）**: オブジェクト付随テキストの埋め込みによる意味検索。設計ゴール。
- FR-2.4 検索結果は常に権限フィルタ通過後のもののみ返す。

### FR-3 Permission
- FR-3.1 **object-type レベル**: ロールごとに型単位の閲覧可否。
- FR-3.2 **row レベル**: 条件付きフィルタ（例: 自部門/担当サービスの行のみ）。
- FR-3.3 **deny-by-default / fail-closed**: 明示許可がなければ拒否。エラー時も拒否側に倒す。
- FR-3.4 権限は**サーバー側で強制**（クライアント=Claude は信頼境界外）。

### FR-4 Action execution
- FR-4.1 ActionType の枠組みを設計（入力スキーマ・前提条件・効果）。
- FR-4.2 既定は**読み取り中心 + 提案**: 変更は提案として返し、実行は人間承認または限定的 writeback。
- FR-4.3 アクション実行は権限チェックと監査記録を伴う。

### FR-5 Audit log
- FR-5.1 クエリ/検索/権限判定/アクションの**全イベント**を PostgreSQL に構造化保存。
- FR-5.2 各レコードに: actor（誰）, role, timestamp, 操作種別, 対象オブジェクト/型, 権限判定結果。
- FR-5.3 「誰がどの顧客データを参照したか」を追跡可能。
- FR-5.4 監査ログは追記専用扱い（アプリが自身のログを改変/削除できない）。

### FR-6 MCP Interface
- FR-6.1 MCP サーバーとして検索/取得/探索/集計/アクションをツール公開。
- FR-6.2 呼び出しユーザー/ロールを認証で識別し、権限・監査に用いる。

## 5. Non-Functional Requirements

| ID | 区分 | 要件 |
|---|---|---|
| NFR-1 | 言語/FW | Python + FastAPI + Pydantic |
| NFR-2 | データ | PostgreSQL（集約データ。ベクトルは pgvector 等を想定、設計時に確定） |
| NFR-3 | LLM | クライアント側 Claude（MCP 経由）。本体に LLM 推論ループは持たない |
| NFR-4 | セキュリティ | **Security Baseline 拡張 = 有効（全15ルール blocking）** |
| NFR-5 | テスト | **PBT 拡張 = Partial（PBT-02/03/07/08/09）**。フレームワーク: Hypothesis |
| NFR-6 | 拡張性 | 題材（ObjectType）追加で他レイヤ不変 |
| NFR-7 | 監査性 | 全アクセス追跡・改ざん耐性 |

## 6. Key Decisions (from clarification)

1. ドメイン = 実ユースケース（マルチサービス × マルチペルソナの自然言語情報取得・分析）
2. データは**集約前提**。外部DB/Storage への直接アクセス制御は本MVP範囲外（将来のコネクタ拡張）
3. RAG は **A→B 段階**（構造化 → ベクトル）。集計は最初から必須
4. 権限 = object-type + row-level、サーバー側強制
5. アクション = 読み取り中心 + 提案
6. I/F = **MCP サーバー**（自前UI不要）
7. 監査 = DB構造化・全件
8. Security = Yes、PBT = Partial

## 7. Assumptions

- 各サービスのデータは事前に PostgreSQL へ取り込み済み（または取り込みパイプラインは別途）。
- ユーザー認証基盤（誰がどのロールか）は MCP サーバーが検証できる前提（具体方式は設計で確定）。
- ベクトル検索の埋め込みモデル/ストアは設計フェーズで選定（pgvector 有力）。

## 8. Out of Scope (MVP)

- 外部DB/Storage へのフェデレーテッドアクセスと、その権限マッピング。
- 自前のチャットUI・LLM推論オーケストレーション。
- フル機能の外部副作用アクション（通知/ジョブ起動は将来、モック可）。
- 本番デプロイ/監視（AI-DLC OPERATIONS フェーズはプレースホルダ）。

## 9. Open Items (設計フェーズで確定)

- O-1 ユーザー/ロール認証の具体方式（MCP のトークン/ヘッダ設計）。
- O-2 ベクトルストアの選定（pgvector vs 外部）。
- O-3 行レベル権限の表現方法（ポリシー式 / 属性ベース）。
- O-4 ActionType の承認フロー詳細。

## 10. Security & PBT Compliance (Requirements stage)

**Security Baseline** — 本ステージ（要件）で評価可能な範囲:
- SECURITY-05/08（入力検証・アプリ層認可）: 要件に明記（FR-3, FR-6）→ 設計で具体化 ✅ 方針記載済
- SECURITY-03/14（ログ・監査・改ざん耐性）: FR-5 に反映 ✅
- SECURITY-01（保存/転送暗号化）, 06/07（最小権限/ネットワーク）, 09–13/15: 設計・実装ステージで評価（現時点 N/A: 対象成果物未生成）
- 本ステージにブロッキング所見なし。

**PBT (Partial)** — PBT-01 は Functional Design で実施予定。要件段階で対象成果物なし → 現時点 N/A。
