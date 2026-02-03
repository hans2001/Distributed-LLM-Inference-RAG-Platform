import os
import time
from typing import List

from fastapi import FastAPI, Response
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Text, create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "retrieval")

resource = Resource.create({"service.name": OTEL_SERVICE_NAME})
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

app = FastAPI(title="Retrieval Service")
FastAPIInstrumentor.instrument_app(app)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
model = SentenceTransformer(EMBEDDING_MODEL)

REQUEST_LATENCY = Histogram("retrieval_request_latency_seconds", "Request latency", ["route"])
REQUEST_COUNT = Counter("retrieval_requests_total", "Total requests", ["route", "status"])


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(128), index=True)
    chunk_id = Column(Integer, index=True)
    text = Column(Text)
    embedding = Column(Vector(384))


class IngestRequest(BaseModel):
    documents: List[dict]


class QueryRequest(BaseModel):
    query: str
    top_k: int = 4


@app.on_event("startup")
def on_startup():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


@app.post("/ingest")
async def ingest(payload: IngestRequest):
    start = time.time()
    session = SessionLocal()
    try:
        count = 0
        for doc in payload.documents:
            text = doc.get("text", "")
            chunks = _chunk(text)
            for i, chunk in enumerate(chunks):
                emb = model.encode(chunk).tolist()
                session.add(Document(doc_id=doc.get("id", ""), chunk_id=i, text=chunk, embedding=emb))
                count += 1
        session.commit()
    finally:
        session.close()
    REQUEST_LATENCY.labels("/ingest").observe(time.time() - start)
    REQUEST_COUNT.labels("/ingest", "200").inc()
    return {"ingested_chunks": count}


@app.post("/query")
async def query(payload: QueryRequest):
    start = time.time()
    session = SessionLocal()
    try:
        query_emb = model.encode(payload.query).tolist()
        results = (
            session.query(Document)
            .order_by(Document.embedding.l2_distance(query_emb))
            .limit(payload.top_k)
            .all()
        )
        data = [{"doc_id": r.doc_id, "chunk_id": r.chunk_id, "text": r.text} for r in results]
    finally:
        session.close()
    REQUEST_LATENCY.labels("/query").observe(time.time() - start)
    REQUEST_COUNT.labels("/query", "200").inc()
    return {"results": data}


def _chunk(text: str, size: int = 500, overlap: int = 50) -> List[str]:
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + size])
        i += size - overlap
    return chunks
