# U2 Permission — NFR Design Patterns

U1 パターン + 共有インフラを継承。U2 固有のパターンを明記。

## 判定コアのパターン
- **Pure-function decision core**: `decide` / `row_constraint` は副作用なし・I/O なし。
  - 効果: テスト容易（PBT-03）、p95<5ms（NFR-U2-1）、推論が単純。
- **Deterministic resolution（deny-by-default + explicit-deny-precedence）**:
  1) 明示 DENY 一致 → DENY、2) SHARED かつ READ → ALLOW、3) ALLOW 評価、4) それ以外 DENY。
  - 決定性により invariant（TP-P1/P2）が保証しやすい。

## 回復性 / 失敗時
- **Fail-closed gateway**: `PermissionGateway` が判定を包み、例外・principal欠落・型不明で DENY（SECURITY-08/15）。
- **Safe-by-default loading**: ポリシーロード失敗時は「空ポリシー」＝全 RESTRICTED 型が全拒否（起動時に検知して停止 or 全拒否）。

## 性能パターン
- **In-memory PolicyRegistry**: 起動時 `PolicyStorePort.load_all`、変更時に更新（U1 TypeRegistry と同型）。判定は索引引き + 純計算のみ。
- キャッシュ不要（判定自体が軽量）。

## セキュリティパターン
- **PII-safe reasons**: AccessDecision.reason / 例外に属性値・PII を含めない（共通の安全メッセージ, SECURITY-03/09）。
- **Least authority for hook**: U1 へ渡す `authorize_hook` は判定のみ（データ取得・変更はしない）。

## 検証 / テスト性
- **PBT-03 invariant**: TP-P1（明示deny→必ず拒否）, TP-P2（deny-by-default）, TP-P3（principal=None→拒否）, TP-P4（decide↔row_constraint整合）。
- **Generators（PBT-07）**: principal / rule / policy / object_attrs。

## マッピング（NFR→パターン）
| NFR | パターン |
|---|---|
| U2-1/2 性能 | Pure-function core + in-memory registry |
| U2-5/6 fail-closed | Fail-closed gateway + safe-by-default loading |
| U2-7 deny-by-default | Deterministic resolution |
| U2-8 PII非漏洩 | PII-safe reasons |
| U2-10 テスト | PBT-03 invariants + generators |

## Compliance Summary (NFR Design — U2)
- Security: SECURITY-08/15/03/09 をパターン化。暗号化/ネットワークは shared-infrastructure（SECURITY-01/07）。ブロッキングなし。
- PBT: invariant/ generator パターンを設計。✅
