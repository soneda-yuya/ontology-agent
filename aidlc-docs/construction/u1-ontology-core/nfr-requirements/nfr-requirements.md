# U1 Ontology Core — NFR Requirements

対象: 型システム・レジストリ・OntologyObject 永続。規模は小規模前提。

## スケーラビリティ
- NFR-U1-1 型数 〜数十、オブジェクト 〜数十万を単一 PostgreSQL で扱う。
- NFR-U1-2 型追加でスキーマ変更（DDL）が不要であること（JSONB 格納により担保）。
- NFR-U1-3 将来の水平スケール時は、TypeRegistry を LISTEN/NOTIFY 無効化方式へ移行できる構造にしておく（今は単一プロセス）。

## パフォーマンス
- NFR-U1-4 `get_object` / 単一型の簡易属性クエリ: **p95 < 100ms**。
- NFR-U1-5 TypeRegistry 参照はインメモリ（O(1) 近似）。
- NFR-U1-6 属性検索は JSONB GIN 索引を用いる。

## 可用性 / 信頼性
- NFR-U1-7 単一インスタンス前提（PoC）。DB 接続失敗・検証失敗は fail-closed（保存/実行しない）。
- NFR-U1-8 書き込みはトランザクション内で実行し、失敗時はロールバック（SECURITY-15）。
- NFR-U1-9 全外部 I/O（DB）に明示的エラーハンドリング、リソース解放（接続/トランザクション）。

## セキュリティ（U1 で関係する範囲）
- NFR-U1-10 SQL はパラメタライズド（文字列連結禁止, SECURITY-05）。
- NFR-U1-11 PII プロパティ値はログ・例外メッセージに出さない（SECURITY-03, BR-11）。
- NFR-U1-12 書き込み時に型整合検証（動的 Pydantic）、余剰プロパティ拒否（SECURITY-05, BR-10）。
- NFR-U1-13 保存時/転送時暗号化は Infrastructure Design で具体化（SECURITY-01）。

## 保守性 / テスト性
- NFR-U1-14 ドメイン core はフレームワーク非依存（ports 経由）。
- NFR-U1-15 PBT: round-trip（PBT-02, TP-1/TP-2）と generators（PBT-07）を実装。shrinking/seed 再現（PBT-08）。
- NFR-U1-16 例示テストと PBT を分離配置（tests/unit, tests/pbt）。

## 監査性
- NFR-U1-17 型登録/更新は AuditService に記録（actor/role/timestamp/対象型）。

## Compliance Summary (NFR Requirements — U1)
- **Security**: SECURITY-05/03/15 を NFR に反映（U1-10/11/12/08）。SECURITY-01 は Infra Design へ（現時点 N/A）。ブロッキングなし。
- **PBT**: PBT-09 フレームワーク選定（Hypothesis）= 本ステージで確定（tech-stack-decisions.md）。PBT-02/07/08 を NFR に明記。✅
