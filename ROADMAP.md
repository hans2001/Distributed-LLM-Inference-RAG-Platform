# Roadmap (Detailed, Scoped)

This roadmap stays intentionally small and production‑minded. Each milestone lists concrete outcomes so teams can track progress without bloating scope.

## Milestone 1 — Runtime & Serving
**Goal:** LLM serving is stable, fast, and measurable.
- [x] vLLM container wired in Docker Compose
- [ ] Start vLLM container and confirm model load
- [ ] Verify OpenAI‑compatible endpoints
  - `POST /v1/chat/completions`
  - `GET /v1/models`
- [ ] Baseline performance test (single user)
  - Capture p50/p95 latency and QPS
- [x] Document serving configuration knobs
  - model name, max tokens, batching settings

## Milestone 2 — Retrieval Foundation
**Goal:** Reliable vector storage + search.
- [x] pgvector schema defined in retrieval service
- [x] Ingest path implemented with chunking + embeddings
- [x] Query path implemented for top‑k retrieval
- [ ] Validate pgvector schema and connectivity
- [ ] Validate end‑to‑end ingest and query relevance
- [ ] Add idempotent inserts (doc_id + chunk_id)
- [ ] Add optional metadata fields (source, title, tags)

## Milestone 3 — Orchestration & Workflow
**Goal:** RAG flow is correct and recoverable.
- [x] Retrieve → generate → validate graph implemented
- [x] Checkpointing enabled (memory)
- [ ] Validate retrieve → generate → validate path
- [ ] Add checkpoint persistence and recovery test
- [ ] Add validation rules (length, structure, groundedness)
- [ ] Add retry policies for retrieve and generate steps

## Milestone 4 — Pipelines (Dagster)
**Goal:** Batch ingestion is reliable and auditable.
- [x] Dagster project scaffolded with ingest pipeline
- [x] Logging of indexed chunks implemented
- [ ] Run Dagster job from UI or CLI
- [ ] Add simple input adapters
  - local files
  - HTTP URL list
- [ ] Validate index count after job completion

## Milestone 5 — Gateway & API Contract
**Goal:** A stable, unified entry point.
- [x] `/chat` implemented (non‑streaming)
- [x] `/ingest` implemented (retrieval service)
- [x] `/health` and `/metrics` implemented
- [ ] `/chat` streaming passthrough
- [ ] Add request validation + error mapping

## Milestone 6 — Observability
**Goal:** End‑to‑end visibility.
- [x] OTel Collector + Jaeger + Prometheus + Grafana wired
- [x] Service metrics endpoints implemented
- [ ] Distributed tracing across gateway → orchestrator → retrieval → vLLM
- [ ] Prometheus metrics visible in Grafana
- [ ] Error rate and latency panels verified
- [ ] Token usage tracked at gateway (from LLM responses)

## Milestone 7 — Benchmarking
**Goal:** Repeatable performance report.
- [x] Benchmark script implemented
- [ ] Run benchmark script at fixed concurrency
- [ ] Store results in `benchmarks/results.json`
- [ ] Compare baseline vs tuned settings

## Milestone 8 — Lightweight GUI (Showcase)
**Goal:** Simple UI that demonstrates the workflow without expanding scope.
- [ ] Single‑page UI with three panels: Ingest, Chat, Observability links
- [ ] Chat response shows retrieved context (top‑k snippets)
- [ ] Display request latency from gateway response
- [ ] Keep UI optional and separate from core services

## Out‑of‑Scope (MVP Guardrails)
- Frontend UI
- Auth / RBAC
- Cloud deployment
- Multi‑tenant routing
