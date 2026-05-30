# Phase 3 Report — Basic Chat Application

## What Was Built

- **`Conversation` and `Message` ORM models** — `backend/db/models.py` extended with two new tables tracking chat sessions and per-message history; Alembic migration generated and applied.
- **`backend/services/chat.py`** — service layer for conversation CRUD: `get_or_create_conversation`, `get_conversation_messages`, `save_message`. All async, typed, keeps agents and API handlers thin.
- **`backend/api/chat.py`** — two endpoints:
  - `POST /chat/` — accepts a message and optional `session_id`, loads history, streams the LLM response as Server-Sent Events, saves both turns to the DB.
  - `GET /chat/{session_id}/messages` — returns the full conversation history for a session.
- **`backend/schemas/chat.py`** — Pydantic models: `ChatRequest`, `MessageSchema`, `ConversationHistory`.
- **Frontend: retro terminal chat UI** — Next.js 16 app at `frontend/` with:
  - `app/page.tsx` — full-page terminal layout: boot-sequence header, scrolling message log, amber prompt input, streaming cursor blink.
  - `hooks/useChat.ts` — `useChat` hook managing SSE connection, message accumulation, session persistence, and the `[NEW SESSION]` clear action.
  - `app/globals.css` — Tailwind v4 CSS variables for the terminal colour palette (`terminal-bg`, `terminal-green`, `terminal-amber`, `terminal-dim`, `terminal-border`).
- **Three post-integration bug fixes** — timezone-aware datetime rejection, CORS on `StreamingResponse`, and `qwen3:8b` thinking-token leak. Documented in `docs/bugfixes/phase-3-bugfixes.md`.

---

## Key Decisions

### Server-Sent Events for streaming

**Decision:** Stream the LLM response as SSE (`text/event-stream`) rather than WebSocket or polling.

**Rationale:** SSE is unidirectional server-to-client, which is exactly the shape of a streaming LLM response. It works over plain HTTP, requires no upgrade handshake, and is natively supported by the browser `EventSource` API. WebSocket adds bidirectional complexity that adds nothing here.

**Tradeoff:** SSE cannot stream data from client to server. If a future phase needs bidirectional streaming (e.g., voice), a WebSocket upgrade would be required then.

---

### Separate `AsyncSessionLocal` for the post-stream DB write

**Decision:** In `api/chat.py`, the assistant reply is saved using a fresh `AsyncSessionLocal()` session opened inside `event_stream()`, rather than reusing the request's `get_db()` session.

**Rationale:** The FastAPI `get_db()` dependency session is tied to the request lifecycle. Once the `StreamingResponse` generator yields the first chunk, FastAPI considers the request "done" and the dependency teardown (commit/close) may run before the stream finishes. Opening a new session inside the generator avoids the race.

**Tradeoff:** Two DB sessions per request instead of one. Acceptable at this scale; a future refactor could use a connection pool callback instead.

---

### `think=False` on `ChatOllama`

**Decision:** Disable `qwen3:8b`'s built-in thinking mode at the LLM call site.

**Rationale:** `qwen3:8b` emits `<think>...</think>` reasoning blocks before its answer. These are streamed as regular `chunk.content` tokens and appear verbatim in the chat UI if not suppressed.

**Tradeoff:** Slightly reduced reasoning quality on complex multi-step tasks. Acceptable for a chat assistant; thinking mode can be selectively re-enabled for the research agent in a later phase.

---

### Retro terminal aesthetic for the frontend

**Decision:** Style the chat UI as a monochrome green-on-black terminal rather than a conventional chat bubble layout.

**Rationale:** The assistant is called "AI Chief of Staff" and targets a technical user (CS student). A terminal aesthetic reinforces that identity, is trivial to style with Tailwind v4 CSS variables, and has zero layout complexity — no avatar images, no bubble sizing, no scroll anchoring edge cases.

**Tradeoff:** Not accessible for non-technical users. Acceptable given the target audience.

---

## Reflection Questions

*(Mapping to PROJECT_ASSIGNMENT.md Phase 2 — Basic Chat Application)*

### 1. How is the chat state maintained?

State lives in two places:

- **Server (PostgreSQL):** Every user message and assistant reply is persisted in the `messages` table, keyed by `session_id`. On each request, the full history is loaded and converted to a LangChain message list before the LLM call, giving the model access to prior turns.
- **Client (React state):** The `useChat` hook holds the current message list in local state for rendering, and persists the `session_id` to `localStorage` so the session survives page refreshes. On mount, the hook fetches history from `GET /chat/{session_id}/messages` to re-populate the UI.

The approach is stateless on the server side per request — no in-memory session cache — which makes the backend horizontally scalable.

---

### 2. What challenges arise when using smaller open-source models?

Three concrete issues encountered with `qwen3:8b`:

- **Thinking token leakage:** The model emits internal `<think>...</think>` reasoning before answering. These tokens stream out just like answer tokens and rendered directly in the UI. Fixed by passing `think=False`.
- **Instruction following:** Smaller models tend to ignore system prompt constraints (e.g., "be concise and direct") more frequently than GPT-4-class models. The model sometimes produces long preamble paragraphs before reaching the point.
- **Latency:** On CPU-only inference, a 200-token response takes 10–20 seconds. This is why streaming matters — the user sees tokens appear incrementally rather than waiting for the full response.

---

### 3. What prompt engineering techniques improved results?

- **Persona anchoring:** The system prompt names the student ("Alex Johnson") and lists specific capabilities ("academic questions, deadlines, grades, research, and general advice"). Named context reduces generic off-topic responses.
- **Explicit brevity instruction:** "Be concise and direct" reduced multi-paragraph filler, though not completely.
- **Honest uncertainty:** "When you don't know something, say so" reduced hallucinated specifics (the model was inventing course grades before the SQL agent is wired up).

---

## Observations & Limitations

- **CORS and `StreamingResponse`:** FastAPI's `CORSMiddleware` does not reliably inject `Access-Control-Allow-Origin` on `StreamingResponse` because the middleware cannot modify headers once the stream has started flushing. The header must be set explicitly on the `StreamingResponse` object. This is a known Starlette limitation.

- **`datetime.utcnow()` vs `datetime.now(timezone.utc)`:** asyncpg rejects timezone-aware Python datetimes when inserting into `TIMESTAMP WITHOUT TIME ZONE` columns. `datetime.utcnow()` returns a naive UTC datetime that asyncpg accepts. Note that `utcnow()` is deprecated in Python 3.12+ — the correct long-term fix is to use `TIMESTAMP WITH TIME ZONE` columns, which accepts aware datetimes correctly.

- **No SQL agent yet:** The LLM has no access to the PostgreSQL data (grades, courses, assignments). All questions about academic data are answered from general knowledge — meaning hallucinated. This is the primary limitation of Phase 3 and the motivator for the SQL agent in a later phase.

- **Single-user assumption:** The chat has no authentication. Any client can supply any `session_id` and read back that session's history. This is acceptable for a local dev prototype with one student, but would be a critical flaw in a multi-user deployment.

- **uvicorn must be run from `backend/`:** `backend/main.py` uses bare imports (`from api.chat import router`), not package-relative imports. Running `uvicorn backend.main:app` from the project root fails because `api` is not importable from the root. The correct command is `uvicorn main:app` run from inside `backend/`. Documented in `docs/running.md`.

---

## AI Tooling Used

| Tool | Used For | Output Quality | Corrections Needed |
|---|---|---|---|
| Claude Code (claude-sonnet-4-6) | Full phase implementation: ORM models, service layer, streaming API, Next.js frontend, Tailwind v4 CSS variables, bug diagnosis | High | Three bugs required post-integration fixes (timezone datetime, CORS on StreamingResponse, thinking token leakage); all were caught via Playwright end-to-end testing |
| playwright-cli skill | End-to-end testing of the chat UI after integration — drove the browser, sent messages, observed streaming output | High | N/A — used as a verification tool |

---

## Claude Code Token Usage

Run `/usage` in Claude Code at end of phase and record output here.

---
