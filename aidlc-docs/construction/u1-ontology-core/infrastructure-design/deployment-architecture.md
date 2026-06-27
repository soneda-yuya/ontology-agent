# U1 Ontology Core — Deployment Architecture (lean)

## トポロジ（クラウド VM / マネージド, チーム共有の常駐ハブ）
```
   各ユーザーのローカル AI クライアント
   (Claude Code / Cursor / Local LLM / 自作Agent)
            |  HTTPS (TLS) : MCP / HTTP API / CLI
            v
   +-------------------------------+
   |  Cloud VM (single instance)   |
   |   Reverse proxy (TLS 終端)     |
   |   Mini AIP / Context Hub       |
   |   (FastAPI + MCP, U1-U6)       |
   +---------------+---------------+
                   |  TLS (sslmode=require), private network
                   v
   +-------------------------------+
   |  Managed PostgreSQL           |
   |   type_defs / objects (JSONB) |
   |   at-rest encryption, backup  |
   +-------------------------------+

   ネットワーク: インバウンドは 443 のみ。DB は非公開（プライベート）。
   シークレット: VM の環境変数 / .env（gitignore, 配布しない）。
```

## 構成要素
- **Compute**: クラウド VM 1 台（小〜中）。コンテナ（Docker）でアプリを実行。
- **DB**: マネージド PostgreSQL（推奨。暗号化/TLS/バックアップが容易）。代替で VM 上コンテナ + ボリューム暗号化。
- **TLS**: リバースプロキシ（Caddy 等で自動証明書）or プラットフォーム LB。
- **将来**: pgvector（U3 phase2）、水平スケール時は TypeRegistry を LISTEN/NOTIFY 化、LB 追加。

## 環境変数（U1 関連・例）
| 変数 | 用途 |
|---|---|
| `DATABASE_URL` | PostgreSQL 接続（TLS 付き）|
| `DB_SSLMODE` | `require` 以上 |
| （その他は U6 で: 認証トークン鍵, CORS 許可元 等）|

## デプロイ手順の自動化
- 本ステージは設計のみ。CI/CD・IaC・監視ダッシュボードは OPERATIONS（プレースホルダ）で具体化。
