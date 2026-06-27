# U5 Audit & Activity — NFR Requirements

U1/U2/shared-infrastructure を継承。U5 固有点を明記。

## パフォーマンス
- NFR-U5-1 監査追記は**同期**（書き込みパス内）。INV-2（監査なきアクション不成立）と fail-closed のため非同期化しない。
- NFR-U5-2 追記は単純 INSERT（インデックスは検索用に最小限）。p95 オーバーヘッド < 10ms 目標。
- NFR-U5-3 監査/Activity 検索は限定利用（ガバナンス/文脈参照）。ホットパスでない。

## スケーラビリティ / 保持
- NFR-U5-4 イベントは追記で単調増加。**保持期間 ≥ 90 日**（SECURITY-14）。古いものはアーカイブ/パージ運用（OPERATIONS）。
- NFR-U5-5 検索用に actor / object_type / timestamp に索引。

## 可用性 / 信頼性
- NFR-U5-6 監査追記の失敗は呼び出し元の操作を失敗させる（fail-closed, INV-2）。
- NFR-U5-7 Activity 追記失敗も原則 fail-closed（設定で緩和可。既定は安全側）。

## セキュリティ
- NFR-U5-8 **追記専用**: update/delete API なし。アプリ DB ユーザに UPDATE/DELETE を付与しない（SECURITY-14）。
- NFR-U5-9 PII 非保持（type/id/op/decision/reason のみ, SECURITY-03）。
- NFR-U5-10 Audit 検索はガバナンス限定（PermissionGateway, RESTRICTED）。Activity は SHARED 読み取り。

## テスト性
- NFR-U5-11 round-trip（PBT-02, TP-AU1）、PII-free invariant（TP-AU2）、mutate/delete 不在（TP-AU3）、generators（PBT-07）。

## Compliance Summary (NFR Requirements — U5)
- Security: SECURITY-14/03/15/08 を反映。暗号化/NW は shared。ブロッキングなし。
- PBT: PBT-02/07（Hypothesis 共通）。
