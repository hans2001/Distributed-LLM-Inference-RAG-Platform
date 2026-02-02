# Design Decisions (MVP Scope)

## Runtime
- **vLLM** for serving due to dynamic batching and KV-cache optimization.
- OpenAI-compatible API to keep clients and tooling standard.

## Retrieval
- **pgvector** for local, self-hosted vector search.
- **SentenceTransformers** for lightweight embeddings (local CPU-friendly).
- Simple fixed-size chunking to keep MVP deterministic.

## Orchestration
- **LangGraph** for stateful RAG workflows with checkpointing.
- Graph steps: retrieve → generate → validate.

## Pipelines
- **Dagster** for batch ingest with retries + logging.
- Minimal pipeline ops to avoid bloat; focused on correctness.

## Observability
- **OTel Collector** as single ingress for traces/metrics.
- **Jaeger** for traces, **Prometheus/Grafana** for metrics.

## Non-Goals (MVP)
- Multi-tenant auth
- Frontend UI
- Cloud deployment
- Multi-vector retrievers
