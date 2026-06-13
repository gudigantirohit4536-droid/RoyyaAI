import asyncio
from pathlib import Path
from app.rag.embedder import embed_texts
from app.rag.qdrant_store import ensure_collection, upsert_chunks

KNOWLEDGE_DIR = Path(__file__).resolve().parents[2] / "knowledge_base"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100


def chunk_text(text: str, source: str) -> list[dict]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    chunk_index = 0
    while i < len(words):
        chunk_words = words[i : i + CHUNK_SIZE]
        chunk_text = " ".join(chunk_words)
        if chunk_text.strip():
            chunks.append({
                "text": chunk_text,
                "source": source,
                "chunk_index": chunk_index,
            })
        i += CHUNK_SIZE - CHUNK_OVERLAP
        chunk_index += 1
    return chunks


async def ingest_file(file_path: Path) -> int:
    text = file_path.read_text(encoding="utf-8")
    source = file_path.name
    chunks = chunk_text(text, source)
    if not chunks:
        return 0

    # Embed in batches of 20
    batch_size = 20
    all_embedded = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c["text"] for c in batch]
        embeddings = await embed_texts(texts)
        for chunk, emb in zip(batch, embeddings):
            chunk["embedding"] = emb
            all_embedded.append(chunk)

    upsert_chunks(all_embedded)
    return len(all_embedded)


async def ingest_all_knowledge_base() -> dict:
    ensure_collection()
    results = {}
    txt_files = list(KNOWLEDGE_DIR.glob("*.txt"))
    for file_path in txt_files:
        count = await ingest_file(file_path)
        results[file_path.name] = count
    return results
