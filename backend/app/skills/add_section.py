import json

name = "Add Section"
keywords = [
    "ajouter",
    "add",
    "nouvelle section",
    "ajoute",
    "ajouter une section",
    "ajoute une section",
]

section_names = [
    "hero",
    "features",
    "benefits",
    "testimonials",
    "pricing",
    "faq",
    "footer",
]


def matches(instruction: str) -> bool:
    normalized = instruction.lower()
    return any(keyword in normalized for keyword in keywords) and any(name in normalized for name in section_names)


def build_prompt(page_state: dict, instruction: str) -> str:
    return f"""Tu es un assistant créatif pour landing pages.
Ajoute UNE seule section demandée par l'utilisateur.
Ne change rien d'autre.

Instruction : {instruction}

Réponds UNIQUEMENT avec un JSON valide contenant la clé de la section à créer.
Exemple : {{"testimonials":[{{"name":"...","text":"...","rating":5}}]}} ou {{"faq":[{{"question":"...","answer":"..."}}]}}.
"""


def validate(changes: dict) -> bool:
    if not isinstance(changes, dict):
        return False
    return len(changes) == 1 and list(changes.keys())[0] in section_names


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = dict(page_state)
    section, content = next(iter(changes.items()))
    updated[section] = content
    return updated
