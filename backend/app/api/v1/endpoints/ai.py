from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.deps import get_current_user_id
from app.schemas.ai import ChatRequest, ChatResponse
from app.services.ai_service import AIService
from app.rag.ingestion import ingest_all_knowledge_base

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    reply = await AIService(db, user_id).chat(data.message, data.pond_id)
    return ChatResponse(reply=reply, pond_id=data.pond_id)


@router.post("/ingest-knowledge", summary="Index knowledge base into Qdrant")
async def ingest_knowledge(user_id: str = Depends(get_current_user_id)):
    results = await ingest_all_knowledge_base()
    total = sum(results.values())
    return {"status": "done", "files_indexed": results, "total_chunks": total}
