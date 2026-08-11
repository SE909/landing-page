import importlib
import logging
from typing import Any

from app.config import settings
from app.services.openai_service import generate_with_openai, OpenAIConfigurationError, OpenAIServiceError

logger = logging.getLogger(__name__)

SKILL_MODULES = [
    "app.skills.edit_hero",
    "app.skills.edit_cta",
    "app.skills.edit_colors",
    "app.skills.add_section",
    "app.skills.remove_section",
    "app.skills.improve_copy",
]


def load_skills():
    skills = []
    for module_name in SKILL_MODULES:
        module = importlib.import_module(module_name)
        skills.append(module)
    return skills


def choose_skill(instruction: str, skills: list[object]) -> object:
    for skill in skills:
        if skill.matches(instruction):
            return skill
    return skills[-1]


def create_skill_payload(skill: object, page_state: dict, instruction: str) -> dict[str, Any]:
    return {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": f"Tu es un assistant IA qui applique la compétence {skill.name}."},
            {"role": "user", "content": skill.build_prompt(page_state, instruction)},
        ],
        "temperature": 0.7,
        "max_tokens": 2048,
    }


async def try_skill(skill: object, page_state: dict, instruction: str) -> tuple[object, dict]:
    payload = create_skill_payload(skill, page_state, instruction)
    response = await generate_with_openai(payload, campaign=page_state)

    if not isinstance(response, dict):
        raise ValueError("Le service de génération a renvoyé un format invalide.")

    if not skill.validate(response):
        raise ValueError("La réponse de la compétence est invalide.")

    return skill, response


async def process_instruction(page_state: dict, instruction: str) -> dict:
    skills = load_skills()
    selected_skill = choose_skill(instruction, skills)

    try:
        selected_skill, response = await try_skill(selected_skill, page_state, instruction)
    except OpenAIConfigurationError as config_error:
        logger.warning(
            f"OpenAI configuration error for instruction '{instruction}': {config_error}"
        )
        raise
    except Exception as first_error:
        logger.warning(f"Skill {selected_skill.name} failed for instruction '{instruction}': {first_error}")
        if selected_skill.name != "Improve Copy":
            fallback_skill = importlib.import_module("app.skills.improve_copy")
            logger.warning("Retrying with fallback Improve Copy skill.")
            try:
                selected_skill, response = await try_skill(fallback_skill, page_state, instruction)
            except OpenAIConfigurationError as fallback_config_error:
                logger.error(
                    f"Fallback Improve Copy also failed due to OpenAI configuration for instruction '{instruction}': {fallback_config_error}"
                )
                raise
            except Exception as fallback_error:
                logger.error(
                    f"Fallback Improve Copy also failed for instruction '{instruction}': {fallback_error}"
                )
                raise ValueError(
                    "Le chatbot n'a pas pu traiter l'instruction. Vérifiez que la clé OpenAI est configurée et que le service est disponible."
                ) from fallback_error
        else:
            raise ValueError(
                "Le chatbot n'a pas pu traiter l'instruction. Vérifiez que la clé OpenAI est configurée et que le service est disponible."
            ) from first_error

    updated_state = selected_skill.apply(page_state, response)
    return {
        "skill": selected_skill.name,
        "changes": response,
        "page_state": updated_state,
    }
