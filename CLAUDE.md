# CLAUDE.md

## Git Workflow (MANDATORY)

Follow these rules for every commit and every phase.

### Branch strategy

- `main` is protected — never commit directly to it
- Every phase gets its own branch: `phase-N` (e.g. `phase-3`)
- Branch off `main` at the start of each phase: `git checkout -b phase-N`
- All work for a phase goes on that branch

### Commit message format (Conventional Commits)

```
<type>: <short description in imperative mood, under 72 chars>
```

Types:
- `feat` — new capability or endpoint
- `fix` — bug fix
- `chore` — config, deps, tooling, scaffolding
- `docs` — documentation only
- `refactor` — restructuring without behavior change
- `test` — adding or updating tests

Examples:
```
feat: add /chat endpoint with streaming SSE
fix: handle null score in grade calculation
chore: add qdrant service to docker-compose
docs: write phase-3 report
```

Rules:
- One logical change per commit — never batch unrelated changes
- Present tense, imperative mood ("add" not "added")
- Commit frequently throughout a phase, not all at once at the end

### End-of-phase PR workflow

1. All phase work is committed and pushed to `phase-N`
2. Open a PR from `phase-N` → `main` using `gh pr create`
3. Claude posts an automated review via GitHub Actions (requires `ANTHROPIC_API_KEY` secret)
4. User reviews the PR on GitHub
5. Any review fixes go as new commits on the same branch
6. User merges using **squash merge** (configured as the only merge strategy)
7. Branch is auto-deleted after merge
8. Write `docs/phases/phase-N.md` before opening the PR

### GitHub repo

- Remote: https://github.com/Athul2609/ai-chief-of-staff
- Default branch: `main`
- Merge strategy: squash merge only
- Branch auto-delete: enabled after merge

---

## Project Overview

This repository contains an implementation of an Open-Source AI Chief of Staff.

The system must satisfy the requirements defined in PROJECT_ASSIGNMENT.md.

Primary goals:

* Build a production-style AI assistant
* Use open-source LLMs as the primary reasoning engine
* Demonstrate LangGraph orchestration
* Implement RAG
* Implement tool calling
* Implement memory
* Implement SQL querying
* Implement research workflows
* Produce structured outputs
* Maintain clear separation between deterministic and agentic components

---

# Core Technology Stack

## Backend

* Python
* FastAPI
* LangGraph
* LangChain
* PostgreSQL
* SQLAlchemy
* Alembic

## Vector Database

Preferred:

* Qdrant

Alternative:

* Pinecone

## LLM Runtime

Preferred:

* Ollama

Supported Models:

* Qwen3
* DeepSeek-R1
* Llama 3.x
* Gemma

## Frontend

* Next.js
* React
* TypeScript
* Tailwind

---

# Architecture Principles

Follow these principles when generating code.

## 1. Keep Agents Thin

Agents should make decisions.

Agents should NOT:

* contain business logic
* contain database logic
* contain retrieval logic

Instead:

Agent -> Tool -> Service Layer

---

## 2. Deterministic First

Prefer deterministic implementations whenever possible.

Examples:

Good:

* SQL validation layer
* Typed schemas
* Structured outputs
* Explicit routing logic

Bad:

* Letting the LLM generate critical system behavior
* Using prompts instead of code validation

---

## 3. Strong Typing

Use:

* Pydantic models
* Typed state objects
* Explicit schemas

Avoid:

* dict[str, Any] unless necessary

---

## 4. Modular Design

Organize code by capability.

Example:

backend/
agents/
graph/
tools/
rag/
memory/
db/
services/
api/
schemas/

---

# Expected Repository Structure

backend/

```
api/
agents/
graph/
tools/
rag/
memory/
services/
db/
schemas/
tests/
```

frontend/

```
app/
components/
hooks/
lib/
```

docs/

PROJECT_REPORT.md
AI_TOOLING_REPORT.md

---

# LangGraph Design

Use a central orchestration graph.

Possible workflow:

User Request

↓

Intent Router

↓

Decision Node

↓

One or more:

* Memory Retrieval
* RAG Retrieval
* SQL Agent
* Research Agent
* Tool Execution

↓

Response Synthesis

↓

Output Validation

↓

Return Response

Graph state should be explicit and typed.

Never use unstructured graph state.

---

# RAG Requirements

Use:

* Semantic chunking when feasible
* Otherwise recursive chunking

Recommended:

Chunk Size: 500–1000 tokens

Overlap: 100–200 tokens

Store:

* document_id
* source
* page
* chunk_id

Always preserve metadata.

Implement:

* ingestion pipeline
* retrieval pipeline
* reranking layer

---

# Tool Calling Standards

Every tool must:

* Have a description
* Have typed inputs
* Have typed outputs
* Be independently testable

Required tools:

* Weather
* Notes
* Search

Additional tools:

* Task creation
* Calendar
* Email drafting

Never expose secrets to the model.

---

# Structured Output Standards

All structured outputs must use:

* Pydantic models
* Validation
* Retry on schema failure

Example:

MeetingSummary

* summary
* action_items
* risks
* decisions

Never trust raw LLM JSON.

---

# Memory Design

Memory categories:

## Short-Term

Conversation history

## Long-Term

User preferences

## Knowledge Notes

Saved facts and documents

Never store:

* passwords
* API keys
* secrets
* authentication tokens

Memory retrieval should use:

* vector search
* metadata filtering

---

# SQL Agent Rules

The SQL agent must:

1. Generate SQL
2. Validate SQL
3. Execute SQL
4. Explain results

Disallow:

* DROP
* DELETE
* UPDATE
* ALTER
* TRUNCATE

Read-only queries only.

Use schema-aware prompting.

---

# Research Agent Rules

Research workflow:

1. Search
2. Retrieve sources
3. Read
4. Summarize
5. Cite

Every factual claim should have a source.

Never present unsupported claims as facts.

---

# API Standards

Use:

* FastAPI routers
* Dependency injection
* Pydantic request models
* Pydantic response models

All endpoints must include:

* validation
* error handling
* logging

---

# Testing Standards

Write tests for:

* tools
* retrieval
* SQL generation
* memory
* graph routing

Prefer pytest.

Target:

> 80% coverage for backend logic.

---

# Observability

Implement:

* structured logging
* LangSmith tracing (optional)
* request IDs
* graph execution logs

Agent behavior must be debuggable.

---

# Documentation Requirements

Maintain:

* PROJECT_REPORT.md
* AI_TOOLING_REPORT.md

Whenever a major architectural decision is made:

Document:

* decision
* rationale
* tradeoffs

---

# Phase Completion Documentation (MANDATORY)

At the end of every phase, before moving to the next phase, create a phase report at:

```
docs/phases/phase-N.md
```

Where N is the phase number (e.g. `docs/phases/phase-1.md`).

Each phase report must include:

## What Was Built

A brief description of everything implemented in this phase.

## Key Decisions

Any technology choices, architecture decisions, or tradeoffs made. Include:

* Decision
* Rationale
* Tradeoff

## Reflection Questions

Answer every reflection question from PROJECT_ASSIGNMENT.md for this phase.

## Observations & Limitations

Anything unexpected, surprising, or worth noting for future phases.

## AI Tooling Used

Record every AI tool used in this phase:

* Tool name
* What it was used for
* Quality of output
* Any corrections needed

This feeds into the final AI_TOOLING_REPORT.md.

## Claude Code Token Usage

At the end of every phase, run `/usage` in Claude Code and record the output:

* Input tokens
* Output tokens
* Cache read tokens
* Cache write tokens
* Total cost (USD)
* Total API duration

This tracks the AI-assisted development cost and effort per phase.

This step is NOT optional. Do not proceed to the next phase without completing the phase report.

---

# AI Tooling Usage Log

Whenever AI assistance is used:

Record:

* Tool
* Task
* Output
* Validation performed

This information should be added to AI_TOOLING_REPORT.md.

---

# Code Generation Rules For Claude

When implementing features:

1. Create architecture first.
2. Create interfaces before implementations.
3. Create schemas before endpoints.
4. Create tests alongside code.
5. Avoid placeholder code.
6. Avoid TODO comments unless explicitly requested.
7. Explain architectural decisions.
8. Prefer maintainability over cleverness.
9. Produce production-quality code.
10. Keep files focused and reasonably sized.

If requirements are ambiguous:

* Propose options.
* Explain tradeoffs.
* Recommend one approach.
