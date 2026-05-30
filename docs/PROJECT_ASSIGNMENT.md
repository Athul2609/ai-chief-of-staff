# Project Assignment: Build an Open-Source AI Chief of Staff

## Overview

In this project, you will design and build an **AI Chief of Staff** using modern open-source LLM infrastructure.

Unlike simple chatbot projects, this assignment focuses on building a production-style AI system capable of:

* Retrieval-Augmented Generation (RAG)
* Agent orchestration
* Tool calling
* Memory
* Workflow automation
* Structured outputs
* Database interaction
* Research workflows

The system must be built primarily using **open-source language models** and modern agent frameworks.

---

# Core Requirement

You are **NOT allowed to use proprietary LLMs as the primary reasoning engine**.

Your system must use one or more open-source models such as:

* Llama
* Qwen
* Gemma
* DeepSeek-R1

Serve the models using:

* [Ollama](https://docs.ollama.com?utm_source=chatgpt.com)
* [vLLM](https://docs.vllm.ai?utm_source=chatgpt.com)

Ollama provides a simple local runtime for models like Llama, Gemma, Qwen, and DeepSeek. ([Ollama][1])

vLLM is one of the most widely used open-source inference engines and provides an OpenAI-compatible serving API. ([vLLM][2])

---

# Required Technologies

Your project must include the following:

| Area                    | Required Technology                                                                          |
| ----------------------- | -------------------------------------------------------------------------------------------- |
| Agent Framework         | [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview?utm_source=chatgpt.com) |
| Open Source LLM Runtime | Ollama or vLLM                                                                               |
| Backend                 | FastAPI                                                                                      |
| Database                | PostgreSQL                                                                                   |
| Vector Database         | Pinecone or Qdrant                                                                           |
| Frontend                | Next.js / React                                                                              |
| Embeddings              | Open-source or OpenAI                                                                        |
| Orchestration           | LangGraph                                                                                    |

LangGraph is specifically designed for stateful agent orchestration and long-running workflows. ([docs.langchain.com][3])

---

# Project Goal

Build an AI assistant capable of:

```text
Answering questions

Searching documents

Performing research

Calling tools

Using memory

Querying databases

Automating workflows

Generating structured outputs
```

---

# High-Level Architecture

```text
User
 |
 v
Frontend
 |
 v
FastAPI Backend
 |
 v
LangGraph Agent
 |
 +-----------------------------+
 |             |               |
 v             v               v
RAG          Tools         Database
 |             |               |
 v             v               v
Vector DB    APIs         PostgreSQL
 |
 v
Open Source LLM
(Ollama / vLLM)
```

---

# Phase 1 — Local LLM Setup

## Objective

Run an open-source model locally.

---

## Requirements

Install:

* Ollama OR
* vLLM

Run at least one model:

```text
Llama

Qwen

Gemma

DeepSeek
```

---

## Deliverables

### Questions

1. Which model did you choose and why?
2. What hardware was required?
3. What limitations did you observe?
4. How did local inference compare with cloud inference?
5. What advantages does local inference provide?

---

# Phase 2 — Basic Chat Application

## Objective

Build a chat interface connected to your local model.

---

## Requirements

The system must:

* Accept user messages
* Stream responses
* Maintain conversation history

---

## Deliverables

### Questions

1. How is the chat state maintained?
2. What challenges arise when using smaller open-source models?
3. What prompt engineering techniques improved results?

---

# Phase 3 — Retrieval-Augmented Generation (RAG)

## Objective

Allow the assistant to answer questions using documents.

---

## Requirements

The system must:

* Upload files
* Chunk documents
* Generate embeddings
* Store vectors
* Retrieve context
* Answer using retrieved information

---

## Deliverables

### Questions

1. What chunking strategy did you choose?
2. How did retrieval quality affect answers?
3. What retrieval failures did you observe?
4. How could reranking improve performance?

---

# Phase 4 — Tool Calling

## Objective

Enable the model to interact with external systems.

---

## Required Tools

Implement at least three:

```text
Weather

Calendar

Notes

Search

Email Drafting

Task Creation
```

---

## Deliverables

### Questions

1. How are tools exposed to the LLM?
2. How does the model decide which tool to use?
3. What safety mechanisms are required?

---

# Phase 5 — Structured Outputs

## Objective

Convert unstructured text into structured information.

---

## Example

Input:

```text
Meeting transcript
```

Output:

```json
{
  "summary": "...",
  "action_items": [],
  "risks": [],
  "decisions": []
}
```

---

## Deliverables

### Questions

1. Why are structured outputs important?
2. How did you validate outputs?
3. What extraction errors occurred?

---

# Phase 6 — Memory System

## Objective

Implement persistent memory.

---

## Requirements

Store:

```text
User Preferences

Conversation History

Long-Term Notes
```

---

## Deliverables

### Questions

1. What should be stored in memory?
2. What should never be stored?
3. How is memory retrieved efficiently?

---

# Phase 7 — Web Research Agent

## Objective

Create an agent capable of conducting research.

---

## Example

```text
Research AI coding assistants
and summarize the market.
```

---

## Requirements

The agent must:

```text
Search

Read

Analyze

Summarize

Cite Sources
```

---

## Deliverables

### Questions

1. How did you evaluate source quality?
2. What hallucination risks exist?
3. How does research differ from standard RAG?

---

# Phase 8 — SQL Agent

## Objective

Allow natural language interaction with databases.

---

## Example

```text
How many applications were submitted this month?
```

---

## Requirements

The system must:

```text
Generate SQL

Validate SQL

Execute SQL

Explain Results
```

---

## Deliverables

### Questions

1. What security risks exist?
2. How did you validate generated SQL?
3. When should SQL generation be avoided?

---

# Phase 9 — LangGraph Agent Orchestration

## Objective

Build a multi-capability AI agent using LangGraph.

---

## Required Capabilities

The agent should decide whether to:

```text
Search Documents

Query Database

Use Memory

Search Web

Call Tools
```

---

## Example

```text
What decisions were made regarding hiring,
and how many candidates remain in the pipeline?
```

Expected behavior:

```text
Search Documents
      |
      v
Query Database
      |
      v
Combine Information
      |
      v
Generate Answer
```

---

## Deliverables

### Questions

1. Why is LangGraph useful compared to a single prompt?
2. What state must be maintained across agent steps?
3. What failure modes occur in multi-agent workflows?
4. How did you debug agent behavior?

---

# AI Development Tooling Report (Mandatory)

Modern AI engineers increasingly rely on AI-assisted development tools.

You must maintain a report documenting every AI tool used during development.

---

## Examples

Possible tools include:

* [Claude Code](https://www.anthropic.com/claude-code?utm_source=chatgpt.com)
* [GitHub Copilot](https://github.com/features/copilot?utm_source=chatgpt.com)
* MCP Servers
* Cursor
* Windsurf
* ChatGPT
* Aider
* Continue
* Roo Code
* Cline

---

## Required Report

Create a document named:

```text
AI_TOOLING_REPORT.md
```

For every tool used, document:

### Tool Name

Example:

```text
Claude Code
```

### Purpose

Example:

```text
Code generation
Debugging
Refactoring
Documentation
```

### Example Usage

Provide concrete examples:

```text
Generated FastAPI routes

Debugged LangGraph state transitions

Helped create SQL schemas
```

### Productivity Impact

Discuss:

```text
What became faster?

What became easier?

What became harder?
```

### Reliability Assessment

Evaluate:

```text
Accuracy

Hallucinations

Debugging usefulness

Code quality
```

---

# Final Technical Report

Create:

```text
PROJECT_REPORT.md
```

The report must include:

## Architecture

System diagrams.

## Model Selection

Why specific models were chosen.

## RAG Design

Chunking, retrieval, embeddings.

## Agent Design

LangGraph workflow explanation.

## Memory Design

Storage and retrieval.

## Tool Calling Design

Tool architecture.

## Challenges

Technical issues encountered.

## Performance Evaluation

Latency.

Cost.

Accuracy.

## Future Improvements

What would be improved next.

---

# Reflection Questions

1. What limitations did open-source models have compared to proprietary models?
2. What component was the most difficult to build?
3. What capability delivered the highest user value?
4. How did LangGraph change the architecture of the system?
5. What tradeoffs exist between local inference and hosted APIs?
6. Which AI development tools provided the greatest productivity improvement?
7. What parts of the application should remain deterministic rather than agent-driven?

---

# Success Criteria

A successful submission demonstrates practical understanding of:

* Open-source LLM deployment
* Ollama or vLLM serving infrastructure
* LangGraph orchestration
* RAG systems
* Embeddings
* Vector databases
* Tool calling
* Memory architectures
* Agent workflows
* SQL agents
* Workflow automation
* AI-assisted software development

The goal is not merely to build a chatbot, but to understand how modern AI products are architected, deployed, evaluated, and developed using both open-source LLM infrastructure and AI-native engineering workflows. ([docs.langchain.com][3])

[1]: https://docs.ollama.com/?utm_source=chatgpt.com "Ollama's documentation - Ollama"
[2]: https://docs.vllm.ai/?utm_source=chatgpt.com "vLLM"
[3]: https://docs.langchain.com/oss/python/langgraph/overview?utm_source=chatgpt.com "LangGraph overview - Docs by LangChain"
