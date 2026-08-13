from copy import deepcopy

TOOL_NAME = "edit_cta"
ALLOWED_FIELDS = {
    "hero_title",
    "hero_subtitle",
    "hero_cta_text",
    "pricing_cta_text",
    "value_proposition",
    "guarantee",
}


def tool_definition() -> dict:
    return {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": "Modifie les appels à l'action, leur contexte commercial ou leur texte associé.",
            "parameters": {
                "type": "object",
                "properties": {
                    "hero_title": {"type": "string", "description": "Nouveau titre du hero si nécessaire."},
                    "hero_subtitle": {"type": "string", "description": "Nouveau sous-titre du hero si nécessaire."},
                    "hero_cta_text": {"type": "string", "description": "Texte du bouton du hero."},
                    "pricing_cta_text": {"type": "string", "description": "Texte du bouton de la section finale/pricing."},
                    "value_proposition": {"type": "string", "description": "Texte de valeur de la section finale/pricing."},
                    "guarantee": {"type": "string", "description": "Texte de garantie, si la landing en utilise un."},
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
    hero = dict(updated.get("hero", {}))
    pricing = dict(updated.get("pricing", {}))

    field_map = {
        "hero_title": (hero, "title"),
        "hero_subtitle": (hero, "subtitle"),
        "hero_cta_text": (hero, "cta_text"),
        "pricing_cta_text": (pricing, "cta_text"),
        "value_proposition": (pricing, "value_proposition"),
        "guarantee": (pricing, "guarantee"),
    }
    for field, value in changes.items():
        target, target_field = field_map[field]
        target[target_field] = value.strip()

    updated["hero"] = hero
    updated["pricing"] = pricing
    return updated


def execute(page_state: dict, arguments: dict) -> dict:
    if not validate(arguments):
        return {
            "ok": False,
            "error": "Les textes de CTA doivent être non vides et correspondre à un champ d'appel à l'action autorisé.",
        }

    changes = {key: value.strip() for key, value in arguments.items()}
    return {
        "ok": True,
        "page_state": apply(page_state, changes),
        "changes": changes,
        "summary": "Les appels à l'action ont été mis à jour.",
    }
