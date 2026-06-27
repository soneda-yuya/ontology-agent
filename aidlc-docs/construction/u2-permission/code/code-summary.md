# U2 Permission — Code Summary

## 生成 / 変更ファイル
```
# U1 への後方互換変更
src/mini_aip/domain/ontology/types.py     # SharingLevel 追加 + ObjectType.sharing_level=RESTRICTED
src/mini_aip/domain/ontology/__init__.py  # SharingLevel export

# U2 新規
src/mini_aip/domain/permission/
├── models.py     # Principal/Operation/Effect/AttributePredicate/PermissionRule/
│                 #   AccessDecision/AccessConstraint/ConstraintKind
├── decision.py   # decide / row_constraint（純関数, TP-P4 整合）
├── registry.py   # PolicyRegistry（インメモリ）
└── errors.py     # PermissionDenied（PII-free）
src/mini_aip/ports/policy_store.py                       # PolicyStorePort
src/mini_aip/adapters/outbound/postgres/policy_store.py  # PostgresPolicyStore（parameterized）
src/mini_aip/services/permission_gateway.py              # PermissionGateway + authorize_hook
src/mini_aip/config/container.py                         # build_secured_ontology_service 追加
migrations/0002_u2_policies.sql                          # policies テーブル

# テスト
tests/unit/test_permission_decision.py     # decide/row_constraint 例示
tests/unit/test_permission_gateway.py      # gateway + hook + secured service
tests/pbt/perm_generators.py               # PBT-07 generators
tests/pbt/test_permission_invariants.py    # TP-P1/P2/P4
tests/integration/test_postgres_policy_store.py  # @integration
```

## 検証結果
- `pytest -m "not integration"`: **47 passed**
- `pytest`（integration 含む・実 PostgreSQL）: **50 passed**
- `ruff check`: clean
- **U1 既存テストは非回帰**（sharing_level は既定値で round-trip 維持）

## 重要点
- **authorize_hook = 型レベルゲート**（deny-by-default / 明示deny / principal=None 拒否 / 不明op 拒否）。
- **単一 get の行レベル(IDOR)は U3** が fetch 後に `authorize_object(attrs)` で実施（本ユニットは gateway + 純関数を提供）。
- **DENY は無条件**（TP-P1 を保証）。`decide` と `row_constraint` は TP-P4 で整合。
- **権限注入**: `build_secured_ontology_service` が `OntologyService(authorize=gateway.authorize_hook)` を構成。既定 `build_ontology_service`(no-op) は bootstrap/テスト用に維持。

## ストーリートレーサビリティ
- US-C1（権限フィルタ）: row_constraint / gateway / decide
- US-C2（越境/IDOR）: authorize_object（行レベル, 単一 get は U3 で fetch 後）/ 型レベルゲート
- PBT-03 invariant: TP-P1/P2/P4（tests/pbt）

## セキュリティ順守
- SECURITY-08（deny-by-default/IDOR）, 15（fail-closed）, 03/09（PII/詳細非漏洩）, 05（parameterized）, 06（policies 最小権限）。

## 未実施 / 後続
- **bootstrap**: 空 policies では deny-by-default で register_type 不可。`build_secured_ontology_service` 利用時は初期 admin ALLOW ルールの seed が必要（PostgresPolicyStore.save）。
- 監査（U5）連携: gateway の拒否/許可を AuditService に記録。
- 単一オブジェクト get の行レベル enforcement は U3 で実装。
