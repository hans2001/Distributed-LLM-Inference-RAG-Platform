# Architecture (MVP Scope)

## Dataflow
1) Ingest
- Client → Gateway `/ingest` → Retrieval `/ingest` → PostgreSQL (pgvector)

2) Chat (RAG)
- Client → Gateway `/chat`
- Gateway → Orchestrator `/run`
- Orchestrator → Retrieval `/query`
- Orchestrator → vLLM `/v1/chat/completions`
- Orchestrator → Gateway → Client

## Mental Model (How to Think About the System)
- **Gateway is the front door**: a thin API layer for clients.
- **Orchestrator is the brain**: executes retrieve → generate → validate.
- **Retrieval is the memory**: vector search over pgvector.
- **Inference is the engine**: vLLM generates responses.
- **Pipelines are the factory**: batch ingest and indexing.
- **Observability is the dashboard**: traces + metrics for operations.

## Proven So Far
- End‑to‑end RAG works (`/ingest` → `/chat` with contexts).
- vLLM serving is live on GPU with a fit‑for‑VRAM model.
- Baseline p50/p95/QPS captured in `benchmarks/results.json`.
- Services are wired and observable (`/metrics` endpoints).

## Components
- **Gateway (FastAPI)**: Entry point for `/chat`, `/ingest`, `/health`, `/metrics`.
- **Retrieval (FastAPI + pgvector)**: Chunking + embeddings + vector search.
- **Orchestrator (LangGraph)**: retrieve → generate → validate graph with checkpointing.
- **Inference (vLLM)**: OpenAI-compatible LLM server.
- **Pipelines (Dagster)**: Batch ingest: load → chunk → embed → write.
- **Observability (OTel)**: Traces + metrics exported to Jaeger + Prometheus/Grafana.

## Scope Guardrails
- No frontend UI
- No auth
- No cloud deployment
- One observability stack (OTel + Jaeger + Prometheus/Grafana)
