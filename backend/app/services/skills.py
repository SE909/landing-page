"""Skills: one-click rewrites of the whole page.

A skill is just a stored prompt sent through the same OpenAI `apply_edits` tool
as the chatbot, so it can only touch known `page_state` properties. Adding a
skill means adding an entry here — no new code path.
"""

from typing import Optional

from pydantic import BaseModel


class Skill(BaseModel):
    id: str
    label: str
    icon: str
    description: str
    prompt: str
    # Set when the skill changes the language of the page (stored in page_state.meta).
    language: Optional[str] = None


SKILLS: list[Skill] = [
    Skill(
        id="translate_en",
        label="Traduire en anglais",
        icon="🇬🇧",
        description="Traduit toute la page en anglais en conservant la structure.",
        language="en",
        prompt=(
            "Traduis en anglais TOUS les textes de la page. Renvoie, via l'outil apply_edits, "
            "chaque section avec chaque propriété traduite : ne laisse aucun texte en français. "
            "Garde exactement les mêmes sections, les mêmes propriétés et la même longueur "
            "approximative. Adapte les tournures pour qu'elles sonnent naturelles en anglais "
            "plutôt que de traduire mot à mot, et garde les noms propres, les prix et les "
            "chiffres tels quels. Le champ `reply` doit rester en français."
        ),
    ),
]

SKILLS_BY_ID = {skill.id: skill for skill in SKILLS}


def get_skill(skill_id: str) -> Optional[Skill]:
    return SKILLS_BY_ID.get(skill_id)
