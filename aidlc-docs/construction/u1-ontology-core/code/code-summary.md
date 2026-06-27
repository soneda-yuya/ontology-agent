# U1 Ontology Core — Code Summary

実装したアプリコードの概要（アプリ本体はワークスペース root、本サマリのみ docs）。

## 生成ファイル（アプリコード）
```
pyproject.toml                  # 依存ピン留め, pytest/ruff 設定 (SECURITY-10)
docker-compose.yml              # dev PostgreSQL (16.3, migrations 自動適用)
Dockerfile                      # 固定タグ・非root (SECURITY-09/10)
.env.example                    # シークレットは env/.env (SECURITY-12)
migrations/0001_u1_ontology.sql # type_defs / objects(JSONB) + GIN

src/mini_aip/
├── domain/ontology/
│   ├── types.py           # PropertyType/ObjectType/LinkType/ActionType/OntologyObject/enums
│   ├── serialization.py   # serialize/deserialize (round-trip, PBT-02)
│   ├── validation.py      # DynamicModelFactory, validate_object, validate_type_def
│   ├── redaction.py       # PiiRedactor (SECURITY-03)
│   ├── registry.py        # TypeRegistry (in-memory)
│   └── errors.py          # DomainError 群 (PII-safe)
├── ports/
│   ├── object_store.py    # ObjectStorePort
│   └── type_registry.py   # TypeRegistryPort
├── adapters/outbound/postgres/
│   ├── connection.py      # ConnectionProvider / UnitOfWork (tx, fail-closed)
│   ├── object_store.py    # PostgresObjectStore (parameterized, JSONB)
│   └── type_registry.py   # PostgresTypeRegistry
├── services/
│   └── ontology_service.py # OntologyService (authorize/audit は注入フック既定no-op)
└── config/
    ├── settings.py        # Settings (env, MINIAIP_*)
    └── container.py       # DI 組み立て

tests/
├── unit/      # types, validation, registry, redaction, ontology_service
├── pbt/       # generators (PBT-07), round-trip (PBT-02)
└── integration/ # postgres store (@integration, Build&Test で実行)
```

## 検証結果（生成時のスモーク確認）
- `pytest -m "not integration"`: **30 passed**（unit + PBT）
- `ruff check`: **All checks passed**
- integration（DB必須）2件は deselected（Build & Test フェーズで実行）

## 設計トレーサビリティ
- US-F1（型登録）: OntologyService.register_type + TypeRegistry + PostgresTypeRegistry
- US-D2（ActionType 定義）: ActionType + register_type（実行は U4）
- US-F1-AC3 / TP-1/TP-2（round-trip, PBT-02）: serialization.py + tests/pbt
- US-H1（共有メモリ保存基盤）: put_object（メモリ系も型登録のみで成立）
- INV-3（型追加でコード不変）: JSONB 格納 + データ駆動型で担保

## セキュリティ順守
- SECURITY-05（パラメタライズド）, 03（PII非ログ/エラー）, 15（fail-closed/tx rollback）,
  09（非root/汎用エラー）, 10（依存・イメージ固定）, 12（.env）。

## U2/U5 連携の残し方
- OntologyService は `authorize` / `audit` フック（既定 no-op）を受け取る。
  U2 PermissionGateway / U5 AuditService 実装時に container で注入する（呼び出し側は不変）。

## 未実施（後続）
- DB を要するテストの実行（Build & Test）。
- 認証・MCP/HTTP/CLI（U6）、権限（U2）、監査/Activity（U5）。
