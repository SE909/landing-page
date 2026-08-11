import json

name = "Edit Hero"
keywords = [
    "hero",
    "titre",
    "sous-titre",
    "cta",
    "call to action",
    "appel à l'action",
    "titre principal",
    "titre accrocheur",
]


def matches(instruction: str) -> bool:
    normalized = instruction.lower()
    return any(keyword in normalized for keyword in keywords)


def build_prompt(page_state: dict, instruction: str) -> str:
    hero = page_state.get("hero", {})
    return f"""Tu es un assistant spécialisé en landing pages.
Modifie UNIQUEMENT la section hero selon l'instruction suivante.
Ne change rien d'autre.

Hero actuel :
{json.dumps(hero, ensure_ascii=False, indent=2)}

Instruction : {instruction}

Réponds UNIQUEMENT avec un JSON valide contenant au maximum les clés : title, subtitle, cta_text.
Si une valeur ne doit pas changer, ne la mentionne pas dans la réponse.
"""


def validate(changes: dict) -> bool:
    if not isinstance(changes, dict):
        return False
    allowed = {"title", "subtitle", "cta_text"}
    return any(key in allowed for key in changes.keys())


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = dict(page_state)
    updated_hero = dict(updated.get("hero", {}))
    updated_hero.update(changes)
    updated["hero"] = updated_hero
    return updated
