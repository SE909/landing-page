import json

name = "Remove Section"
keywords = [
    "supprimer",
    "remove",
    "retirer",
    "delete",
    "enlever",
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
    return f"""Tu es un assistant pour landing pages.
Supprime uniquement la section demandée par l'utilisateur.
Ne change rien d'autre.

Instruction : {instruction}

Réponds UNIQUEMENT avec un JSON valide qui contient une clé de section et une valeur vide appropriée.
Exemple : {{"faq":[]}} ou {{"testimonials":[]}}.
"""


def validate(changes: dict) -> bool:
    if not isinstance(changes, dict):
        return False
    if len(changes) != 1:
        return False
    section = next(iter(changes))
    return section in section_names


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = dict(page_state)
    updated[next(iter(changes))] = next(iter(changes.values()))
    return updated
