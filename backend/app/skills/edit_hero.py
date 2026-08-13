from copy import deepcopy

TOOL_NAME = "edit_hero"
ALLOWED_FIELDS = {"title", "subtitle", "cta_text"}


def tool_definition() -> dict:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": "Modifie le titre, le sous-titre ou le bouton principal de la section hero.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Nouveau titre du hero."},
                    "subtitle": {"type": "string", "description": "Nouveau sous-titre du hero."},
                    "cta_text": {"type": "string", "description": "Nouveau texte du bouton du hero."},
                },
                "additionalProperties": False,
            },
        },
    }


def validate(changes: dict) -> bool:
    return (
        isinstance(changes, dict)
        and bool(changes)
        and set(changes).issubset(ALLOWED_FIELDS)
        and all(isinstance(value, str) and value.strip() for value in changes.values())
    )


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = deepcopy(page_state)
    updated_hero = dict(updated.get("hero", {}))
    updated_hero.update({key: value.strip() for key, value in changes.items()})
    updated["hero"] = updated_hero
    return updated


def execute(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return {
            "ok": False,
            "error": "Le hero doit contenir au moins un texte non vide parmi le titre, le sous-titre ou le bouton.",
        }

    changes = {key: value.strip() for key, value in arguments.items()}
    return {
        "ok": True,
        "page_state": apply(page_state, changes),
        "changes": {"hero": changes},
        "summary": "La section hero a été mise à jour.",
    }
