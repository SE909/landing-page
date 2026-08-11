import json

name = "Improve Copy"
keywords = [
    "rewrite",
    "réécrire",
    "améliore",
    "améliorer",
    "plus persuasive",
    "persuasive",
    "ton",
    "copy",
    "texte",
    "contenu",
]


def matches(instruction: str) -> bool:
    normalized = instruction.lower()
    return any(keyword in normalized for keyword in keywords)


def build_prompt(page_state: dict, instruction: str) -> str:
    return f"""Tu es un assistant copywriting.
Améliore le texte de la landing page selon l'instruction sans modifier la structure.
Ne change rien d'autre.

Page actuelle :
{json.dumps(page_state, ensure_ascii=False, indent=2)}

Instruction : {instruction}

Réponds UNIQUEMENT avec un JSON valide contenant les sections qui doivent être mises à jour. Exemple : {{"hero":{{"title":"...","subtitle":"..."}},"pricing":{{"value_proposition":"..."}}}}
"""


def validate(changes: dict) -> bool:
    if not isinstance(changes, dict):
        return False
    allowed = {"hero", "problem_solution", "program", "social_proof", "pricing", "instructor", "testimonial", "faq"}
    return any(key in allowed for key in changes.keys())


def apply(page_state: dict, changes: dict) -> dict:
    if not validate(changes):
        return page_state
    updated = dict(page_state)
    for section, value in changes.items():
        if isinstance(value, dict):
            updated_section = dict(updated.get(section, {}))
            updated_section.update(value)
            updated[section] = updated_section
        else:
            updated[section] = value
    return updated
