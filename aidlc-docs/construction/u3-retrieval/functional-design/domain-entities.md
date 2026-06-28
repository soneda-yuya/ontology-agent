# U3 Retrieval / RAG — Domain Entities

技術非依存。検索・集計・ファイルの問い合わせモデル。権限は U2、永続は U1/ObjectStore、監査は U5。

## クエリ
### Operator（enum）
`EQ` / `IN` / `GT` / `LT` / `GTE` / `LTE` / `BETWEEN` / `CONTAINS`

### FieldFilter
| フィールド | 型 | 説明 |
|---|---|---|
| property | str | 対象プロパティ名 |
| operator | Operator | 演算子 |
| value | Any | 値（IN/BETWEEN は配列/2要素） |

### ObjectQuery
| フィールド | 型 | 説明 |
|---|---|---|
| object_type | str | 対象型 |
| filters | tuple[FieldFilter, ...] | AND 結合 |
| limit | int | 既定 100 |

### Granularity（enum）
`DAY` / `WEEK` / `MONTH`

### AggregateQuery
| フィールド | 型 | 説明 |
|---|---|---|
| object_type | str | 対象型 |
| filters | tuple[FieldFilter, ...] | 母集団の絞り込み |
| group_by | str \| None | グループ化プロパティ |
| time_bucket_property | str \| None | 期間集計の対象（DATE/DATETIME プロパティ） |
| granularity | Granularity \| None | 期間粒度 |
| metric | str | "count"（MVP） |

### AggregateResult
| フィールド | 型 |
|---|---|
| rows | tuple[AggregateRow, ...] |

AggregateRow: { key: str | None, bucket: str | None, count: int }

## ファイル
### FileMatch
| フィールド | 型 | 説明 |
|---|---|---|
| path | str | ファイルパス/ID |
| snippet | str | 一致箇所抜粋 |
| score | float | 関連度（tsrank 等） |

## 内部（adapter 向け）
### SqlSpec
- 生成された WHERE 句（パラメタライズド）+ params。`FieldFilter` と `AccessConstraint`（U2）から構築。
- ObjectStorePort.query(SqlSpec) を U3 が拡張利用（U1 の get/write に加え query を提供）。

## 関係（テキスト）
```
ObjectQuery 1───* FieldFilter
AggregateQuery 1───* FieldFilter
RetrievalService ─uses→ PermissionGateway(row_constraint/authorize_object), ObjectStorePort(query),
                         FileIndexPort(search), AuditService(record), VectorStorePort(phase2)
AccessConstraint(U2) + FieldFilter ──build──> SqlSpec
```

## 擬似型（権限解決）
- ファイル検索は pseudo 型 `"File"`（既定 RESTRICTED, ガバナンスで共有設定可）で gateway 認可。
