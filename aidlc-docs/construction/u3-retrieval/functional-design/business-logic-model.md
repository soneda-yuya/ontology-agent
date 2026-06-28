# U3 Retrieval / RAG — Business Logic Model

すべての取得は **PermissionGateway 通過後**のみ返す（INV-1）。各操作は U5 に監査記録。

## L1. search_objects(principal, query) — US-A1 / US-B 母集団 / US-C1
```
1. constraint = PermissionGateway.authorize_query(principal, query.object_type)   # AccessConstraint
2. if constraint.kind == NONE: audit(decision=allowed, empty); return []          # 権限ゼロ → 空
3. spec = build_sql(query.filters, constraint)                                     # パラメタライズド
4. results = ObjectStorePort.query(spec)
5. AuditService.record(search)                                                     # U5
6. return results   # 権限通過分のみ
```

## L2. get_object(principal, type, id) — US-A1-AC2 / US-C2(IDOR)
```
1. obj = ObjectStorePort.get(type, id)
2. if obj is None: audit; return None
3. decision = PermissionGateway.decide via authorize_object(principal, type, READ, obj.properties)
4. if denied: audit(denied); return None        # R4: 存在を秘匿（None=「無い」と区別不能）
5. audit(allowed); return obj
```

## L3. traverse_link(principal, start_ref, link_name, depth=1) — US-A2
```
1. link = TypeRegistry.get_link_type(link_name)
2. related = ObjectStore からリンク先を取得（REFERENCE/cardinality に従う）
3. 各 related に authorize_object(principal, link.target_type, READ, attrs) を適用しフィルタ   # US-A2-AC2 除外
4. audit; return 権限通過分
```

## L4. aggregate(principal, query) — US-B1/B2/B3
```
1. constraint = authorize_query(principal, query.object_type)
2. if NONE: return empty result
3. spec = build_aggregate_sql(filters, constraint, group_by, time_bucket+granularity)
     - 母集団は constraint+filters を満たす行のみ（US-B1-AC2: 権限外は母集団から除外）
     - group_by: properties->>'<g>' で GROUP BY
     - 期間: date_trunc(granularity, (properties->>'<t>')::timestamptz)
4. rows = ObjectStorePort.aggregate(spec)
5. audit; return AggregateResult(rows)
```

## L5. file_search(principal, text, limit) — US-H2
```
1. constraint = authorize_query(principal, "File")     # pseudo 型で認可（既定 RESTRICTED）
2. if NONE: return []
3. matches = FileIndexPort.search(text, limit)          # tsvector 全文検索（tsrank 順）
4. audit; return matches
```

## L6. semantic_search（phase2, 雛形のみ）
```
VectorStorePort.search(embedding, k) → ObjectRef → 権限フィルタ → audit。今回は interface のみ用意可。
```

## build_sql（row_constraint→SQL の中核）
```
AccessConstraint:
  UNCONSTRAINED → 追加句なし
  NONE          → 呼び出し前に空返し（ここに来ない）
  PREDICATES    → OR( properties->>'<obj_prop>' = ANY(%s) )  # %s = principal.attributes[principal_attribute] の配列
FieldFilter（JSONB, パラメタライズド）:
  EQ:       properties->>'p' = %s
  IN:       properties->>'p' = ANY(%s)
  GT/GTE/LT/LTE: (properties->>'p')::numeric <op> %s
  BETWEEN:  (properties->>'p')::numeric BETWEEN %s AND %s
  CONTAINS: properties->>'p' ILIKE '%%' || %s || '%%'
最終 WHERE = object_type = %s AND (filters...) AND (constraint predicates...)
```

## エラー / 不変
- 権限通過前に ObjectStore を読まない（INV-1）。
- get の権限違反は None（情報秘匿, R4）。
- 監査記録の失敗は操作失敗（INV-2, U5 が伝播）。
- すべてパラメタライズド（SECURITY-05）。
