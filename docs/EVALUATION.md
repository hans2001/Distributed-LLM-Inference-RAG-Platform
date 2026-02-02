# Evaluation (MVP Scope)

## Goals
- Confirm retrieval relevance
- Confirm generation groundedness
- Track latency p50/p95

## Minimal RAG Checks
- **Retrieval Recall:** Ensure top-k contains the correct chunk for a small labeled set.
- **Grounded Answer:** Verify answer references retrieved context.
- **Latency:** Use benchmark script for p50/p95 and QPS.

## Inputs
- Small curated set of 10-20 Q/A items with known source chunks.
- Store results in `benchmarks/results.json`.

## Out of Scope
- Large-scale eval suites
- Advanced hallucination detection
