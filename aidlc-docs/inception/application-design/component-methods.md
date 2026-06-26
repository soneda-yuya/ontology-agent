# Component Methods — ontology-agent (Mini AIP)

> メソッドシグネチャと高レベル目的のみ。詳細ビジネスルールは Functional Design（per-unit）で定義。
> 表記は Python 風（型ヒント）。実際の型名は Functional Design で確定。

## PermissionGateway (C-A1)
```python
def authorize_query(principal: Principal, query: ObjectQuery) -> ObjectQuery
    # 型レベル可否を判定（不可なら deny）。row-level 制約を query に注入して返す。fail-closed。
def authorize_object(principal: Principal, object_type: str, obj_id: str) -> AccessDecision
    # 単一オブジェクトアクセスの可否（IDOR 防止, SECURITY-08）。
def authorize_action(principal: Principal, action: ActionProposal) -> AccessDecision
    # アクション実行権限の可否。
```

## OntologyService (C-A2)
```python
def register_type(principal: Principal, definition: ObjectTypeDef | LinkTypeDef | ActionTypeDef) -> TypeId
    # 型定義を検証し登録（ガバナンスロール限定）。監査記録。
def get_type(name: str) -> TypeDef
def list_types(kind: TypeKind) -> list[TypeDef]
```

## RetrievalService (C-A3)
```python
def search_objects(principal: Principal, query: ObjectQuery) -> list[OntologyObject]
    # authorize_query → ObjectStorePort.query → audit。権限通過分のみ返す。
def get_object(principal: Principal, object_type: str, obj_id: str) -> OntologyObject | None
    # authorize_object → store.get → audit。
def traverse_link(principal: Principal, start: ObjectRef, link: str, depth: int = 1) -> list[OntologyObject]
    # LinkType に従い探索。各到達要素を権限フィルタ。
def aggregate(principal: Principal, query: AggregateQuery) -> AggregateResult
    # count/group-by/期間集計。母集団は権限通過行のみ。PM/Sales 向け。
def semantic_search(principal: Principal, text: str, object_type: str | None) -> list[OntologyObject]
    # phase 2: VectorStorePort.search → 権限フィルタ → audit。
```

## ActionService (C-A4)
```python
def propose_action(principal: Principal, action_type: str, target: ObjectRef, inputs: dict) -> ActionProposal
    # 実行せず差分・前提条件を返す。authorize_action（提案権限）+ audit。
def invoke_action(principal: Principal, proposal_id: str, approval: Approval) -> ActionResult
    # 承認済提案のみ writeback。authorize_action + 前提条件再評価 + audit。
```

## AuditService (C-A5)
```python
def record(event: AuditEvent) -> None
    # 追記専用 sink へ書き込み（改変不可, SECURITY-14）。
def query_events(principal: Principal, filter: AuditFilter) -> list[AuditEvent]
    # ガバナンスロール限定の監査検索。
```

## Domain pure functions（PBT 対象候補）
```python
# Permission (C-D4)
def decide(principal, action, target_type, target_attrs) -> AccessDecision   # PBT-03 invariant: 明示deny → 必ず拒否
def row_constraint(principal, object_type) -> AccessConstraint
# Query (C-D3)
def build_sql(query: ObjectQuery, constraint: AccessConstraint) -> SqlSpec    # パラメタライズド（SECURITY-05）
# Ontology (C-D1/D2)
def serialize_type(def_: TypeDef) -> dict ; def deserialize_type(d: dict) -> TypeDef  # PBT-02 round-trip
```

## Ports（インターフェース・抜粋）
```python
class ObjectStorePort(Protocol):
    def query(self, spec: SqlSpec) -> list[OntologyObject]: ...
    def get(self, object_type: str, obj_id: str) -> OntologyObject | None: ...
    def aggregate(self, spec: AggregateSpec) -> AggregateResult: ...
    def write(self, obj: OntologyObject) -> None: ...        # action writeback
class VectorStorePort(Protocol):
    def upsert(self, ref: ObjectRef, embedding: list[float]) -> None: ...
    def search(self, embedding: list[float], k: int) -> list[ObjectRef]: ...
class PolicyStorePort(Protocol):
    def policies_for(self, role: str) -> list[PermissionPolicy]: ...
class TypeRegistryPort(Protocol):
    def load_all(self) -> list[TypeDef]: ...
    def save(self, def_: TypeDef) -> None: ...
class AuditSinkPort(Protocol):
    def append(self, event: AuditEvent) -> None: ...
    def query(self, filter: AuditFilter) -> list[AuditEvent]: ...
class AuthenticatorPort(Protocol):
    def authenticate(self, credential: str) -> Principal: ...   # 失敗時は拒否（SECURITY-08）
```
