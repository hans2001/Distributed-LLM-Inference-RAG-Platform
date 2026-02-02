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
