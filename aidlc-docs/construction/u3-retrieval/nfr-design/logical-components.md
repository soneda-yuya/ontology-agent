# U3 Retrieval / RAG — Logical Components

| コンポーネント | 役割 | 配置 |
|---|---|---|
| **RetrievalService** | search/get/traverse/aggregate/file_search のオーケストレーション（権限→IO→監査） | services |
| **SqlSpecBuilder** | FieldFilter + AccessConstraint → SqlSpec（純関数, パラメタライズド） | domain/query or adapters |
| **ObjectStorePort（拡張）** | query(SqlSpec) / aggregate(AggregateSpec) を追加 | ports |
| **FileIndexPort** | search(text) / index(path, content) | ports |
| **PostgresObjectStore（拡張）** | query/aggregate 実装（JSONB, GROUP BY, date_trunc） | adapters/outbound/postgres |
| **PostgresFileIndex** | tsvector 全文検索 | adapters/outbound/postgres |
| **VectorStorePort（phase2）** | upsert/search（interface のみ今回） | ports |

## 統合パターン
```
search/aggregate:
  authorize_query(principal, type) → AccessConstraint
    NONE → 空返し（+audit）
    else → SqlSpecBuilder(filters, constraint) → ObjectStore.query/aggregate → audit → 返却

get:
  ObjectStore.get → None?返す : authorize_object(attrs) 不許可?None : audit+返却

file_search:
  authorize_query(principal,"File") → FileIndexPort.search → audit
```

## DI（container 追記予定）
```
retrieval = RetrievalService(object_store, file_index, gateway, audit_adapter, registry)
# secured builder に統合（OntologyService とは別に公開）
```

## 将来拡張（インターフェース不変）
- VectorStorePort 実装（pgvector）で semantic_search（A→B の B）。
- 複合論理フィルタ（AND/OR ネスト）、フィルタ DSL。
