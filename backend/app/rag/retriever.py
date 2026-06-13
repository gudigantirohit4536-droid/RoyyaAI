from app.rag.embedder import embed_text
from app.rag.qdrant_store import search


async def retrieve_context(query: str, top_k: int = 4) -> str:
    """Retrieve relevant knowledge base chunks for a query."""
    query_embedding = await embed_text(query)
    results = search(query_embedding, top_k=top_k)

    if not results:
        return ""

    context_parts = []
    for i, r in enumerate(results, 1):
        source = r["source"].replace(".txt", "").replace("_", " ").title()
        context_parts.append(f"[Knowledge {i} - {source}]\n{r['text']}")

    return "\n\n".join(context_parts)
