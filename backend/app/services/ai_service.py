from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from openai import AsyncOpenAI
from app.core.config import settings
from app.models.conversation import AIConversation, MessageRole
from app.models.daily_log import DailyLog
from app.models.pond import Pond, Stocking
from app.models.farm import Farm
from app.agents.prompts import build_system_prompt
from app.rag.retriever import retrieve_context


class AIService:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def chat(self, message: str, pond_id: str | None = None) -> str:
        pond_context = await self._build_pond_context(pond_id)
        conversation_history = await self._get_conversation_history(pond_id)
        rag_context = await retrieve_context(message)
        system_prompt = build_system_prompt(pond_context, conversation_history, rag_context)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ]

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1024,
            temperature=0.7,
        )

        reply = response.choices[0].message.content

        # Save user message and AI reply to conversation history
        await self._save_message(MessageRole.USER, message, pond_id)
        await self._save_message(MessageRole.ASSISTANT, reply, pond_id)

        return reply

    async def _build_pond_context(self, pond_id: str | None) -> str:
        if not pond_id:
            return "No specific pond selected. Farmer is asking a general question."

        # Get pond info
        pond_result = await self.db.execute(
            select(Pond).where(Pond.id == pond_id)
        )
        pond = pond_result.scalar_one_or_none()
        if not pond:
            return "Pond not found."

        # Get active stocking
        stocking_result = await self.db.execute(
            select(Stocking).where(Stocking.pond_id == pond_id, Stocking.is_active == True)
        )
        stocking = stocking_result.scalar_one_or_none()

        # Get last 7 daily logs
        logs_result = await self.db.execute(
            select(DailyLog)
            .where(DailyLog.pond_id == pond_id)
            .order_by(DailyLog.log_date.desc())
            .limit(7)
        )
        logs = logs_result.scalars().all()

        # Build context string
        context = f"""
POND INFORMATION:
- Pond Name: {pond.name}
- Area: {pond.area_acres} acres
- Type: {pond.pond_type}
- Water Source: {pond.water_source}
- Status: {pond.status}
"""

        if stocking:
            context += f"""
CURRENT STOCKING:
- Stocking Date: {stocking.stocking_date}
- PL Count: {f"{stocking.pl_count:,}" if stocking.pl_count else "N/A"}
- Stocking Density: {stocking.stocking_density} PL/sqm
- PL Source: {stocking.pl_source}
"""

        if logs:
            context += "\nRECENT DAILY LOGS (latest first):\n"
            for log in logs:
                context += f"""
  Date: {log.log_date} | DOC: {log.doc}
  DO: {log.dissolved_oxygen} mg/L | pH: {log.ph} | Temp: {log.temperature}°C
  Salinity: {log.salinity} ppt | Alkalinity: {log.alkalinity} mg/L
  Ammonia: {log.ammonia} mg/L | Nitrite: {log.nitrite} mg/L
  Feed: {log.feed_quantity_kg} kg | ABW: {log.abw_grams}g | Mortality: {log.mortality_count}
  Notes: {log.notes or 'None'}
"""
        else:
            context += "\nNo daily logs recorded yet for this pond.\n"

        return context

    async def _get_conversation_history(self, pond_id: str | None, limit: int = 6) -> str:
        result = await self.db.execute(
            select(AIConversation)
            .where(
                AIConversation.user_id == self.user_id,
                AIConversation.pond_id == pond_id,
            )
            .order_by(AIConversation.created_at.desc())
            .limit(limit)
        )
        messages = list(reversed(result.scalars().all()))

        if not messages:
            return "No previous conversation."

        history = ""
        for msg in messages:
            role = "Farmer" if msg.role == MessageRole.USER else "RoyyaAI"
            history += f"{role}: {msg.message}\n\n"

        return history

    async def _save_message(self, role: MessageRole, message: str, pond_id: str | None) -> None:
        conversation = AIConversation(
            user_id=self.user_id,
            pond_id=pond_id,
            role=role,
            message=message,
        )
        self.db.add(conversation)
        await self.db.flush()
