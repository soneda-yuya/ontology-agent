# U3 Retrieval / RAG — NFR Design Patterns

U1/U2/U5 パターン + shared を継承。U3 固有。

## 権限・取得パターン
- **Permission-before-IO**: 必ず `authorize_query`/`authorize_object` を先に評価し、通過後のみ store へ（INV-1）。
- **Constraint→SQL translation**: `AccessConstraint`(U2) を JSONB 述語にコンパイル（`= ANY(%s)`）。`SqlSpecBuilder` に集約。
- **Aggregate population filtering**: 集計 SQL の WHERE に constraint+filters を適用し、母集団から権限外を除外（BR-R2）。
- **IDOR-hide**: get 不許可は None（存在秘匿, BR-R3）。

## 性能パターン
- **Index-backed**: 属性/集計は objects GIN、全文は file_index tsvector GIN。
- **Bounded results**: limit 既定 100。集計はサーバ側 GROUP BY。

## 安全性
- **Parameterized everywhere**: 値はすべてバインド（SECURITY-05）。列名/演算子は固定集合から選択（インジェクション不可）。
- **Validate inputs**: 不正な期間/演算子/型は検証エラー（BR-R8, SECURITY-15）。

## 監査
- **Audit wrap**: search/get/traverse/aggregate/file を U5 に記録（BR-R7）。

## テスト性
- **Pure SqlSpecBuilder**: FieldFilter+AccessConstraint→SqlSpec は純関数（テスト容易, TP-R2/R3）。
- round-trip（TP-R1）/ generators（PBT-07）。

## マッピング
| NFR | パターン |
|---|---|
| U3-7/8 権限/IDOR | Permission-before-IO + IDOR-hide |
| U3-1/2/3 性能 | Index-backed + bounded |
| U3-9 安全 | Parameterized + fixed operators + validate |
| U3-10 監査 | Audit wrap |

## Compliance Summary (NFR Design — U3)
- Security: SECURITY-08/05/15/03 をパターン化。ブロッキングなし。
- PBT: 純関数 SqlSpecBuilder + round-trip + generators。
