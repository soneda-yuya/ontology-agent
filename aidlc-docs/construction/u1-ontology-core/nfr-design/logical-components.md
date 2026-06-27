# U1 Ontology Core — Logical Components

NFR を支える論理コンポーネント（インフラ的要素）と統合パターン。

## コンポーネント
| コンポーネント | 役割 | 配置 |
|---|---|---|
| **ConnectionProvider** | PostgreSQL 接続プールの提供 | adapters/outbound/postgres |
| **UnitOfWork / TxManager** | トランザクション境界（begin/commit/rollback）を提供。書き込み操作をラップ | adapters/outbound/postgres |
| **InMemoryTypeRegistry** | 型定義のインメモリ索引。起動時ロード、register_type で更新 | services / domain（純データ） + Port 実装でロード |
| **DynamicModelFactory** | 型定義から Pydantic モデルを生成し書き込み時検証 | domain/ontology |
| **PiiRedactor** | ログ/例外出力前に is_pii 値をマスク | domain/ontology（共通ヘルパ） |
| **SqlSpecBuilder** | ObjectQuery → パラメタライズド SQL（GIN 活用） | adapters/outbound/postgres |

## 統合パターン
```
register_type / write object:
  TxManager.begin
    → DynamicModelFactory.validate(動的Pydantic)        # 検証失敗→ rollback, fail-closed
    → ObjectStorePort / TypeRegistryPort.save           # パラメタライズド
    → (register_type なら) InMemoryTypeRegistry.update
  TxManager.commit  (失敗時 rollback, 接続解放)

read:
  InMemoryTypeRegistry.get(type)                        # O(1)
  ObjectStorePort.get/query(SqlSpecBuilder, GIN)        # キャッシュなし
  PiiRedactor は lo-level ログ出力時に常時適用
```

## 接続・プール方針
- 小規模・単一インスタンス前提。プールサイズは控えめ（設定で調整可）。
- 接続は UnitOfWork スコープで取得・解放（リーク防止, NFR-U1-9）。

## 将来拡張ポイント（インターフェース不変で差し込み可能）
- リトライ/バックオフ: ObjectStorePort 実装にデコレータとして追加。
- 読み取りキャッシュ: RetrievalService と Port の間にキャッシュ層。
- マルチプロセス: InMemoryTypeRegistry に LISTEN/NOTIFY 無効化を追加。

## Open（Infrastructure Design へ）
- 接続文字列の TLS 強制、保存時暗号化（SECURITY-01）。
- シークレット（DB 認証情報）の供給方法（SECURITY-12: ハードコード禁止）。
