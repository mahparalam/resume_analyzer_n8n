import logging

import openai
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.services.openai_client import LLMOutputError

logger = logging.getLogger(__name__)


def describe_ai_error(error: Exception) -> tuple[int, str]:
    """Map an OpenAI SDK error to an HTTP status and a message for the user."""
    if isinstance(error, openai.APITimeoutError):
        return 504, "The AI service took too long to respond. Please try again."

    if isinstance(error, openai.APIConnectionError):
        return 503, "Could not reach the AI service. Check the network connection and try again."

    if isinstance(error, openai.RateLimitError):
        return 503, "The AI service is rate-limiting requests or the API quota is used up. Please try again later."

    if isinstance(error, (openai.AuthenticationError, openai.PermissionDeniedError)):
        return 502, "The AI service rejected the API key. Check OPENAI_API_KEY."

    if isinstance(error, openai.APIStatusError):
        return 502, f"The AI service returned an error (HTTP {error.status_code}). Please try again."

    if isinstance(
        error,
        (
            openai.LengthFinishReasonError,
            openai.ContentFilterFinishReasonError,
            LLMOutputError,
        ),
    ):
        return 502, "The AI service returned an incomplete or unusable answer. Please try again."

    return 502, "The AI service failed. Please try again."


async def handle_ai_error(request: Request, error: Exception) -> JSONResponse:
    status_code, detail = describe_ai_error(error)

    logger.error(
        "AI request failed on %s %s: %r",
        request.method,
        request.url.path,
        error,
    )

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail},
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(openai.OpenAIError, handle_ai_error)
    app.add_exception_handler(LLMOutputError, handle_ai_error)
