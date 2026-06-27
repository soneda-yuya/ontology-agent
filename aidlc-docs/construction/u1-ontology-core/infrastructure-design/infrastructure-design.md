# U1 Ontology Core — Infrastructure Design (lean)

論理コンポーネント（PostgreSQL・アプリプロセス・接続/シークレット）を実インフラへ最小マッピング。
デプロイ自動化（CI/CD・IaC）は OPERATIONS フェーズへ。プロバイダ非依存（例示は汎用）。

## サービスマッピング
| 論理コンポーネント | インフラ | 備考 |
|---|---|---|
| アプリプロセス（U1〜U6 同梱・モジュラーモノリス） | **クラウド VM 上のコンテナ**（Docker） | 小規模・単一インスタンス |
| PostgreSQL（type_defs / objects） | **マネージド PostgreSQL**（推奨） or VM 上コンテナ | マネージドだと暗号化/TLS/バックアップが容易（SECURITY-01） |
| TLS 終端 | リバースプロキシ（Caddy/nginx）or プラットフォーム LB | クライアント↔ハブを HTTPS 化 |
| シークレット | **環境変数 + .env（gitignore）** | DB 認証情報等。ハードコード禁止（SECURITY-12） |

## セキュリティ設定（Security 拡張準拠）
- **SECURITY-01 暗号化**:
  - 転送: クライアント↔ハブ TLS（HTTPS）、アプリ↔DB は `sslmode=require` 以上。
  - 保存: マネージド DB の at-rest 暗号化 / VM ボリューム暗号化。
- **SECURITY-07 ネットワーク（deny-by-default）**:
  - インバウンドは 443（TLS）のみ許可。DB ポートは公開しない（プライベートネットワーク/同一 VPC 限定）。
  - 管理アクセス（SSH 等）は送信元を限定。
- **SECURITY-12 認証情報**: ソース/IaC にハードコードしない。.env は配布せず VM 側で注入。DB ユーザは最小権限（U1 に必要な CRUD のみ, SECURITY-06）。
- **SECURITY-14 ログ保持/改ざん**: アプリ/監査ログは集約し保持期間 ≥ 90 日。監査ログは追記専用（アプリは自ログ削除権限を持たない）。
- **SECURITY-09 ハードニング**: 既定資格情報なし、本番でスタックトレース非表示、不要機能無効。
- **SECURITY-10 サプライチェーン**: 依存 lock、イメージタグ固定（`latest` 禁止）。

## U1 固有の留意
- objects テーブルの GIN 索引はマイグレーションで作成（migrations/）。
- DB 接続プールは VM のリソースに合わせ控えめ。接続は UnitOfWork スコープで解放。

## Compliance Summary (Infrastructure Design — U1)
- Security: SECURITY-01/06/07/09/10/12/14 を本ステージで具体化。ブロッキングなし。
- 注: 監査/Activity の保持・改ざん耐性詳細は U5、認証（トークン）と CORS/レート制限は U6 で具体化。
