"""Chatbot backed by the OpenAI API. It edits `page_state`, never HTML."""

import json
import logging

import httpx

from app.config import settings
from app.services.page_state import SECTION_SCHEMA

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es l'assistant d'édition d'une landing page de formation.
Tu modifies UNIQUEMENT le `page_state` structuré fourni. Tu ne produis JAMAIS de HTML.

Réponds UNIQUEMENT avec un JSON de cette forme :
{
  "reply": "réponse courte en français à l'utilisateur",
  "updates": {"<section_id>": {"<prop>": "nouvelle valeur"}},
  "visibility": {"<section_id>": true|false}
}

Règles :
- `updates` ne contient que les sections et propriétés réellement modifiées.
- N'invente pas de nouvelles sections ni de nouvelles propriétés.
- Les valeurs sont du texte brut (sauf `program.skills` qui est une liste de textes).
- Si la demande ne nécessite aucune modification, renvoie `updates` et `visibility` vides et réponds dans `reply`.
"""


class OpenAIError(RuntimeError):
    pass


def _schema_description() -> str:
    return json.dumps(SECTION_SCHEMA, ensure_ascii=False)


async def edit_page_state(
    message: str, page_state: dict, history: list[dict] | None = None
) -> dict:
    """Ask OpenAI for structured edits. Returns `{reply, updates, visibility}`."""
    if not settings.openai_api_key:
        raise OpenAIError(
            "Clé OpenAI manquante : définissez OPENAI_API_KEY dans le fichier .env du backend."
        )

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                f"Schéma des sections (section_id -> propriétés) : {_schema_description()}\n"
                f"page_state actuel : {json.dumps(page_state, ensure_ascii=False)}"
            ),
        },
    ]
    for entry in history or []:
        role = entry.get("role")
        content = entry.get("content")
        if role in ("user", "assistant") and content:
            messages.append({"role": role, "content": str(content)})
    messages.append({"role": "user", "content": message})

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.openai_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.openai_api_key}"},
                json={
                    "model": settings.openai_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as exc:
        logger.warning("OpenAI HTTP error: %s", exc.response.text[:500])
        raise OpenAIError(f"Erreur OpenAI ({exc.response.status_code}).") from exc
    except Exception as exc:
        logger.warning("OpenAI call failed: %s", exc)
        raise OpenAIError("Impossible de contacter OpenAI.") from exc

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise OpenAIError("Réponse OpenAI invalide (JSON attendu).") from exc

    return {
        "reply": str(parsed.get("reply") or "").strip(),
        "updates": parsed.get("updates") if isinstance(parsed.get("updates"), dict) else {},
        "visibility": parsed.get("visibility") if isinstance(parsed.get("visibility"), dict) else {},
    }
