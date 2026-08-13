import importlib
import json
import logging
from copy import deepcopy
from typing import Any

from app.config import settings
from app.services.openai_service import assistant_text, create_chat_completion

logger = logging.getLogger(__name__)

SKILL_MODULES = [
    "app.skills.edit_hero",
    "app.skills.edit_cta",
    "app.skills.edit_colors",
    "app.skills.add_section",
    "app.skills.remove_section",
    "app.skills.improve_copy",
]
MAX_TOOL_ROUNDS = 3
MAX_HISTORY_MESSAGES = 12

SYSTEM_PROMPT = """Tu es l’assistant conversationnel de Landing Page Creator.

Réponds toujours en français, avec un ton clair, utile et concis.
Tu aides l’utilisateur à comprendre et améliorer sa landing page de formation.

Règles impératives :
- Ne révèle jamais de JSON, d’arguments d’outil, de schémas, de détails techniques internes ou de résultats bruts d’outil.
- Si l’utilisateur pose une question, réponds directement en texte naturel. N’appelle aucun outil si la page ne doit pas être modifiée.
- Si l’utilisateur demande une modification concrète de la landing page, appelle l’outil approprié.
- Une même demande peut nécessiter plusieurs outils : appelle-les tous si nécessaire.
- Tu peux répondre à une question et proposer ou effectuer une modification dans le même message si l’utilisateur le demande explicitement.
- Utilise uniquement les outils disponibles et leurs paramètres. Ne prétends jamais avoir modifié la page sans résultat d’outil réussi.
- Les modifications sont préparées pour confirmation : ne dis pas qu’elles sont définitivement enregistrées avant confirmation.
- Après un résultat d’outil, transforme-le en réponse utilisateur naturelle. En cas d’échec d’un outil, explique simplement le problème et, si utile, indique comment le corriger.
- Ne demande une précision que lorsqu’elle est indispensable pour effectuer une modification sûre.
- Ne mentionne pas les trois aperçus comme des pages distinctes : une modification concerne la même landing page et son rendu responsive.
"""


def load_skills() -> dict[str, Any]:
    skills = [importlib.import_module(module_name) for module_name in SKILL_MODULES]
    return {skill.TOOL_NAME: skill for skill in skills}


def tool_definitions(skills: dict[str, Any]) -> list[dict]:
    return [skill.tool_definition() for skill in skills.values()]


def _history_messages(history: list[dict] | None) -> list[dict]:
    messages: list[dict] = []
    for item in (history or [])[-MAX_HISTORY_MESSAGES:]:
        role = item.get("role") if isinstance(item, dict) else None
        text = item.get("text") if isinstance(item, dict) else None
        if role in {"user", "assistant"} and isinstance(text, str) and text.strip():
            messages.append({"role": role, "content": text.strip()})
    return messages


def _tool_result(tool_call_id: str, result: dict) -> dict:
    """Build a tool result message. It is only sent back to the model."""
    return {
        "role": "tool",
        "tool_call_id": tool_call_id,
        "content": json.dumps(result, ensure_ascii=False),
    }


def _execute_tool(skill: Any | None, arguments_json: str, page_state: dict) -> dict:
    if skill is None:
        return {"ok": False, "error": "L’outil demandé n’est pas disponible."}
    try:
        arguments = json.loads(arguments_json or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": "Les paramètres de la modification sont invalides."}
    if not isinstance(arguments, dict):
        return {"ok": False, "error": "Les paramètres de la modification doivent être un objet."}

    try:
        return skill.execute(page_state, arguments)
    except Exception:
        logger.exception("Tool %s failed unexpectedly.", skill.TOOL_NAME)
        return {"ok": False, "error": "La modification n’a pas pu être préparée. Réessayez avec une demande plus précise."}


async def process_conversation(
    page_state: dict,
    instruction: str,
    history: list[dict] | None = None,
) -> dict:
    """Run OpenAI's native tool-calling loop for one user message.

    Successful tools update a temporary state sequentially. The caller decides
    whether to persist that state as one grouped pending proposal.
    """
    skills = load_skills()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": "État actuel de la landing page (contexte interne, ne pas le citer tel quel) :\n"
            + json.dumps(page_state, ensure_ascii=False),
        },
        *_history_messages(history),
        {"role": "user", "content": instruction.strip()},
    ]
    working_state = deepcopy(page_state)
    applied_changes: list[dict] = []
    used_tools: list[str] = []

    for _ in range(MAX_TOOL_ROUNDS):
        assistant_message = await create_chat_completion(
            {
                "model": settings.openai_model,
                "messages": messages,
                "tools": tool_definitions(skills),
                "tool_choice": "auto",
                "temperature": 0.2,
                "max_tokens": 1200,
            }
        )
        tool_calls = assistant_message.get("tool_calls") or []
        messages.append(assistant_message)

        if not tool_calls:
            message = assistant_text(assistant_message)
            if message:
                return {
                    "message": message,
                    "page_state": working_state,
                    "edited": bool(applied_changes),
                    "changes": applied_changes,
                    "tools": used_tools,
                }
            break

        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            tool_name = function.get("name")
            result = _execute_tool(skills.get(tool_name), function.get("arguments", "{}"), working_state)
            if result.get("ok"):
                working_state = result["page_state"]
                applied_changes.append(
                    {
                        "tool": tool_name,
                        "changes": result.get("changes", {}),
                        "summary": result.get("summary", "Modification préparée."),
                    }
                )
                used_tools.append(tool_name)

            messages.append(_tool_result(tool_call.get("id", "missing-tool-call-id"), result))

    # This fallback is intentionally plain language: raw tool data never crosses
    # the service boundary, even if the model omits a final text response.
    if applied_changes:
        message = "J’ai préparé les modifications demandées. Vous pouvez les confirmer dans l’aperçu."
    else:
        message = "Je n’ai pas pu préparer cette modification. Pouvez-vous préciser ce que vous souhaitez changer ?"
    return {
        "message": message,
        "page_state": working_state,
        "edited": bool(applied_changes),
        "changes": applied_changes,
        "tools": used_tools,
    }
