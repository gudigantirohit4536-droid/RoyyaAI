from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from app.core.config import settings
from app.rag.embedder import EMBEDDING_DIM
import uuid

COLLECTION = settings.QDRANT_COLLECTION

_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        if settings.QDRANT_API_KEY:
            _client = QdrantClient(
                url=f"https://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}",
                api_key=settings.QDRANT_API_KEY,
            )
        else:
            _client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    return _client


def ensure_collection() -> None:
    client = get_qdrant()
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION not in existing:
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def upsert_chunks(chunks: list[dict]) -> None:
    """chunks: list of {text, embedding, source, chunk_index}"""
    client = get_qdrant()
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=chunk["embedding"],
            payload={
                "text": chunk["text"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
            },
        )
        for chunk in chunks
    ]
    client.upsert(collection_name=COLLECTION, points=points)


def search(query_embedding: list[float], top_k: int = 5) -> list[dict]:
    client = get_qdrant()
    results = client.search(
        collection_name=COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True,
    )
    return [
        {
            "text": r.payload["text"],
            "source": r.payload.get("source", ""),
            "score": r.score,
        }
        for r in results
    ]
