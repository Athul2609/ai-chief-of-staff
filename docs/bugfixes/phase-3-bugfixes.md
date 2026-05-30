# Phase 3 — Bug Fixes Found During End-to-End Test

Bugs discovered while using `playwright-cli` to test the chat UI end-to-end after Phase 3 was built, plus one startup issue found when running the app for the first time after the phase was complete.

---

## Bug 1 — Timezone-aware datetime rejected by asyncpg

**File:** `backend/services/chat.py`

**Symptom:**
`POST /chat/` returned HTTP 500 on every request. Browser showed a CORS error (which was a red herring — the 500 prevented CORS headers from ever being set).

**Root cause:**
The `Conversation` and `Message` models use SQLAlchemy `DateTime` columns, which map to PostgreSQL `TIMESTAMP WITHOUT TIME ZONE`. asyncpg rejects timezone-aware Python datetimes when inserting into naive timestamp columns because it tries to subtract the UTC offset, which is undefined for naive types.

The service was passing `datetime.now(timezone.utc)` — a timezone-aware datetime — into that column.

**Error:**
```
asyncpg.exceptions.DataError: invalid input for query argument $2:
datetime.datetime(..., tzinfo=datetime.timezone.utc)
(can't subtract offset-naive and offset-aware datetimes)
```

**Fix:**
```python
# Before
from datetime import datetime, timezone
created_at=datetime.now(timezone.utc)

# After
from datetime import datetime
created_at=datetime.utcnow()
```

**Why `utcnow()`:** The column is `TIMESTAMP WITHOUT TIME ZONE`, so it expects a naive datetime. `utcnow()` returns a naive UTC datetime, which asyncpg accepts directly.

**Note:** `utcnow()` is deprecated in Python 3.12+. The correct long-term fix is to change the column type to `TIMESTAMP WITH TIME ZONE`, which accepts timezone-aware datetimes. Deferred to a later refactor.

---

## Bug 2 — CORS headers missing on StreamingResponse

**File:** `backend/api/chat.py`

**Symptom:**
After fixing Bug 1, the endpoint returned 200 but the browser still blocked the request:
```
Access to fetch at 'http://localhost:8000/chat/' from origin 'http://localhost:3000'
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
on the requested resource.
```

**Root cause:**
FastAPI's `CORSMiddleware` reliably adds `Access-Control-Allow-Origin` to standard `JSONResponse` and `Response` objects. However, with `StreamingResponse`, the middleware sometimes does not inject the header — particularly when the response body is a generator. This is a known Starlette behaviour where the middleware cannot modify response headers once the stream has started sending.

**Fix:**
Add the `Access-Control-Allow-Origin` header explicitly on the `StreamingResponse`:

```python
# Before
return StreamingResponse(
    event_stream(),
    media_type="text/event-stream",
    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
)

# After
return StreamingResponse(
    event_stream(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
        "Access-Control-Allow-Origin": "http://localhost:3000",
    },
)
```

**Note:** This hardcodes the allowed origin to `localhost:3000`. In production this should be driven by a config value.

---

## Bug 3 — qwen3:8b thinking tokens leaking into response

**File:** `backend/api/chat.py`

**Symptom:**
The model's internal reasoning was appearing in the chat UI as part of the response:
```
$ <think> Okay, the user is asking what courses they're enrolled in...
...
</think> I can't access your course enrollment information directly...
```

**Root cause:**
`qwen3:8b` has a built-in "thinking mode" that emits `<think>...</think>` blocks before the final answer. When `ChatOllama` streams the response, these thinking tokens are included in `chunk.content` by default.

**Fix:**
Pass `think=False` to `ChatOllama` to disable thinking mode:

```python
# Before
llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)

# After
llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url, think=False)
```

**Trade-off:** Disabling thinking mode reduces reasoning quality slightly on complex tasks but is the right default for a chat assistant where the user should only see the final answer. Thinking mode can be re-enabled selectively in future phases (e.g. for the research agent).

---

## Bug 4 — uvicorn fails to start when run from project root

**File:** N/A (startup command / developer workflow)

**Symptom:**
Running the backend from the project root with `uvicorn backend.main:app` crashed immediately:
```
ModuleNotFoundError: No module named 'api'
```

**Root cause:**
`backend/main.py` uses bare imports — `from api.chat import router`, `from config import get_settings`, etc. These resolve correctly when Python's working directory is `backend/`, because `backend/` is on `sys.path`. When running `uvicorn backend.main:app` from the project root, Python imports `backend.main` as a package module but does NOT add `backend/` to `sys.path`, so `api`, `config`, and other sibling modules are not found.

**Fix:**
Always run uvicorn from inside `backend/` using the unqualified module name:

```powershell
# Wrong — run from project root
uvicorn backend.main:app --port 8000

# Correct — run from backend/
cd backend
uvicorn main:app --port 8000
```

The full venv-path version (for when the venv isn't activated):
```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Alternative fix (not applied):** Add `sys.path.insert(0, os.path.dirname(__file__))` at the top of `main.py`. Not applied because it's a hack that masks the real issue and breaks if the file moves.

Documented in `docs/running.md` under Common Problems.

---

## Summary

| # | File | Issue | Fix |
|---|---|---|---|
| 1 | `services/chat.py` | Timezone-aware datetime rejected by asyncpg | Use `datetime.utcnow()` instead of `datetime.now(timezone.utc)` |
| 2 | `api/chat.py` | CORS headers not applied to `StreamingResponse` | Add `Access-Control-Allow-Origin` header explicitly |
| 3 | `api/chat.py` | qwen3 thinking tokens leaking into UI | Pass `think=False` to `ChatOllama` |
| 4 | startup | `ModuleNotFoundError: No module named 'api'` when running from project root | Run `uvicorn main:app` from inside `backend/` |
