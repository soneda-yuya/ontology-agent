# Unit of Work — Story Map

各ストーリーを主担当ユニットへ割当（協働ユニットも併記）。全 12 ストーリーが割当済。

| Story | 概要 | 主ユニット | 協働 |
|---|---|---|---|
| US-A1 | 顧客と関連オブジェクトの構造化取得 | U3 Retrieval | U1, U2, U5 |
| US-A2 | リンク探索 | U3 Retrieval | U1, U2 |
| US-B1 | 機能別/カテゴリ別 集計（PM） | U3 Retrieval | U2, U5 |
| US-B2 | セグメント別 解約率分析（Sales） | U3 Retrieval | U2, U5 |
| US-B3 | 期間トレンド | U3 Retrieval | U2 |
| US-C1 | 全結果の権限フィルタ（中央強制） | U2 Permission | 全ユニット |
| US-C2 | 担当外データ越境防止（IDOR） | U2 Permission | U3, U6 |
| US-D1 | アクション提案・承認・実行 | U4 Action | U2, U5, U1 |
| US-D2 | ActionType 定義 | U1 Ontology | U4 |
| US-E1 | 全件監査記録（追記専用） | U5 Audit | 全ユニット |
| US-E2 | 監査検索（ガバナンス） | U5 Audit | U2 |
| US-F1 | ObjectType/LinkType 登録 | U1 Ontology | U2, U5 |
| US-G1 | MCP ツール利用・認証 | U6 MCP | U2, 全サービス |

## カバレッジ検証
- **全ストーリー割当**: ✅ 12/12。
- **横断ストーリー**: US-C1（権限）と US-E1（監査）は全ユニットに作用する横断要件 → U2/U5 を主に、各ユニット実装時に必ず経由（INV-1/INV-2）。
- **ペルソナ整合**: CS=U3 中心, PM/Sales=U3 集計, Governance=U1/U5, 全員=U6 経由。
- **PBT 割当**: U2（PBT-03 invariant）, U1（PBT-02 round-trip）。
