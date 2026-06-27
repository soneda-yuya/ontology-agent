# U2 Permission — Domain Entities

技術非依存。中央集権 PermissionGateway の判定に必要なモデル。

## エンティティ

### Principal（呼び出し主体）
| フィールド | 型 | 説明 |
|---|---|---|
| id | str | ユーザーID（AI クライアントは代理ユーザーの id を引き継ぐ） |
| roles | tuple[str, ...] | 例: ("cs",), ("pm","sales") |
| attributes | dict[str, tuple[str, ...]] | 例: {"department": ("sales",), "territory": ("apac",)} |

> attributes は **認証時(U6)に解決して載せる**（U2 は受け取って評価, Q-P4=A）。

### Operation（操作種別）
`READ` / `WRITE` / `ADMIN`。U1 の authorize フックの operation 文字列を写像:
| U1 hook operation | Operation |
|---|---|
| get_object / search / aggregate / traverse | READ |
| put_object / invoke_action | WRITE |
| register_type | ADMIN |

### Effect
`ALLOW` / `DENY`。

### AttributePredicate（行レベル条件, Q-P1=A）
| フィールド | 型 | 意味 |
|---|---|---|
| object_property | str | 対象オブジェクトの属性名（例: "department"） |
| principal_attribute | str | principal.attributes のキー（例: "department"） |

判定: `object[object_property] ∈ principal.attributes[principal_attribute]`。

### PermissionRule
| フィールド | 型 | 説明 |
|---|---|---|
| role | str | 対象ロール |
| object_type | str | 対象 ObjectType（`*` で全型） |
| operation | Operation | 対象操作 |
| effect | Effect | ALLOW / DENY |
| row_predicate | AttributePredicate \| None | None=行制約なし（型レベル許可） |

### PermissionPolicy
- ルールの集合（`list[PermissionRule]`）。PolicyStorePort からロード。

### AccessDecision
| フィールド | 型 |
|---|---|
| allowed | bool |
| reason | str（監査・デバッグ用。PII を含めない） |

### AccessConstraint（クエリ用の行フィルタ表現）
判定の "クエリ版"。U3 がこれを SQL に落とす（U2 は表現のみ定義）。
| 種別 | 意味 |
|---|---|
| UNCONSTRAINED | 全行可（型が shared、または無条件 ALLOW） |
| NONE | 0 行（拒否） |
| predicates: list[AttributePredicate] | これらの OR を満たす行のみ可 |

### SharingLevel（U1 ObjectType への後方互換追加）
`SHARED` / `RESTRICTED`（既定=RESTRICTED=安全側）。
- SHARED: 行制約なし（チーム既定共有のコンテキスト型）。
- RESTRICTED: ロールの ALLOW ルール＋行述語に従う（業務型）。
- **U1 変更**: `ObjectType.sharing_level: SharingLevel = RESTRICTED` を追加（任意・既定値ありで round-trip 維持）。

## 関係（テキスト）
```
PermissionPolicy 1───* PermissionRule *───0..1 AttributePredicate
Principal (roles, attributes)  ──評価──>  PermissionRule  ──>  AccessDecision / AccessConstraint
ObjectType.sharing_level  ──>  SHARED は行制約バイパス
```
