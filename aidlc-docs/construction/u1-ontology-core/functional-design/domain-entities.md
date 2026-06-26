# U1 Ontology Core — Domain Entities

技術非依存のドメインモデル。ハイブリッド型方式: 型定義はデータ、検証は書き込み時に Pydantic。

## エンティティ

### PropertyType
| フィールド | 型 | 説明 |
|---|---|---|
| name | str | プロパティ名（型内で一意） |
| data_type | DataType | enum: STRING, INTEGER, FLOAT, BOOLEAN, DATE, DATETIME, ENUM, REFERENCE |
| required | bool | 必須か |
| is_pii | bool | PII フラグ（ログ除外・権限で利用, SECURITY-03） |
| enum_values | list[str] \| None | data_type=ENUM のとき必須 |
| ref_object_type | str \| None | data_type=REFERENCE のとき必須（参照先 ObjectType 名） |

### ObjectType
| フィールド | 型 | 説明 |
|---|---|---|
| name | str | 型名（グローバル一意） |
| properties | list[PropertyType] | プロパティ定義 |
| id_property | str | 一意キーとなるプロパティ名（既定: "id"） |
| title_property | str \| None | 表示・検索用の代表プロパティ |
| text_properties | list[str] | ベクトル検索対象テキスト（phase2 で利用） |

### LinkType（有向 + cardinality + 逆ナビ）
| フィールド | 型 | 説明 |
|---|---|---|
| name | str | リンク名（順方向ナビゲーション名） |
| source_type | str | 起点 ObjectType |
| target_type | str | 終点 ObjectType |
| cardinality | Cardinality | ONE_TO_ONE / ONE_TO_MANY / MANY_TO_MANY |
| inverse_name | str | 逆方向ナビゲーション名（例: aircraft↔flights） |

### ActionType
| フィールド | 型 | 説明 |
|---|---|---|
| name | str | アクション名 |
| target_type | str | 対象 ObjectType |
| input_schema | list[PropertyType] | 入力パラメータ定義 |
| effect | ActionEffect | enum: CREATE / UPDATE / STATE_TRANSITION |
| preconditions | list[str] | 前提条件式（評価は U4 が担当） |

### OntologyObject（汎用インスタンス）
| フィールド | 型 | 説明 |
|---|---|---|
| object_type | str | 型名（TypeRegistry に存在必須） |
| id | str | id_property の値（UUID 文字列を既定） |
| properties | dict[str, Any] | プロパティ値（型定義に整合必須） |

### TypeRegistry
- 登録済 ObjectType/LinkType/ActionType のインメモリ索引（起動時に TypeRegistryPort.load_all で構築）。
- `get_object_type(name)`, `list_object_types()`, `get_link_type(name)`, `links_from(type)`, `get_action_type(name)`。

## 関係（ER 概念図, テキスト）
```
ObjectType 1───* PropertyType
ObjectType 1───* LinkType (source)        ActionType *───1 ObjectType (target)
LinkType  *───1 ObjectType (target)       ActionType 1───* PropertyType (input_schema)
OntologyObject *───1 ObjectType (object_type)
TypeRegistry 1───* {ObjectType, LinkType, ActionType}
```

## バージョニング
- MVP: なし。型は名前で一意、更新は上書き。`unit-of-work.md` の将来拡張に versioning を残す。
