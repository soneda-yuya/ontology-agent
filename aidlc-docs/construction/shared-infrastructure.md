# Shared Infrastructure — ontology-agent (Mini AIP / Context Hub)

U1 で確定したインフラのうち、**全ユニット（U1-U6）で共有**する要素をまとめる。
各ユニットの Infrastructure Design はこの共有方針を参照する（重複定義を避ける）。

## 共有方針
- **デプロイ**: クラウド VM 単一インスタンス上にモジュラーモノリス（U1-U6 同梱）をコンテナ実行。チームが HTTPS で接続する常駐ハブ。
- **データストア**: マネージド PostgreSQL を全ユニットで共有（type_defs/objects=U1、policies=U2、audit/activity=U5、file index メタ=U3、vector=U3 phase2 は pgvector）。
- **シークレット**: 環境変数 + .env（gitignore、配布禁止、VM 側注入）。ハードコード禁止（SECURITY-12）。
- **ネットワーク**: deny-by-default。インバウンド 443(TLS) のみ。DB は非公開（プライベート）。管理アクセスは送信元限定（SECURITY-07）。
- **暗号化**: 転送 TLS（クライアント↔ハブ、アプリ↔DB）、保存 at-rest 暗号化（SECURITY-01）。
- **ログ/監査**: 集約・保持 ≥90日、監査は追記専用・アプリは自ログ削除不可（SECURITY-14）。
- **サプライチェーン**: 依存 lock、イメージタグ固定、`latest` 禁止（SECURITY-10）。

## ユニット横断の対応表
| 関心事 | 主担当ユニット | 共有要素 |
|---|---|---|
| 認証（トークン/CORS/レート制限） | U6 | TLS、認証鍵（env） |
| 権限ポリシー保存 | U2 | 共有 PostgreSQL |
| 監査/Activity 保持・改ざん耐性 | U5 | 集約ログ、append-only |
| ベクトル/ファイル索引 | U3 | pgvector（phase2）、ファイルアクセス権 |

## 注記
- CI/CD・IaC・監視ダッシュボード等の運用自動化は OPERATIONS フェーズ（現状プレースホルダ）。
- 本ファイルは U2-U6 の Infrastructure 検討時に更新・追記していく。
