"""Chatbot backed by the OpenAI API.

It both advises about the landing page and edits it. Edits go through the
`apply_edits` tool and only ever touch `page_state`, never HTML.
"""

import json
import logging

import httpx

from app.config import settings
from app.services.page_state import SECTION_SCHEMA

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es le conseiller et l'éditeur d'une landing page de formation.
Tu réponds en français, de manière concrète et concise.

Deux modes :
1. Conseil : l'utilisateur pose une question ou demande un avis (« pourquoi mon titre est faible ? »,
   « que manque-t-il à ma page ? », « que veut dire cette section ? »). Réponds simplement en texte,
   en t'appuyant sur le `page_state` fourni. Propose des améliorations précises et demande si tu dois
   les appliquer. N'appelle AUCUN outil dans ce cas.
2. Édition : l'utilisateur demande un changement à l'impératif (« rends le titre plus percutant »,
   « change le bouton en... », « raccourcis le sous-titre ») ou accepte une proposition. Appelle
   IMMÉDIATEMENT l'outil `apply_edits` avec le nouveau texte. Ne te contente jamais de proposer une
   formulation dans `reply` : si tu as trouvé la meilleure version, applique-la.

Règles d'édition :
- Tu modifies UNIQUEMENT le `page_state` structuré fourni, jamais du HTML.
- N'invente pas de sections ni de propriétés : respecte le schéma.
- Les valeurs sont du texte brut (sauf `program.skills`, une liste de textes).
- Une demande à l'impératif est une édition, pas une question. Ne conseille que si la demande est
  vraiment une question ou trop vague pour deviner quelle propriété modifier.
"""

APPLY_EDITS_TOOL = {
    "type": "function",
    "function": {
        "name": "apply_edits",
        "description": (
            "Applique des modifications au page_state de la landing page. "
            "À n'utiliser que lorsque l'utilisateur demande un changement."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "reply": {
                    "type": "string",
                    "description": "Phrase en français expliquant ce qui a été modifié.",
                },
                "updates": {
                    "type": "object",
                    "description": (
                        "Objet {section_id: {propriété: nouvelle valeur}} limité aux "
                        "propriétés réellement modifiées."
                    ),
                },
                "visibility": {
                    "type": "object",
                    "description": "Objet {section_id: bool} pour masquer ou afficher une section.",
                },
            },
            "required": ["reply", "updates"],
        },
    },
}


class OpenAIError(RuntimeError):
    pass


def _schema_description() -> str:
    return json.dumps(SECTION_SCHEMA, ensure_ascii=False)


def _parse_tool_call(choice: dict) -> dict:
    """Turn the assistant message into `{reply, updates, visibility}`."""
    assistant = choice.get("message", {})
    text = str(assistant.get("content") or "").strip()
    tool_calls = assistant.get("tool_calls") or []
    if not tool_calls:
        return {"reply": text, "updates": {}, "visibility": {}}

    try:
        args = json.loads(tool_calls[0]["function"]["arguments"] or "{}")
    except json.JSONDecodeError as exc:
        raise OpenAIError("Arguments d'édition OpenAI invalides.") from exc

    return {
        "reply": str(args.get("reply") or text).strip(),
        "updates": args.get("updates") if isinstance(args.get("updates"), dict) else {},
        "visibility": args.get("visibility") if isinstance(args.get("visibility"), dict) else {},
    }


async def edit_page_state(
    message: str, page_state: dict, history: list[dict] | None = None
) -> dict:
    """Answer a question about the page, or edit it. Returns `{reply, updates, visibility}`."""
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
                    "tools": [APPLY_EDITS_TOOL],
                    "tool_choice": "auto",
                },
            )
            response.raise_for_status()
            choice = response.json()["choices"][0]
    except httpx.HTTPStatusError as exc:
        logger.warning("OpenAI HTTP error: %s", exc.response.text[:500])
        raise OpenAIError(f"Erreur OpenAI ({exc.response.status_code}).") from exc
    except Exception as exc:
        logger.warning("OpenAI call failed: %s", exc)
        raise OpenAIError("Impossible de contacter OpenAI.") from exc

    return _parse_tool_call(choice)
