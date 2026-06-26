# AI-DLC State Tracking

## Project Information
- **Project Name**: ontology-agent (Mini AIP)
- **Project Type**: Greenfield
- **Start Date**: 2026-06-26
- **Current Stage**: INCEPTION - Workflow Planning (awaiting approval)

## Execution Plan Summary
- **Stages to Execute**: Application Design, Units Planning, Units Generation, Functional Design, NFR Requirements, NFR Design, Infrastructure Design (lean), Code Generation, Build and Test
- **Stages to Skip**: Reverse Engineering (Greenfield)
- **Design-First checkpoint**: pause before Code Generation
- **Preliminary units**: U1 Ontology Core, U2 Permission, U3 Retrieval/RAG, U4 Action, U5 Audit, U6 MCP/API

## Scope Definition (agreed)
`Mini AIP = Ontology + RAG + Permission + Action execution + Audit log`
- Intended stack: Python (FastAPI + Pydantic), LLM = Claude
- Goal: design-document-first (設計ドキュメント先行)

### Scope Extension (2026-06-26): Context Hub / Memory Server
チーム共有のローカル・コンテキストハブとして再定義。各ユーザーのローカルAI（Claude Code/Cursor/Local LLM/自作Agent）のコンテキストを中央ハブ経由でチーム共有。
- 追加: 共有メモリ型（Memory/Note/Conversation/WorkSession/Project/Preference, データ駆動登録）、File index（U3）、Activity log（U5, Audit と分離）、3インターフェース（MCP+HTTP+CLI, U6）、AI=ユーザー代理 principal。
- 反映: requirements.md §11, personas.md P5, stories.md Feature H(US-H1..5), application-design.md, unit-of-work*.md。
- 影響: U1/U2 不変、U3/U5/U6 を追加拡張。作り直しなし（追加的）。

## Workspace State
- **Existing Code**: No (only `.aidlc-rule-details/` rules and `CLAUDE.md`)
- **Programming Languages**: None yet (intended: Python)
- **Build System**: None yet
- **Project Structure**: Empty
- **Reverse Engineering Needed**: No (Greenfield)
- **Workspace Root**: /Users/y.soneda/projects/yuya/ontology-agent

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only

## Extension Configuration
| Extension | Enabled | Mode | Decided At |
|---|---|---|---|
| Security Baseline | Yes | All rules blocking | Requirements Analysis |
| Property-Based Testing | Yes | Partial (PBT-02, 03, 07, 08, 09) | Requirements Analysis |

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection
- [ ] Reverse Engineering (N/A — Greenfield)
- [x] Requirements Analysis (approved)
- [x] User Stories (approved; 12 stories across 7 features, 4 personas)
- [x] Workflow Planning (approved)
- [x] Application Design (approved; Hexagonal, hybrid types, central permission gateway, port abstraction)
- [x] Units Planning (modular monolith, layer-based dirs, 6 units, dependency order)
- [x] Units Generation (3 artifacts created — awaiting approval; 6 units U1-U6)

### 🟢 CONSTRUCTION PHASE (per-unit loop, dependency order U1→U2→U5→U3→U4→U6)
- **U1 Ontology Core**
  - [x] Functional Design (awaiting approval)
  - [ ] NFR Requirements
  - [ ] NFR Design
  - [ ] Infrastructure Design (lean)
  - [ ] Code Generation (design-first checkpoint here)
- [ ] U2 Permission … U6 MCP (pending)
- [ ] Build and Test

### 🟡 OPERATIONS PHASE
- [ ] (placeholder)

## Current Status
- **Lifecycle Phase**: INCEPTION (nearly complete)
- **Current Stage**: Units Generation complete — awaiting approval
- **Next Stage**: CONSTRUCTION — per-unit loop starting with U1 Ontology Core (Functional Design)
- **Design-First checkpoint**: pause before Code Generation
