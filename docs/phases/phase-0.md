# Phase 0 Report — Planning & Architecture

## What Was Built

- Analyzed all three specification documents: `PROJECT_ASSIGNMENT.md`, `CLAUDE.md`, `TASKS.md`
- Produced MUST-HAVE vs NICE-TO-HAVE requirement breakdown
- Designed high-level MVP architecture
- Defined implementation roadmap (12-day plan)
- Identified premature/overly complex tasks in TASKS.md
- Scaffolded full repository structure (`backend/`, `frontend/`, `docs/`)
- Created placeholder `PROJECT_REPORT.md` and `AI_TOOLING_REPORT.md`
- Updated `CLAUDE.md` with phase documentation requirements

---

## Key Decisions

### Single LangGraph graph (not multi-graph)

**Decision:** One central orchestration graph with an intent router dispatching to capability nodes.

**Rationale:** Simpler to debug, sufficient for the project scope, and directly matches the architecture diagram in PROJECT_ASSIGNMENT.md. Multi-graph patterns (supervisor + sub-graphs) add complexity without benefit at this stage.

**Tradeoff:** Less flexible for future multi-agent collaboration, but easier to reason about and test.

---

### Qdrant local via Docker (not Pinecone cloud)

**Decision:** Run Qdrant locally in Docker rather than use Pinecone.

**Rationale:** No API key or cloud account needed. Qdrant's Python client is straightforward. Local instance is sufficient for this project's data volume.

**Tradeoff:** Requires Docker to be running; no managed backup. Acceptable for a course project.

---

### DuckDuckGo for web search (no API key)

**Decision:** Use the `duckduckgo-search` Python package for the research agent and search tool.

**Rationale:** Free, no registration, works out of the box.

**Tradeoff:** Rate-limited and occasionally unreliable; not suitable for production. Fine for a demo project.

---

### Skip Calendar and Email tools

**Decision:** Implement only Weather, Search, and Notes for tool calling (the required minimum of 3).

**Rationale:** Calendar and Email require OAuth flows that add significant complexity with no academic credit — the assignment only requires 3 tools.

**Tradeoff:** Reduced "Chief of Staff" realism, but scope-appropriate.

---

### nomic-embed-text for embeddings (local via Ollama)

**Decision:** Use `nomic-embed-text` served by Ollama for all vector embeddings.

**Rationale:** Fully local, no API key, 768-dimensional output compatible with Qdrant, already pulled.

**Tradeoff:** Lower quality than OpenAI `text-embedding-3-large`, but sufficient for this project.

---

### qwen3:8b as primary LLM

**Decision:** Use `qwen3:8b` (already installed) as the primary reasoning engine.

**Rationale:** Fits in 8 GB VRAM, strong instruction following, native tool-calling support, built-in reasoning mode. See [phase-1.md](phase-1.md) for full rationale.

**Tradeoff:** Slower than cloud APIs (~34 tok/s), but private and free.

---

## Architecture Overview

```
User
 └─> Next.js (chat UI, file upload)
       └─> FastAPI (/chat, /upload, /documents, /tools)
             └─> LangGraph (single orchestration graph)
                   ├─> Intent Router
                   ├─> RAG Node       → Qdrant + nomic-embed-text
                   ├─> Tool Node      → Weather / DuckDuckGo / Notes
                   ├─> Memory Node    → PostgreSQL (short-term) + Qdrant (long-term)
                   ├─> SQL Node       → PostgreSQL (read-only, validated)
                   ├─> Research Node  → DuckDuckGo + summarise + cite
                   └─> Response Node  → Pydantic-validated structured output
                         └─> Ollama → qwen3:8b
```

---

## Repository Structure

```
.
├── CLAUDE.md
├── TASKS.md
├── backend/
│   ├── api/            # FastAPI routers and endpoint definitions
│   ├── agents/         # LangGraph agent definitions
│   ├── graph/          # LangGraph graph assembly and state
│   ├── tools/          # Tool implementations (weather, search, notes)
│   ├── rag/            # Document ingestion and retrieval pipeline
│   ├── memory/         # Short-term and long-term memory
│   ├── services/       # Business logic layer (called by tools/agents)
│   ├── db/             # SQLAlchemy models, Alembic migrations, session management
│   ├── schemas/        # Pydantic request/response models
│   └── tests/          # pytest test suite
├── frontend/
│   ├── app/            # Next.js App Router pages
│   ├── components/     # Reusable React components
│   ├── hooks/          # Custom React hooks
│   └── lib/            # API client, utilities
└── docs/
    ├── PROJECT_REPORT.md
    ├── AI_TOOLING_REPORT.md
    └── phases/         # Per-phase reports (this directory)
```

---

## Implementation Roadmap

| Phase | Focus | Key Deliverable |
|---|---|---|
| 0 | Planning & architecture | This document |
| 1 | Local LLM setup | qwen3:8b + nomic-embed-text verified |
| 2 | Backend foundation | FastAPI + PostgreSQL + health endpoint |
| 3 | Basic chat | Streaming chat UI end-to-end |
| 4 | LangGraph foundation | Typed graph state + core nodes |
| 5 | RAG system | PDF upload → chunk → embed → retrieve |
| 6 | Tool calling | Weather + Search + Notes tools |
| 7 | Structured outputs | MeetingSummary schema + retry |
| 8 | Memory system | Conversation + long-term user prefs |
| 9 | Research agent | Search → read → summarise → cite |
| 10 | SQL agent | NL → validated SQL → explain |
| 11 | Multi-capability integration | Intent router wires all nodes |
| 12 | Frontend completion | Full UI polish |
| 13 | Testing & evaluation | pytest suite + latency benchmarks |
| 14 | Documentation | Final PROJECT_REPORT.md |

---

## Tasks Identified as Premature or Overly Complex

| Task | Reason |
|---|---|
| Phase 0 architecture diagram | Premature before any code exists; sketch only |
| Evaluate all 4 LLM candidates | Pick based on hardware and move on |
| Reranking in Phase 5 | Stretch goal; get basic retrieval working first |
| Phase 11 as a separate phase | It's the integration result of Phases 4–10, not new code |
| Phase 13 latency benchmarks | Only meaningful after the system works end-to-end |
| vLLM runtime evaluation | Requires Linux + GPU server; Ollama is sufficient |
| Calendar + Email tools | OAuth complexity not worth it for 3-tool minimum |

---

## Reflection Questions

Phase 0 has no formal reflection questions in PROJECT_ASSIGNMENT.md. The planning decisions above serve as the equivalent.

---

## AI Tooling Used

| Tool | Used For | Output Quality | Corrections Needed |
|---|---|---|---|
| Claude Code (claude-sonnet-4-6) | Full phase: requirement analysis, architecture design, TASKS.md critique, roadmap, repo scaffold | High | Model recommendation self-corrected from qwen3:4b to qwen3:8b after hardware check |

---

## Claude Code Token Usage

> Run `/usage` in Claude Code at the end of the phase and paste the output below.

| Metric | Value |
|---|---|
| Input tokens | — |
| Output tokens | — |
| Cache read tokens | — |
| Cache write tokens | — |
| Total cost (USD) | — |
| Total API duration | — |
