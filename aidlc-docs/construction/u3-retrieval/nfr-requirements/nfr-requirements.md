# U3 Retrieval / RAG — NFR Requirements

U1/U2/U5/shared を継承。U3 固有点を明記。

## パフォーマンス
- NFR-U3-1 単一 get / 単純 search: p95 < 100ms（U1 継承、JSONB GIN 利用）。
- NFR-U3-2 aggregate（count/group_by/期間）: 小規模で p95 < 300ms。
- NFR-U3-3 file_search: PostgreSQL 全文検索（tsvector + GIN）。p95 < 300ms。
- NFR-U3-4 権限オーバーヘッドは無視可（U2 純関数）。

## スケーラビリティ
- NFR-U3-5 小規模前提。索引: objects の GIN（U1）、file_index の tsvector GIN。
- NFR-U3-6 ベクトル検索（phase2）は pgvector 拡張を追加時に対応（今回は interface のみ）。

## 信頼性 / セキュリティ
- NFR-U3-7 権限通過前に store を読まない（INV-1）。空権限=空結果。
- NFR-U3-8 IDOR 秘匿（get 不許可→None）。
- NFR-U3-9 すべてパラメタライズド（SECURITY-05）。フィルタ/制約値はバインド。
- NFR-U3-10 全取得を U5 に監査（記録失敗→操作失敗, INV-2）。

## テスト性
- NFR-U3-11 query round-trip（PBT-02, TP-R1）、constraint→SQL 整合（TP-R2/R3）、generators（PBT-07）。

## Compliance Summary (NFR Requirements — U3)
- Security: SECURITY-08/05/15/03 を反映。暗号化/NW は shared。ブロッキングなし。
- PBT: PBT-02/07（Hypothesis 共通）。
