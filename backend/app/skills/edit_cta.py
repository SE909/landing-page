import json

name = "Edit CTA"
keywords = [
    "cta",
    "appel à l'action",
    "bouton",
    "call to action",
    "inscription",
    "réserver",
]


def matches(instruction: str) -> bool:
    normalized = instruction.lower()
    return any(keyword in normalized for keyword in keywords)


def build_prompt(page_state: dict, instruction: str) -> str:
    hero = page_state.get("hero", {})
    pricing = page_state.get("pricing", {})
    return f"""Tu es un assistant spécialisé en landing pages.
Modifie UNIQUEMENT le texte des boutons et des appels à l'action.
Ne change rien d'autre.

Hero actuel :
{json.dumps(hero, ensure_ascii=False, indent=2)}

Pricing actuel :
{json.dumps(pricing, ensure_ascii=False, indent=2)}

Instruction : {instruction}

Réponds UNIQUEMENT avec un JSON valide contenant des clés comme title, cta_text, value_proposition, guarantee, et/ou subtitle.
Ne renvoie pas de markdown, pas d'explications.
"""


def validate(changes: dict) -> bool:
    if not isinstance(changes, dict):
        return False
    return any(key in changes for key in {"cta_text", "value_proposition", "guarantee", "title", "subtitle"})


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = dict(page_state)
    if "cta_text" in changes or "value_proposition" in changes or "guarantee" in changes:
        updated_pricing = dict(updated.get("pricing", {}))
        for key in ["cta_text", "value_proposition", "guarantee"]:
            if key in changes:
                updated_pricing[key] = changes[key]
        updated["pricing"] = updated_pricing
    if "title" in changes or "subtitle" in changes:
        updated_hero = dict(updated.get("hero", {}))
        if "title" in changes:
            updated_hero["title"] = changes["title"]
        if "subtitle" in changes:
            updated_hero["subtitle"] = changes["subtitle"]
        updated["hero"] = updated_hero
    return updated
