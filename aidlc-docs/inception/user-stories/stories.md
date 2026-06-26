# User Stories — ontology-agent (Mini AIP)

- **分割アプローチ**: Hybrid（Persona × Feature）
- **受け入れ基準**: Given / When / Then
- **粒度**: 中粒度。各ストーリーは INVEST 準拠。
- **ペルソナ**: P1=CS, P2=PM, P3=Sales, P4=Governance（personas.md 参照）

> 記法: 各ストーリーに ID / ペルソナ / Feature / 優先度 を付与。AC = Acceptance Criteria。

---

## Feature A: RAG — 構造化検索・リンク探索

### US-A1（P1 CS / 構造化検索 / Must）
**As** CS担当, **I want** 顧客名やIDから顧客と関連オブジェクト（契約・チケット）を自然言語で取得したい, **so that** 問い合わせに素早く正確に答えられる。
- **AC1** Given 担当サービスの顧客X, When 「顧客Xの契約と直近チケットを見せて」と問い合わせる, Then 顧客Xのオブジェクトと、リンクされた契約・チケットが返る。
- **AC2** Given 担当外の顧客Z, When 同様に問い合わせる, Then 権限により結果に含まれず、その旨が明示される（データ存在を漏らさない）。
- **AC3** Given 該当なし, When 問い合わせる, Then 空結果と理由が返る（エラーで落ちない）。

### US-A2（P1 CS / リンク探索 / Must）
**As** CS担当, **I want** あるオブジェクトから関連オブジェクトをたどりたい（例: チケット→対象サービス→既知障害）, **so that** 文脈を把握できる。
- **AC1** Given チケットT, When 関連をたどる, Then LinkType に従い到達可能な関連オブジェクトのみ返る。
- **AC2** Given 探索経路上に閲覧不可の型/行, When たどる, Then その要素は除外され、経路は破綻しない。

## Feature B: RAG — 集計・分析クエリ

### US-B1（P2 PM / 集計 / Must）
**As** PM, **I want** 機能別の要望件数やカテゴリ別の問い合わせ件数を集計したい, **so that** プロダクトの方向性を判断できる。
- **AC1** Given 期間と group-by キー（機能/カテゴリ）, When 集計を要求, Then count/group-by 結果が返る。
- **AC2** Given 閲覧境界, When 集計, Then 集計対象は閲覧可能な行のみ（境界外は母集団から除外）。
- **AC3** Given 個人特定可能な粒度の要求, When 集計, Then PII を伴う行明細ではなく集計値が返る（PM の境界）。

### US-B2（P3 Sales / セグメント分析 / Must）
**As** Sales, **I want** セグメント別の解約率や契約状況を分析したい, **so that** 売り方・ターゲティングを決められる。
- **AC1** Given セグメント条件（例: プラン別・期間）, When 解約率を要求, Then セグメント別の比率/件数が返る。
- **AC2** Given 担当テリトリ外, When 分析, Then テリトリ外は集計母集団に含まれない。

### US-B3（P2/P3 / 期間トレンド / Should）
**As** PM/Sales, **I want** 指標の期間推移（週次/月次）を見たい, **so that** トレンドを把握できる。
- **AC1** Given 指標と期間粒度, When 推移を要求, Then 時系列の集計が返る。
- **AC2** Given 不正な期間（終了<開始）, When 要求, Then 検証エラーが安全に返る（SECURITY-05/15）。

## Feature C: Permission — 行レベル境界

### US-C1（全ペルソナ / 権限強制 / Must）
**As** システム, **I want** すべての検索・取得・集計結果を呼び出しロールの権限で必ずフィルタしたい, **so that** 見てよいデータだけが返る。
- **AC1** Given 任意のロールR と権限ポリシー, When 任意のクエリ, Then 結果は R が許可された型かつ行のみを含む（deny-by-default）。
- **AC2** Given 明示的 deny, When 当該データを要求, Then グループ等の他許可より deny が優先される。
- **AC3** Given 権限評価中のエラー, When クエリ, Then fail-closed（拒否側に倒す）（SECURITY-15）。
- **AC4**（PBT-03 invariant）任意の (role, data) 組合せで、明示denyがあれば必ず結果に出現しない。

### US-C2（P1 CS / 越境防止 / Must）
**As** CS担当, **I want** 担当外の顧客データに到達できないようにしたい, **so that** 情報漏洩を防げる。
- **AC1** Given 担当外顧客のID直指定, When get_object, Then 認可チェックで拒否（IDOR防止, SECURITY-08）。

## Feature D: Action — 提案と承認

### US-D1（P1 CS / アクション提案 / Must）
**As** CS担当, **I want** チケットのタグ付け・ステータス更新を提案として作成したい, **so that** 人手の手間を減らしつつ安全に運用できる。
- **AC1** Given 対象チケットと変更内容, When propose_action, Then 実行はされず、提案（差分・前提条件）が返る。
- **AC2** Given 承認権限のない呼び出し, When invoke_action, Then 拒否され監査に残る。
- **AC3** Given 承認された提案, When invoke_action, Then writeback が実行され、結果と監査記録が返る。

### US-D2（P4 Governance / アクション定義 / Should）
**As** ガバナンス担当, **I want** ActionType（入力スキーマ・前提条件・効果）を定義したい, **so that** 実行可能な操作を統制できる。
- **AC1** Given ActionType 定義, When 登録, Then 以後その型のアクションが提案/実行可能になる。
- **AC2** Given 不正な入力スキーマ, When 登録, Then 検証エラーで拒否。

## Feature E: Audit log

### US-E1（全ペルソナ / 全件記録 / Must）
**As** システム, **I want** クエリ・検索・権限判定・アクションをすべて構造化記録したい, **so that** 誰がどの顧客データを参照したか追跡できる。
- **AC1** Given 任意の操作, When 実行, Then actor/role/timestamp/操作種別/対象型/権限判定結果が監査に1件記録される。
- **AC2** Given アプリ実行主体, When 監査ログへ, Then 自身のログを改変/削除できない（追記専用, SECURITY-14）。

### US-E2（P4 Governance / 監査閲覧 / Must）
**As** ガバナンス担当, **I want** 監査ログを検索・閲覧したい, **so that** アクセスの妥当性を確認できる。
- **AC1** Given actor/期間/対象型のフィルタ, When 監査検索, Then 該当ログが返る。
- **AC2** Given 業務データ本体, When ガバナンス担当が要求, Then 職務分離により最小限のみ（監査メタデータ中心）。

## Feature F: Ontology 管理

### US-F1（P4 Governance / 型登録 / Must）
**As** ガバナンス担当, **I want** ObjectType/LinkType/PropertyType をレジストリに登録・更新したい, **so that** 題材が増えても他レイヤを変えずに拡張できる。
- **AC1** Given 新しい ObjectType 定義（プロパティ・PIIフラグ・リンク）, When 登録, Then 検索・権限・監査が当該型に対し汎用的に機能する。
- **AC2** Given PII フラグ付きプロパティ, When 定義, Then 権限/ログで PII として扱われる（ログに出さない, SECURITY-03）。
- **AC3**（PBT-02 round-trip）任意の型定義を保存→読込すると元定義と一致する。

## Feature G: MCP インターフェース

### US-G1（全ペルソナ / MCP利用 / Must）
**As** 利用者, **I want** Claude 等の AI クライアントから MCP ツールで問い合わせたい, **so that** 使い慣れた AI 経由で自然言語利用できる。
- **AC1** Given 認証トークン, When MCP ツール呼び出し, Then 呼び出しユーザー/ロールが識別され権限・監査に用いられる。
- **AC2** Given 無効/欠落トークン, When 呼び出し, Then 認証エラーで拒否（deny-by-default, SECURITY-08）。
- **AC3** Given ツール `search_objects`/`get_object`/`traverse_link`/`aggregate`/`propose_action`/`invoke_action`, When 一覧取得, Then 各ツールのスキーマが MCP に公開される。

## Feature H: Context Hub（チーム共有メモリ・拡張）

### US-H1（P5 AIクライアント / 共有メモリ保存 / Must）
**As** ユーザーの代理AI, **I want** 作業内容・メモ・会話・作業セッションを中央ハブに保存したい, **so that** ローカルに留まらずチームで共有できる。
- **AC1** Given 代理ユーザーの認証, When Memory/Note/Conversation を保存, Then ハブに永続し、既定でチーム共有として保存される。
- **AC2** Given 機微フラグ付き内容, When 保存, Then 行レベル権限に従い共有範囲が制限される。
- **AC3** Given 保存操作, When 実行, Then Activity log に追記され、Audit にも記録される。

### US-H2（P5 / 横断検索 / Must）
**As** 代理AI, **I want** 過去の会話・メモ・**ファイル**・プロジェクト情報を自然言語で横断検索したい, **so that** 文脈を素早く再利用できる。
- **AC1** Given クエリ, When 検索, Then メモリ系オブジェクトとファイル索引が統合的に返る（権限通過分のみ）。
- **AC2** Given ファイル索引（FileIndexPort）, When ファイル検索, Then 該当ファイル/断片が返る。

### US-H3（P5 / ユーザー嗜好・ルール取得 / Should）
**As** 代理AI, **I want** ユーザーの好み・ルールを取得したい, **so that** それに沿って振る舞える。
- **AC1** Given Preference/Rule オブジェクト, When 取得, Then 代理ユーザーに紐づく設定が返る。

### US-H4（P5 / Activity 文脈読取 / Should）
**As** 代理AI, **I want** 他AI/ユーザーの作業履歴（Activity log）を文脈として読みたい, **so that** チームの直近の動きを踏まえられる。
- **AC1** Given Activity log, When 読取, Then 共有ポリシーに従い作業履歴が返る（Audit 証跡とは別API）。
- **AC2** Activity と Audit は別ストア・別アクセス（US-E1/E2 と分離）。

### US-H5（全ペルソナ / 3経路アクセス / Must）
**As** 利用者/代理AI, **I want** MCP・HTTP API・CLI のいずれからもアクセスしたい, **so that** 各クライアントから使える。
- **AC1** Given 3経路いずれか, When 同一操作, Then 同一サービス層・同一権限/監査を通過し結果が一致する。
- **AC2** Given AI クライアント, When 認証, Then 代理ユーザー＋ロールが解決される（AI固有 principal なし）。

---

## INVEST / カバレッジ確認
- **Independent**: 各ストーリーは独立に設計・テスト可能。
- **Negotiable / Valuable**: 各ペルソナの価値に紐づく。
- **Estimable / Small**: 中粒度で見積もり可能。
- **Testable**: すべて Given/When/Then を持つ。
- **網羅**: 構造化検索/集計/権限境界/アクション提案・承認/監査記録・閲覧/型登録/MCP を全 Feature でカバー。
- **権限**: US-C1/C2, US-A1-AC2, US-B1-AC2, US-G1 で行レベル境界を多面的に検証。
- **PBT 対象**: US-C1-AC4（invariant, PBT-03）, US-F1-AC3（round-trip, PBT-02）を明示。
