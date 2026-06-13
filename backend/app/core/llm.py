from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from app.core.config import settings
from typing import AsyncIterator


def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def get_anthropic_client() -> AsyncAnthropic:
    return AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)


async def chat_completion(messages: list[dict], stream: bool = False) -> str | AsyncIterator:
    """
    Single entry point for LLM calls. Switches provider via LLM_PROVIDER env var.
    messages: [{"role": "system"|"user"|"assistant", "content": "..."}]
    """
    if settings.LLM_PROVIDER == "openai":
        client = get_openai_client()
        if stream:
            return await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                stream=True,
            )
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        return response.choices[0].message.content

    elif settings.LLM_PROVIDER == "anthropic":
        client = get_anthropic_client()
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user_messages = [m for m in messages if m["role"] != "system"]
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=system,
            messages=user_messages,
        )
        return response.content[0].text

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {settings.LLM_PROVIDER}")
