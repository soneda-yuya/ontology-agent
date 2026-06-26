# Unit of Work — Dependency Matrix

## 依存マトリクス（行 → 列に依存）
| ↓ \ → | U1 Ontology | U2 Permission | U3 Retrieval | U4 Action | U5 Audit | U6 MCP |
|---|---|---|---|---|---|---|
| **U1 Ontology** | – | – | – | – | – | – |
| **U2 Permission** | ✓(型参照) | – | – | – | – | – |
| **U3 Retrieval** | ✓ | ✓ | – | – | ✓ | – |
| **U4 Action** | ✓ | ✓ | – | – | ✓ | – |
| **U5 Audit** | – | ✓(検索の認可) | – | – | – | – |
| **U6 MCP** | ✓ | ✓ | ✓ | ✓ | ✓ | – |

- 循環依存なし。U1 が根、U6 が葉。
- すべて同一プロセス内呼び出し（同期）。外部 I/O は outbound adapter のみ。

## クリティカルパス / 並行化
- **クリティカルパス**: U1 → U2 →（U3, U4, U5 は U2/U1 完了後に並行可）→ U6。
- **並行化余地**: U3・U4・U5 は U1/U2 完了後に並行開発可能（U6 が全てを統合）。

## ビルド/依存方針
- 単一 `pyproject.toml`。依存は lock で固定（SECURITY-10）。
- ユニット間の直接 import を避け、ports/services 経由（境界保護）。
- テスト: ポートのモックでユニットを独立検証 → integration で結合。

## 開発順序（依存順・確定）
```
1. U1 Ontology Core      (基盤: 型・レジストリ・ObjectStore)
2. U2 Permission         (中央ゲート・ポリシー)        ← U1
3. U5 Audit              (追記専用 sink)               ← U2
4. U3 Retrieval/RAG      (検索・集計)                  ← U1,U2,U5
5. U4 Action             (提案・writeback)             ← U1,U2,U5
6. U6 MCP/API            (公開・認証・統合)            ← U1-U5
```
