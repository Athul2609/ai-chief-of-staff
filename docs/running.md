# Running the Application

This project has four services. Start them in order; stop them in reverse.

---

## Prerequisites

| Requirement | Check |
|---|---|
| Docker Desktop running | Open Docker Desktop and wait for the engine to start |
| Ollama installed | `ollama list` returns without error |
| `qwen3:8b` pulled | `ollama list` shows `qwen3:8b` |
| `nomic-embed-text` pulled | `ollama list` shows `nomic-embed-text` |
| Python venv exists | `.venv\Scripts\python.exe` is present |
| Node modules installed | `frontend\node_modules` exists |

First-time setup only:
```powershell
ollama pull qwen3:8b
ollama pull nomic-embed-text
cd frontend; npm install; cd ..
```

---

## Starting

### 1 — PostgreSQL (Docker)

```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose up -d
```

> If `docker` is on your PATH (it may not be by default on Windows): `docker compose up -d`

Verify: `docker compose ps` should show `chiefofstaff-postgres-1` as `running (healthy)`.

---

### 2 — Run database migrations

Only needed after pulling new code that adds migrations. Safe to run every time — it's a no-op if already up to date.

```powershell
cd backend
..\\.venv\Scripts\python.exe -m alembic upgrade head
cd ..
```

First time only — seed the database:
```powershell
cd backend
..\\.venv\Scripts\python.exe -m db.seed
cd ..
```

---

### 3 — Backend (FastAPI)

**Must be run from inside `backend/`** — the app uses bare imports (`from api.chat import router`) that only resolve when `backend/` is the working directory.

Open a dedicated terminal window and run:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify: `http://localhost:8000/health` should return:
```json
{"status":"ok","db":"ok","ollama":"ok","model":"qwen3:8b"}
```

API docs: `http://localhost:8000/docs`

---

### 4 — Frontend (Next.js)

Open a separate terminal window and run:

```powershell
cd frontend
npm run dev
```

Verify: open `http://localhost:3000` in a browser. You should see the retro terminal UI.

---

### 5 — Ollama (if not already running)

Ollama usually runs as a background service after installation. If the health check shows `"ollama":"error"`, start it manually:

```powershell
ollama serve
```

---

## Stopping

Stop in reverse order.

### 1 — Frontend

In the `npm run dev` terminal: `Ctrl+C`

### 2 — Backend

In the `uvicorn` terminal: `Ctrl+C`

If the terminal is gone and uvicorn is still running, find and kill it:

```powershell
# Find the PID listening on port 8000
netstat -ano | findstr ":8000"

# Kill it (replace 1234 with the actual PID)
Stop-Process -Id 1234 -Force
```

Or kill all Python processes (careful if you have other Python apps running):

```powershell
Get-Process python* | Stop-Process -Force
```

### 3 — PostgreSQL (Docker)

```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose down
```

This stops and removes the container but **preserves the data volume** (`postgres_data`). Your database survives.

To also delete all data (destructive — resets the database):

```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose down -v
```

### 4 — Ollama

If you started `ollama serve` manually:

```powershell
# Find the process
Get-Process ollama -ErrorAction SilentlyContinue

# Kill it
Get-Process ollama | Stop-Process -Force
```

If Ollama runs as a Windows service/system tray app, use the system tray icon to quit it.

---

## Port Reference

| Port | Service |
|---|---|
| 3000 | Next.js frontend |
| 8000 | FastAPI backend |
| 5432 | PostgreSQL |
| 11434 | Ollama |

---

## Common Problems

### `docker: command not found`

Docker isn't on your PATH. Use the full path:
```powershell
& "C:\Program Files\Docker\Docker\resources\bin\docker.exe" compose up -d
```

### `ModuleNotFoundError: No module named 'api'`

You ran uvicorn from the wrong directory. Always `cd backend` first, then run `uvicorn main:app` — not `uvicorn backend.main:app` from the project root.

### `[Errno 10048] only one usage of each socket address`

Port 8000 is already in use. Find and kill the process:
```powershell
netstat -ano | findstr ":8000"
Stop-Process -Id <PID> -Force
```

### CORS error in browser after backend returns 200

The `StreamingResponse` in `api/chat.py` must explicitly set `Access-Control-Allow-Origin`. This is already in the code — if you see this error after a code change, check that the header is still present on the `StreamingResponse`.

### Health check shows `"ollama":"error"`

Ollama is not running. Start it with `ollama serve`.

### Health check shows `"db":"error"`

PostgreSQL container is not running. Run `docker compose up -d` (or the full Docker path version above).
