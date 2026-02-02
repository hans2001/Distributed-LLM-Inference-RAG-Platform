import os
from typing import List

from dagster import op, job, RetryPolicy, get_dagster_logger, Definitions
from sqlalchemy import Column, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/rag")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
model = SentenceTransformer(EMBEDDING_MODEL)


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    doc_id = Column(String(128), index=True)
    chunk_id = Column(Integer, index=True)
    text = Column(Text)
    embedding = Column(Vector(384))


@op(retry_policy=RetryPolicy(max_retries=3))
def load_documents() -> List[dict]:
    return [
        {"id": "demo-1", "text": "Example document about LLM inference and RAG systems."},
        {"id": "demo-2", "text": "Second example document covering observability and pipelines."},
    ]


@op(retry_policy=RetryPolicy(max_retries=3))
def chunk_documents(docs: List[dict]) -> List[dict]:
    chunks = []
    for doc in docs:
        for i, chunk in enumerate(_chunk(doc["text"])):
            chunks.append({"id": doc["id"], "chunk_id": i, "text": chunk})
    return chunks


@op(retry_policy=RetryPolicy(max_retries=3))
def embed_chunks(chunks: List[dict]) -> List[dict]:
    for chunk in chunks:
        chunk["embedding"] = model.encode(chunk["text"]).tolist()
    return chunks


@op(retry_policy=RetryPolicy(max_retries=3))
def write_pgvector(chunks: List[dict]) -> int:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    logger = get_dagster_logger()
    try:
        count = 0
        for chunk in chunks:
            session.add(Document(doc_id=chunk["id"], chunk_id=chunk["chunk_id"], text=chunk["text"], embedding=chunk["embedding"]))
            count += 1
        session.commit()
        logger.info("Indexed %s chunks", count)
        return count
    finally:
        session.close()


@op
def validate_index(count: int) -> str:
    return f"Indexed {count} chunks"


@job
def ingest_pipeline():
    validate_index(write_pgvector(embed_chunks(chunk_documents(load_documents()))))


definitions = Definitions(jobs=[ingest_pipeline])


def _chunk(text: str, size: int = 500, overlap: int = 50):
    if not text:
        return []
    chunks = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + size])
        i += size - overlap
    return chunks
