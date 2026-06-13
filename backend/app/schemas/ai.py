from pydantic import BaseModel
from datetime import datetime


class ChatRequest(BaseModel):
    message: str
    pond_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    pond_id: str | None = None


class ConversationMessage(BaseModel):
    id: str
    role: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}
