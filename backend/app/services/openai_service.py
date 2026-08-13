import json
import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIConfigurationError(ValueError):
    pass


class OpenAIServiceError(ValueError):
    pass


async def create_chat_completion(payload: dict) -> dict:
    """Call OpenAI Chat Completions and return the complete assistant message.

    The complete message is needed for native tool calling because it includes
    both the user-facing content and the optional ``tool_calls`` array.
    """
    if not settings.openai_api_key:
        raise OpenAIConfigurationError(
            "OpenAI API key is required for the chatbot. Set OPENAI_API_KEY in the backend environment or .env file."
        )

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.openai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openai_api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        message = data.get("choices", [{}])[0].get("message")
        if not isinstance(message, dict):
            raise OpenAIServiceError("OpenAI n'a renvoyé aucun message assistant exploitable.")
        return message
    except httpx.HTTPStatusError as error:
        body = error.response.text if error.response is not None else str(error)
        status = error.response.status_code if error.response is not None else "unknown"
        logger.warning("OpenAI HTTP error (%s): %s", status, body)
        raise OpenAIServiceError(f"OpenAI HTTP error: {body}") from error
    except OpenAIConfigurationError:
        raise
    except OpenAIServiceError:
        raise
    except Exception as error:
        logger.warning("OpenAI chat completion failed: %s", error)
        raise OpenAIServiceError(f"Erreur OpenAI : {error}") from error


def assistant_text(message: dict) -> str:
    """Return safe plain assistant text, never a serialized tool payload."""
    content = message.get("content")
    return content.strip() if isinstance(content, str) else ""


async def generate_with_openai(payload: dict, campaign: dict = None) -> dict:
    """Backward-compatible JSON helper for non-chat callers."""
    message = await create_chat_completion(payload)
    raw = assistant_text(message)
    cleaned_raw = re.sub(r"```json\s*", "", raw)
    cleaned_raw = re.sub(r"```\s*", "", cleaned_raw).strip()
    match = re.search(r"\{.*\}", cleaned_raw, re.DOTALL)
    if not match:
        raise OpenAIServiceError(f"OpenAI response ne contient pas de JSON valide : {cleaned_raw}")
    try:
        return json.loads(match.group())
    except json.JSONDecodeError as error:
        logger.warning("OpenAI JSON decode failed: %s", error)
        raise OpenAIServiceError("Impossible d’analyser la réponse JSON d’OpenAI.") from error


async def generate_text_with_openai(payload: dict, campaign: dict = None) -> str:
    """Backward-compatible plain-text helper for non-tool chat callers."""
    return assistant_text(await create_chat_completion(payload))
