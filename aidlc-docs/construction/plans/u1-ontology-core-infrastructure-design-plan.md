# Infrastructure Design Plan (lean) — U1 Ontology Core

**目的**: U1 の論理コンポーネント（PostgreSQL/接続/シークレット）を実インフラへ最小マッピング。
**方針**: lean。Security 拡張（SECURITY-01/07/12/14）を満たす最小限。デプロイ自動化は OPERATIONS へ。

> U1 のインフラは主に PostgreSQL とアプリプロセス。多くは共有インフラ（shared-infrastructure）として U6 にも効く。
> 質問はチャットで収集し [Answer]: に記録。

---

## Infrastructure Questions

### Q-I1: デプロイ・トポロジ（Context Hub は「チーム共有」前提）
A) 自ホスト単一サーバー（チームがアクセスする常駐サーバー / Docker Compose）— 「共有」要件に自然
B) 各ユーザーがローカル起動（共有は別途同期が必要 → 今回の趣旨と不整合）
C) クラウド VM / マネージド（小さな共有サーバーをクラウドに）
X) Other

[Answer]: C) クラウド VM / マネージド

### Q-I2: シークレット管理（DB 認証情報等, SECURITY-12）
A) 環境変数 + .env（gitignore 済）— PoC 最小。ハードコード禁止は満たす
B) 専用シークレットマネージャ（Vault / クラウドの secrets）— 本番寄り
X) Other

[Answer]: A) 環境変数 + .env

### Q-I3: 暗号化・転送（SECURITY-01）
A) クライアント↔ハブ TLS + DB 接続 TLS + ディスク/ボリューム暗号化（OS/インフラ層）— セキュリティON 準拠
B) 一部は後段（PoC では TLS のみ等）
X) Other

[Answer]: A) TLS + DB TLS + ディスク暗号

---

## Mandatory Artifacts
- [ ] `construction/u1-ontology-core/infrastructure-design/infrastructure-design.md`
- [ ] `construction/u1-ontology-core/infrastructure-design/deployment-architecture.md`
- [ ] `construction/shared-infrastructure.md`（U1 の PostgreSQL 等は共有のため）

## Execution Checklist
- [x] 1. 回答反映
- [x] 2. infrastructure-design.md（サービスマッピング・セキュリティ設定）
- [x] 3. deployment-architecture.md（トポロジ・構成図）
- [x] 4. shared-infrastructure.md（PostgreSQL/ネットワーク/シークレット共有方針）
- [x] 5. aidlc-state.md 更新
