# Observability (MVP Scope)

## Traces
- All services emit traces via OpenTelemetry.
- Collector exports to Jaeger.

## Metrics
- Gateway: latency, request count, token count
- Retrieval: latency, request count
- Orchestrator: latency, request count

## Dashboards
- Grafana dashboard: p95 latency + request rate panels.
- Prometheus scrapes service `/metrics` plus OTel Collector metrics.

## Scope Guardrails
- Single stack only (OTel + Jaeger + Prometheus/Grafana)
- No duplicate monitoring tools
