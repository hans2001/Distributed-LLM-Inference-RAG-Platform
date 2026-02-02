import os
import time
from typing import List, Optional

import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

INFERENCE_BASE_URL = os.getenv("INFERENCE_BASE_URL", "http://localhost:8001")
RETRIEVAL_BASE_URL = os.getenv("RETRIEVAL_BASE_URL", "http://localhost:8002")
LANGGRAPH_BASE_URL = os.getenv("LANGGRAPH_BASE_URL", "http://localhost:8003")
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "gateway")

resource = Resource.create({"service.name": OTEL_SERVICE_NAME})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
HTTPXClientInstrumentor().instrument()

app = FastAPI(title="LLM Gateway")
FastAPIInstrumentor.instrument_app(app)

REQUEST_LATENCY = Histogram("gateway_request_latency_seconds", "Request latency", ["route"])
REQUEST_COUNT = Counter("gateway_requests_total", "Total requests", ["route", "status"])
TOKEN_COUNT = Counter("gateway_tokens_total", "Total tokens", ["type"])


class ChatRequest(BaseModel):
    messages: List[dict]
    top_k: int = 4
    stream: bool = False


class IngestRequest(BaseModel):
    documents: List[dict]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return app.response_class(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest")
async def ingest(payload: IngestRequest):
    start = time.time()
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{RETRIEVAL_BASE_URL}/ingest", json=payload.dict())
    REQUEST_LATENCY.labels("/ingest").observe(time.time() - start)
    REQUEST_COUNT.labels("/ingest", str(resp.status_code)).inc()
    return resp.json()


@app.post("/chat")
async def chat(payload: ChatRequest):
    start = time.time()
    async with httpx.AsyncClient(timeout=60) as client:
        retr = await client.post(f"{LANGGRAPH_BASE_URL}/run", json=payload.dict())
    REQUEST_LATENCY.labels("/chat").observe(time.time() - start)
    REQUEST_COUNT.labels("/chat", str(retr.status_code)).inc()
    if "usage" in retr.json():
        usage = retr.json()["usage"]
        TOKEN_COUNT.labels("input").inc(usage.get("prompt_tokens", 0))
        TOKEN_COUNT.labels("output").inc(usage.get("completion_tokens", 0))
    return retr.json()
