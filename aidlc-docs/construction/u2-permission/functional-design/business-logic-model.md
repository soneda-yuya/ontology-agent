# U2 Permission — Business Logic Model

技術非依存。純関数 `decide` / `row_constraint` と、それを包む PermissionGateway。

## L1. decide（単一対象の可否） — US-C1 / US-C2
```
入力: principal, operation, object_type, object_attrs (任意), sharing_level
1. applicable = ポリシー中、principal.roles と (object_type or '*') と operation に一致する rule
2. 明示 DENY が1つでも一致 → DENY（最優先, fail-closed 寄り）          # P2
3. sharing_level == SHARED かつ READ → ALLOW（行制約バイパス）          # P3
4. ALLOW rule を評価:
     - row_predicate なし → 型レベル ALLOW
     - row_predicate あり:
         - object_attrs 提供あり → 述語成立で ALLOW（object[op] ∈ principal.attr[pa]）
         - object_attrs なし（存在判定前） → 「条件付き ALLOW」候補として保留
   いずれかの ALLOW 成立 → ALLOW
5. それ以外 → DENY（deny-by-default）                                  # P2
出力: AccessDecision(allowed, reason)   # reason に PII を含めない
```

## L2. row_constraint（クエリ用の行フィルタ） — US-C1
```
入力: principal, operation(READ), object_type, sharing_level
1. 明示 DENY（型レベル, 無条件）が一致 → NONE
2. sharing_level == SHARED → UNCONSTRAINED
3. ALLOW rule を集約:
     - 無条件 ALLOW（row_predicate なし）が1つでも → UNCONSTRAINED
     - row_predicate 付き ALLOW → predicates に追加
4. predicates が空 → NONE（deny-by-default）
   そうでなければ → AccessConstraint(predicates)   # OR 条件
出力: AccessConstraint
```

## L3. PermissionGateway（中央集権・必須通過点）
```
authorize_object(principal, object_type, obj_id, operation, object_attrs=None):
    sharing = registry.get_object_type(object_type).sharing_level
    d = decide(principal, operation, object_type, object_attrs, sharing)
    if not d.allowed: raise PermissionDenied(d.reason)   # fail-closed

authorize_query(principal, object_type, operation=READ) -> AccessConstraint:
    sharing = registry.get_object_type(object_type).sharing_level
    return row_constraint(principal, operation, object_type, sharing)

authorize_action(principal, action_type, target_attrs=None):
    # ActionType.target_type を解決し WRITE で decide
```

## L4. U1 連携（authorize フック実装の提供）
```
PermissionGateway は U1 OntologyService の authorize フックに渡すアダプタを提供:

def authorize_hook(operation_str, context):
    op = MAP[operation_str]                  # register_type→ADMIN, put_object→WRITE, get_object→READ
    principal = context["principal"]
    if principal is None: raise PermissionDenied("no principal")   # deny-by-default
    object_type = context["type"]
    decision = decide(principal, op, object_type, object_attrs=None, sharing=...)
    if not decision.allowed: raise PermissionDenied(decision.reason)

=> container で OntologyService(authorize=gateway.authorize_hook) を注入。
```

## L5. ポリシーのロード
- PolicyStorePort.load_all() → PermissionPolicy をメモリ保持（U1 の TypeRegistry と同方針: 起動時ロード + 変更時更新）。

## エラーハンドリング / 失敗時
- principal 欠落・評価エラー・型不明 → すべて DENY（fail-closed, SECURITY-15）。
- 例外 `PermissionDenied(reason)` は内部詳細・PII を含めない（SECURITY-09/03）。

## データフロー
```
呼び出し → PermissionGateway.authorize_* → decide/row_constraint(純関数)
   → ALLOW: 続行（クエリは AccessConstraint を U3 が SQL 化）
   → DENY: PermissionDenied（監査に記録: U5 連携）
```
