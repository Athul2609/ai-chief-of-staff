# Phase 1 Report — Local LLM Setup

## What Was Built

- Confirmed Ollama v0.11.10 is installed and running on Windows 11
- Selected and verified `qwen3:8b` as the primary reasoning model
- Pulled `nomic-embed-text` as the embedding model for future RAG phases
- Verified inference via the Ollama REST API (`POST /api/generate`)
- Verified embeddings via `POST /api/embeddings`

## Key Decisions

### Model: qwen3:8b (not qwen3:4b)

**Decision:** Use `qwen3:8b` instead of the originally planned `qwen3:4b`.

**Rationale:** The GPU (RTX 4070 Laptop, 8 GB VRAM) has 7.5 GB free, and `qwen3:8b` at 5.2 GB fits comfortably with headroom for KV cache. The 8b model offers meaningfully better instruction following and tool-calling reliability than 4b, with no hardware penalty at this VRAM level.

**Tradeoff:** Slightly higher VRAM usage (~5.5 GB at runtime including KV cache) vs. better output quality and reasoning. Accepted.

---

### Embedding model: nomic-embed-text

**Decision:** Use `nomic-embed-text` via Ollama for all vector embeddings.

**Rationale:** Fully local, no API key required, 274 MB, and produces 768-dimensional embeddings compatible with Qdrant. Keeps the entire stack offline and free.

**Tradeoff:** Lower embedding quality than OpenAI `text-embedding-3-large`, but sufficient for this project's RAG needs.

---

### Runtime: Ollama (not vLLM)

**Decision:** Use Ollama exclusively. vLLM was not evaluated.

**Rationale:** vLLM requires Linux and a more complex setup. Ollama runs natively on Windows, has a simple REST API, and handles model management cleanly. No practical benefit from vLLM for this project.

**Tradeoff:** Slightly lower throughput than vLLM for batch inference. Not relevant for a single-user assistant.

---

## Reflection Questions

**1. Which model did you choose and why?**

`qwen3:8b`. Strong instruction following, native tool-calling support, and a built-in thinking/reasoning mode (`<think>` blocks). Fits within 8 GB VRAM with room to spare. The Qwen3 family also has good multilingual support and excels at structured output generation — both useful for this project.

**2. What hardware was required?**

NVIDIA RTX 4070 Laptop GPU (8 GB VRAM), Windows 11. The model runs entirely on-GPU with no CPU offload. Approximately 5.5 GB VRAM is consumed at runtime (model weights + KV cache for a typical context length).

**3. What limitations did you observe?**

- **Thinking mode latency:** qwen3:8b includes a chain-of-thought thinking step by default, visible as `<think>...</think>` blocks in the response. This adds 1–3 seconds of overhead on simple queries. We will use the `/no_think` pragma or `thinking: false` parameter for fast-path tool calls and simple responses.
- **Throughput:** ~34 tokens/sec on this hardware. Adequate for conversational use but noticeably slower than a cloud API (GPT-4o does ~80–100 tokens/sec).
- **Context window:** qwen3:8b supports up to 32k tokens, which is sufficient for most tasks but constrains large document RAG (need chunking).

**4. How did local inference compare with cloud inference?**

| Dimension | Local (qwen3:8b) | Cloud (e.g. GPT-4o) |
|---|---|---|
| Latency | ~1.5s TTFT, 34 tok/s | ~0.3s TTFT, 80–100 tok/s |
| Cost | $0 per query | ~$0.01–0.05 per query |
| Privacy | Full — data never leaves machine | Data sent to third party |
| Availability | Depends on local hardware | 99.9%+ uptime |
| Quality | Good for most tasks | Better on complex reasoning |

**5. What advantages does local inference provide?**

- **Privacy:** Sensitive documents and queries never leave the machine — critical for a "Chief of Staff" handling confidential information.
- **Cost:** Zero marginal cost per query. Important for high-volume agentic workflows that may make dozens of LLM calls per user request.
- **Offline capability:** Works without internet access.
- **Customization:** Models can be fine-tuned or system-prompted without vendor restrictions.
- **No rate limits:** No throttling during intensive workflows.

---

## Observations & Limitations

- The Ollama REST API is clean and OpenAI-compatible (`/v1/chat/completions`), which means LangChain's `ChatOllama` integration works out of the box.
- `qwen3max` (also installed) is a larger variant — we will use `qwen3:8b` as the primary model and can switch to `qwen3max` for complex reasoning tasks if VRAM allows after profiling.
- Thinking mode (`<think>` tokens) will need to be managed per-node in LangGraph. Fast nodes (routing, tool dispatch) should disable thinking; slow nodes (research, SQL explanation) can leave it on.

---

## Useful Commands

### Ollama status & model management

```bash
# Check running models and server status
ollama list

# Check if Ollama server is up
curl http://localhost:11434

# Show model details (size, parameters, quantization)
ollama show qwen3:8b
ollama show nomic-embed-text
```

### Running the LLM

```bash
# Interactive chat (with thinking mode)
ollama run qwen3:8b

# Interactive chat (disable thinking mode for faster responses)
ollama run qwen3:8b --nowordwrap
# Then type: /set parameter think false

# One-shot prompt via CLI
ollama run qwen3:8b "Summarise the key risks in this sentence: ..."

# One-shot via REST API (thinking ON, streaming OFF)
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:8b",
    "prompt": "What is the capital of France?",
    "stream": false
  }'

# One-shot via REST API (thinking OFF — faster for simple queries)
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:8b",
    "prompt": "/no_think What is the capital of France?",
    "stream": false
  }'

# OpenAI-compatible chat endpoint (used by LangChain ChatOllama)
curl -X POST http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3:8b",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### Using the embedding model

```bash
# Generate an embedding vector
curl -X POST http://localhost:11434/api/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "nomic-embed-text",
    "prompt": "The quick brown fox jumps over the lazy dog"
  }'

# nomic-embed-text produces 768-dimensional float vectors
# The response shape is: { "embedding": [float, float, ...] }  (768 values)
```

### Python usage (LangChain — used throughout this project)

```python
from langchain_ollama import ChatOllama, OllamaEmbeddings

# LLM (thinking mode off for fast responses)
llm = ChatOllama(model="qwen3:8b", base_url="http://localhost:11434", think=False)
response = llm.invoke("What is 2 + 2?")
print(response.content)

# LLM (thinking mode on for complex reasoning)
llm_think = ChatOllama(model="qwen3:8b", base_url="http://localhost:11434", think=True)

# Embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")
vector = embeddings.embed_query("Hello world")
print(len(vector))  # 768
```

---

## AI Tooling Used

| Tool | Used For | Output Quality | Corrections Needed |
|---|---|---|---|
| Claude Code (claude-sonnet-4-6) | Phase planning, requirement analysis, CLAUDE.md updates, documentation | High | Minor — model recommendation adjusted from qwen3:4b to qwen3:8b based on actual hardware check |

---

## Claude Code Token Usage

> Run `/usage` in Claude Code at the end of the phase and paste the output below.

| Metric | Value |
|---|---|
| Input tokens | 44 |
| Output tokens | 15,300 |
| Cache read tokens | — |
| Cache write tokens | — |
| Total cost (USD) | 0.86$ |
| Total API duration | — |
