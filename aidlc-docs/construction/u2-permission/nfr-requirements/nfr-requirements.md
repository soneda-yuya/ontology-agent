# U2 Permission — NFR Requirements

U1 / shared-infrastructure を継承。U2 固有点を明記。

## パフォーマンス
- NFR-U2-1 権限判定（decide / row_constraint）は**純関数・インメモリ**。**p95 < 5ms**（全リクエストの critical path のためオーバーヘッドを無視できる水準）。
- NFR-U2-2 ポリシーはインメモリ保持（PolicyStorePort.load_all を起動時）。

## スケーラビリティ
- NFR-U2-3 小規模（ロール・ルール数は限定的）。ポリシーは全件インメモリで可。
- NFR-U2-4 ポリシー変更時はインメモリを更新（単一プロセス。将来は LISTEN/NOTIFY、U1 と同方針）。

## 可用性 / 信頼性（fail-closed）
- NFR-U2-5 principal 欠落・型不明・評価例外は**常に拒否**（SECURITY-08/15）。
- NFR-U2-6 ポリシーロード失敗時は「全拒否」に倒す（起動時に検知、安全側）。

## セキュリティ
- NFR-U2-7 deny-by-default・明示 deny 最優先（SECURITY-08）。
- NFR-U2-8 AccessDecision.reason / 例外に PII・属性値を含めない（SECURITY-03/09）。
- NFR-U2-9 権限判定（許可/拒否）は監査対象（U5 連携）。

## テスト性
- NFR-U2-10 **PBT-03 invariant** を実装（明示 deny→必ず拒否 / deny-by-default / principal=None→拒否 / decide↔row_constraint 整合）。generators（PBT-07）。
- NFR-U2-11 純関数中心のため例示テスト + PBT で高カバレッジが容易。

## Compliance Summary (NFR Requirements — U2)
- Security: SECURITY-08/15/03/09 を反映。ブロッキングなし。
- PBT: PBT-09 = Hypothesis（U1 と共通）。PBT-03/07 を U2 の主対象として明記。
