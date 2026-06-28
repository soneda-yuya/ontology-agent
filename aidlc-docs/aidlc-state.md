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
  - [x] Functional Design (approved)
  - [x] NFR Requirements (approved; small scale, JSONB single table, in-memory registry, p95<100ms, Hypothesis)
  - [x] NFR Design (approved; fail-closed no-retry, tx boundary, no read cache, parameterized, PII redaction)
  - [x] Infrastructure Design (lean) (approved/merged)
  - [x] Code Generation (implemented — awaiting approval; src/mini_aip U1, 30 unit+PBT tests pass, ruff clean)
- **U2 Permission**
  - [x] Functional Design (approved; attribute-match predicates, deny-by-default + explicit-deny-wins, ObjectType.sharing_level shared/restricted, principal carries attributes)
  - [x] NFR Requirements (approved; in-memory policy load, decide p95<5ms, inherits U1/shared)
  - [x] NFR Design (approved; pure-function decision core, deny-by-default resolution, fail-closed gateway, in-memory PolicyRegistry)
  - [x] Infrastructure Design (lean) (approved; inherits shared-infrastructure, adds policies table)
  - [x] Code Generation (implemented — awaiting approval; domain/permission, gateway, PostgresPolicyStore, secured container; 50 tests pass incl. integration, ruff clean; U1 sharing_level added backward-compatibly)
- **U5 Audit & Activity**
  - [x] Functional Design (approved; append-only + DB grants, Activity=significant actions/SHARED read, audit query governance-only, PII-free, fail-closed)
  - [x] NFR Requirements (approved; synchronous append for INV-2, retention >=90d, inherits U1/U2/shared)
  - [x] NFR Design (approved-batch; append-only ports, synchronous record, ref-only events, audit=RESTRICTED/activity=SHARED)
  - [x] Infrastructure Design (lean) (approved-batch; inherits shared, adds audit_events/activity_events tables, no UPDATE/DELETE grant)
  - [x] Code Generation (implemented — awaiting approval; domain/audit, AuditService/ActivityService/AuditAdapter, Postgres sinks, gateway deny-recording, secured container wiring; 61 tests pass incl. integration, ruff clean; U1/U2 non-regressed)
- **U3 Retrieval / RAG**
  - [x] Functional Design (approved; eq+comparison+contains filters, count/group_by/period aggregate, FileIndexPort+FTS, get returns None on row-deny/IDOR; row_constraint->SQL, audited)
  - [x] NFR Requirements (approved-batch; index-backed, FTS via tsvector, p95 targets, inherits)
  - [x] NFR Design (approved-batch; permission-before-IO, constraint->SQL, IDOR-hide, pure SqlSpecBuilder, audit wrap)
  - [x] Infrastructure Design (lean) (awaiting approval; inherits shared, adds file_index table + tsvector GIN)
  - [ ] Code Generation
- [ ] U4 Action, U6 MCP (pending)
- [ ] Build and Test
- Note: U2 adds `ObjectType.sharing_level` to U1 (backward-compatible, default RESTRICTED)

### 🟡 OPERATIONS PHASE
- [ ] (placeholder)

## Current Status
- **Lifecycle Phase**: INCEPTION (nearly complete)
- **Current Stage**: Units Generation complete — awaiting approval
- **Next Stage**: CONSTRUCTION — per-unit loop starting with U1 Ontology Core (Functional Design)
- **Design-First checkpoint**: pause before Code Generation
