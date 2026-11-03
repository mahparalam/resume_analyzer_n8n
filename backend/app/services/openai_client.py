from openai import OpenAI

from app.config import settings

# Shared by every service that calls OpenAI
client = OpenAI(
    api_key=settings.openai_api_key,
    timeout=settings.openai_timeout,
    max_retries=settings.openai_max_retries,
)


class LLMOutputError(Exception):
    """The model answered, but not with the structured output we asked for."""
