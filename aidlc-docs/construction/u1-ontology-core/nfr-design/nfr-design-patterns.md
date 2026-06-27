# U1 Ontology Core — NFR Design Patterns

NFR 要件（nfr-requirements.md）を設計パターンへ落とす。

## 回復性 / エラーハンドリング
- **Fail-closed（リトライなし）**: DB 一時エラーも含め、エラー時は即座に失敗を返し、保存/実行しない（ND1=B, SECURITY-15）。
  - 将来拡張: 一時エラー（接続断/デッドロック）への限定リトライ+バックオフを Port 実装に差し込める形にしておく（インターフェースは不変）。
- **Transaction boundary（Unit of Work）**: 書き込み（型登録・オブジェクト保存）は単一トランザクション内。失敗時ロールバック、接続/トランザクションは finally で解放（NFR-U1-8/9）。
- **Global error mapping**: ドメイン例外（DomainValidationError 等）をサービス層で安全なエラーに変換。内部詳細・スタックトレースを露出しない（SECURITY-09/15）。

## 性能パターン
- **In-memory TypeRegistry**: 起動時全ロード、register_type 時に同プロセス内で直接更新（O(1) 参照, NFR-U1-5）。
- **JSONB + GIN index**: 属性検索は GIN 索引を利用（NFR-U1-6）。p95<100ms 目標。
- **No read cache**（ND2=A）: 小規模では DB+索引で目標達成。早期最適化を回避。必要時に Port 前段でキャッシュ追加可能（設計に余地あり）。

## セキュリティパターン
- **Parameterized queries 徹底**（SECURITY-05）: 文字列連結を一切しない。クエリ構築は SqlSpec→パラメタ束縛。
- **Write-time validation（動的 Pydantic）**: 型定義から生成した Pydantic モデルで検証。余剰プロパティ拒否（BR-10）。
- **PII redaction**: is_pii プロパティはログ/例外メッセージから除外する共通ヘルパを通す（SECURITY-03, BR-11）。
- **Deny/relay 不可情報**: 検証失敗時に「なぜ通らなかったか」は必要最小限のみ返す。

## 検証 / テスト性パターン
- **Property-based（Hypothesis）**: round-trip（TP-1/TP-2, PBT-02）、generators（PBT-07）、shrinking+seed（PBT-08）。
- **Ports によるテスト容易性**: ObjectStorePort/TypeRegistryPort をモックしドメイン/サービスを独立検証。

## マッピング（要件→パターン）
| NFR | パターン |
|---|---|
| U1-7/8/9 fail-closed/トランザクション | Fail-closed + Transaction boundary |
| U1-4/5/6 性能 | In-memory registry + JSONB/GIN（no cache） |
| U1-10/11/12 セキュリティ | Parameterized + write-time validation + PII redaction |
| U1-15/16 テスト | Hypothesis PBT + ports モック |

## Compliance Summary (NFR Design — U1)
- Security: SECURITY-05/03/09/15 をパターン化。SECURITY-01（暗号化）は Infra Design。ブロッキングなし。
- PBT: round-trip/generator/shrinking パターンを設計。✅
