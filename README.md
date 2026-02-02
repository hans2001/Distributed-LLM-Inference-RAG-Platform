# Distributed LLM Inference & RAG Platform

## What this is
A cloud‑native, local MVP platform for production‑style GenAI workloads: low‑latency LLM serving, RAG, orchestration, and full observability. It’s designed as a reusable, open‑source reference stack that teams can adopt instead of building this infrastructure from scratch.

## Why we built it
Most teams don’t need a custom GenAI stack; they need a reliable, observable foundation they can plug into real products quickly. This project packages the essential building blocks—serving, retrieval, orchestration, and pipelines—into a single, coherent platform so teams can focus on business logic rather than rebuilding infrastructure.

## Who it’s for
- Engineering teams building internal LLM applications or enterprise AI services
- Platform teams who need a standard, reusable GenAI foundation
- OSS users who want a complete, runnable LLM + RAG stack

## Why it matters
- **Performance‑minded serving:** vLLM for dynamic batching and KV‑cache optimization
- **RAG done right:** embeddings + vector search with pgvector, plus orchestration
- **Operational discipline:** tracing + metrics via OpenTelemetry, Jaeger, Grafana
- **Production‑style pipelines:** Dagster with retries and logging

## Core capabilities
- **LLM Serving (vLLM):** OpenAI‑compatible API; concurrent inference and streaming.
- **RAG Pipelines (Dagster):** Chunk → embed → index into pgvector with retries + logging.
- **LangGraph Workflow:** retrieve → generate → validate with checkpointed state.
- **Unified Gateway (FastAPI):** `/chat`, `/ingest`, `/health`, `/metrics`.
- **Observability:** end‑to‑end tracing + latency/QPS metrics.

## How it’s built
- **Gateway:** FastAPI (`gateway/`)
- **Orchestrator:** LangGraph (`orchestrator/`)
- **Retrieval:** FastAPI + pgvector + PostgreSQL (`retrieval/`)
- **Inference:** vLLM OpenAI‑compatible server (`inference/`)
- **Pipelines:** Dagster (`pipelines/`)
- **Observability:** OTel Collector + Jaeger + Prometheus + Grafana (`infra/`)
- **Benchmarking:** load test script (`benchmarks/`)

## How to run (local)
1) Start services
```bash
docker compose up --build
```
2) Ingest a document
```bash
curl -X POST http://localhost:8000/ingest -H "Content-Type: application/json" -d '{"documents":[{"id":"doc1","text":"RAG systems combine retrieval and generation."}]}'
```
3) Chat with RAG
```bash
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{"messages":[{"role":"user","content":"What is RAG?"}],"top_k":4}'
```

## Observability (local)
- Jaeger: `http://localhost:16686`
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

## Use cases
- Internal knowledge assistant for enterprise docs and policies
- Support automation with grounded answers and auditability
- RAG‑powered search across product, legal, or engineering docs
- LLM reasoning workflows that require stepwise validation

## Docs
- `docs/ARCHITECTURE.md` — dataflow and component map
- `docs/DESIGN_DECISIONS.md` — tool choices and tradeoffs
- `docs/OBSERVABILITY.md` — tracing + metrics plan
- `docs/EVALUATION.md` — minimal RAG eval guidance
- `ROADMAP.md` — technical milestones (kept outside README)
