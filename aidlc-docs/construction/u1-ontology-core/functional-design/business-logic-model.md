# U1 Ontology Core — Business Logic Model

技術非依存のロジック。永続は ObjectStorePort/TypeRegistryPort 経由（U1 が定義）。

## L1. 型登録（register_type） — US-F1 / US-D2
```
入力: TypeDef（ObjectType | LinkType | ActionType）, principal
1. 認可: PermissionGateway.authorize（ガバナンスロール限定）  ← U2
2. 構造検証（validate_type_def, 下記 business-rules 参照）
3. 整合検証:
   - ObjectType: id_property/title_property/text_properties が properties に存在
   - REFERENCE プロパティの ref_object_type が登録済（または同一バッチ内）
   - LinkType: source_type/target_type が登録済、inverse_name が source 側で衝突しない
   - ActionType: target_type 登録済、input_schema 妥当
4. TypeRegistryPort.save(def) → TypeRegistry 再読込（索引更新）
5. AuditService.record(type_registered)  ← U5
出力: TypeId
失敗時: 検証エラーを返し保存しない（fail-closed, SECURITY-15）
```

## L2. 型取得（get_type / list_types）
- TypeRegistry の索引から返す（読み取り、検証なし=F4）。

## L3. オブジェクト整合チェック（validate_object）
```
入力: OntologyObject
1. object_type が TypeRegistry に存在
2. 各 required プロパティが存在
3. 各プロパティ値が data_type に整合（型変換規則は business-rules）
4. ENUM 値が enum_values に含まれる
5. REFERENCE 値が参照先 ObjectType の既存 id（存在チェックは ObjectStore 経由・任意）
=> 書き込み時のみ実行（F4=write-only）。Pydantic モデルを型定義から動的構築して検証。
```

## L4. シリアライズ / デシリアライズ（PBT-02 round-trip 対象）
```
serialize_type(TypeDef) -> dict        # 永続/転送用
deserialize_type(dict) -> TypeDef      # ロード用
不変条件: deserialize_type(serialize_type(t)) == t  （全 valid な t について）
serialize_object(OntologyObject) <-> deserialize_object
```

## L5. ハイブリッド検証の実装方針
- 型定義（データ）から **動的に Pydantic モデルを生成**し、書き込み時の OntologyObject を検証。
- 読み取りは検証しない（F4=A）。これにより題材追加時もコード変更不要（D2 ハイブリッド）。

## データフロー
```
register_type → validate → TypeRegistryPort.save → registry reload → audit
write object  → validate_object(動的Pydantic) → ObjectStorePort.write
read  type/obj → registry / ObjectStorePort（検証なし）
```

## エラーハンドリング
- 検証失敗: ドメイン例外（DomainValidationError）。サービス層で 4xx 相当に変換。
- 未知の型/プロパティ: 明示エラー（推測で通さない）。
- すべて fail-closed（保存・実行しない）。
