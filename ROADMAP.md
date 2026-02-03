# Roadmap (Detailed, Scoped)

This roadmap stays intentionally small and production‑minded. Each milestone lists concrete outcomes so teams can track progress without bloating scope.

## Milestone 1 — Runtime & Serving
**Goal:** LLM serving is stable, fast, and measurable.
- [x] vLLM container wired in Docker Compose
- [x] Start vLLM container and confirm model load
- [x] Verify OpenAI‑compatible endpoints
  - `POST /v1/chat/completions`
  - `GET /v1/models`
- [x] Baseline performance test (single user)
  - Capture p50/p95 latency and QPS
- [x] Document serving configuration knobs
  - model name, max tokens, batching settings

## Track — Distributed Serving (Single Machine)
**Goal:** Demonstrate multi‑service scheduling, queueing, and failover on one GPU node.

### Milestone DS‑1 — Router/Scheduler Service
- [ ] Router service API contract finalized
- [ ] Maintain per‑worker health + queue depth
- [ ] Routing policies: least‑loaded + token‑aware
- [ ] Backpressure (429) when overloaded

### Milestone DS‑2 — Worker Pool (Replicas)
- [ ] Run 2 worker replicas with vLLM (separate ports)
- [ ] Liveness + readiness checks per worker
- [ ] Per‑worker queue depth metric exposed

### Milestone DS‑3 — Streaming + Failover
- [ ] SSE streaming through gateway → router → worker
- [ ] Retry/reroute on worker timeout/crash
- [ ] Chaos test: kill worker under load, capture recovery time

### Milestone DS‑4 — Performance & Reliability
- [ ] Measure TTFT, p95/p99 latency, throughput, queue depth
- [ ] Load test 10–100 concurrent users
- [ ] Max sustainable concurrency before overload

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
