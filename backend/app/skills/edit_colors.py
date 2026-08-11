import json

name = "Edit Colors"
keywords = [
    "couleur",
    "blue",
    "bleu",
    "palette",
    "primary",
    "secondary",
    "thème",
]


def matches(instruction: str) -> bool:
    normalized = instruction.lower()
    return any(keyword in normalized for keyword in keywords)


def build_prompt(page_state: dict, instruction: str) -> str:
    branding = page_state.get("branding", {})
    return f"""Tu es un assistant UI/marketing.
Modifie UNIQUEMENT les couleurs de la landing page dans le format de branding suivant.
Ne change rien d'autre.

Branding actuel :
{json.dumps(branding, ensure_ascii=False, indent=2)}

Instruction : {instruction}

Réponds UNIQUEMENT avec un JSON valide contenant les clés : primary_color et/ou secondary_color.
"""


def validate(changes: dict) -> bool:
    if not isinstance(changes, dict):
        return False
    return any(key in changes for key in {"primary_color", "secondary_color"})


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = dict(page_state)
    updated_branding = dict(updated.get("branding", {}))
    updated_branding.update({k: v for k, v in changes.items() if k in {"primary_color", "secondary_color"}})
    updated["branding"] = updated_branding
    return updated
