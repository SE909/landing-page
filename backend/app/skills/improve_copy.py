from copy import deepcopy

TOOL_NAME = "improve_copy"
ALLOWED_SECTIONS = {
    "hero",
    "problem_solution",
    "program",
    "social_proof",
    "pricing",
    "instructor",
    "testimonial",
    "faq",
}


def tool_definition() -> dict:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": "Améliore ou réécrit des textes existants sans modifier la structure de la landing page.",
            "parameters": {
                "type": "object",
                "properties": {
                    "updates": {
                        "type": "object",
                        "description": "Sections à mettre à jour. Chaque valeur doit être un objet ne contenant que les champs textuels à modifier.",
                        "additionalProperties": {"type": "object"},
                    },
                },
                "required": ["updates"],
                "additionalProperties": False,
            },
        },
    }


def validate(arguments: dict) -> bool:
    if not isinstance(arguments, dict) or set(arguments) != {"updates"}:
        return False
    updates = arguments.get("updates")
    if not isinstance(updates, dict) or not updates or not set(updates).issubset(ALLOWED_SECTIONS):
        return False
    return all(isinstance(value, dict) and value for value in updates.values())


def apply(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return page_state
    updated = deepcopy(page_state)
    for section, values in arguments["updates"].items():
        current = dict(updated.get(section, {}))
        current.update(deepcopy(values))
        updated[section] = current
    return updated


def execute(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return {
            "ok": False,
            "error": "Les améliorations doivent cibler au moins une section textuelle connue avec des champs à modifier.",
        }

    return {
        "ok": True,
        "page_state": apply(page_state, arguments),
        "changes": deepcopy(arguments["updates"]),
        "summary": "Les textes demandés ont été améliorés.",
    }
