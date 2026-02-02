import os
import time
from typing import Dict, List

import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

RETRIEVAL_BASE_URL = os.getenv("RETRIEVAL_BASE_URL", "http://localhost:8002")
INFERENCE_BASE_URL = os.getenv("INFERENCE_BASE_URL", "http://localhost:8001")
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "orchestrator")

resource = Resource.create({"service.name": OTEL_SERVICE_NAME})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = FastAPI(title="LangGraph Orchestrator")
FastAPIInstrumentor.instrument_app(app)

REQUEST_LATENCY = Histogram("orchestrator_request_latency_seconds", "Request latency", ["route"])
REQUEST_COUNT = Counter("orchestrator_requests_total", "Total requests", ["route", "status"])


class ChatRequest(BaseModel):
    messages: List[dict]
    top_k: int = 4
    stream: bool = False


class GraphState(dict):
    query: str
    contexts: List[str]
    answer: str


async def retrieve(state: GraphState) -> GraphState:
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{RETRIEVAL_BASE_URL}/query", json={"query": state["query"], "top_k": state.get("top_k", 4)})
    contexts = [r["text"] for r in resp.json().get("results", [])]
    state["contexts"] = contexts
    return state


async def generate(state: GraphState) -> GraphState:
    prompt = "\n\n".join(state.get("contexts", [])) + "\n\nQuestion: " + state["query"]
    payload = {
        "model": "llm",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{INFERENCE_BASE_URL}/v1/chat/completions", json=payload)
    data = resp.json()
    state["answer"] = data["choices"][0]["message"]["content"]
    state["usage"] = data.get("usage", {})
    return state


async def validate(state: GraphState) -> GraphState:
    answer = state.get("answer", "")
    state["valid"] = bool(answer)
    return state


graph = StateGraph(GraphState)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_node("validate", validate)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", "validate")

memory = MemorySaver()
app_graph = graph.compile(checkpointer=memory)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return app.response_class(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/run")
async def run(payload: ChatRequest):
    start = time.time()
    query = payload.messages[-1]["content"] if payload.messages else ""
    result = await app_graph.ainvoke({"query": query, "top_k": payload.top_k})
    REQUEST_LATENCY.labels("/run").observe(time.time() - start)
    REQUEST_COUNT.labels("/run", "200").inc()
    return {
        "answer": result.get("answer", ""),
        "contexts": result.get("contexts", []),
        "usage": result.get("usage", {}),
        "valid": result.get("valid", False),
    }
