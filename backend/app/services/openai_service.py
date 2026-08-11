import httpx
import json
import logging
import re

from app.config import settings

logger = logging.getLogger(__name__)


class OpenAIConfigurationError(ValueError):
    pass


class OpenAIServiceError(ValueError):
    pass


async def generate_with_openai(payload: dict, campaign: dict = None) -> dict:
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
            raw = data["choices"][0]["message"]["content"]

        cleaned_raw = re.sub(r"```json\s*", "", raw)
        cleaned_raw = re.sub(r"```\s*", "", cleaned_raw).strip()

        match = re.search(r"\{.*\}", cleaned_raw, re.DOTALL)
        if match:
            return json.loads(match.group())

        raise OpenAIServiceError(f"OpenAI response ne contient pas de JSON valide : {cleaned_raw}")
    except httpx.HTTPStatusError as e:
        body = e.response.text if e.response is not None else str(e)
        logger.warning(f"OpenAI generation HTTP error ({e.response.status_code}): {body}")
        raise OpenAIServiceError(f"OpenAI HTTP error: {body}")
    except json.JSONDecodeError as e:
        logger.warning(f"OpenAI JSON decode failed: {e}")
        raise OpenAIServiceError("Impossible d’analyser la réponse JSON d’OpenAI.")
    except OpenAIConfigurationError:
        raise
    except Exception as e:
        logger.warning(f"OpenAI generation call failed ({e}).")
        raise OpenAIServiceError(f"Erreur OpenAI : {e}")
