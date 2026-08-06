import json
import logging
import re
import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def generate_fallback_content(campaign: dict) -> dict:
    """Fallback generator when Ollama is offline or produces invalid JSON."""
    formation_name = campaign.get("formation", {}).get("name", "Formation")
    user_name = campaign.get("user_info", {}).get("full_name", "Votre Formateur")
    audience = campaign.get("formation", {}).get("target_audience", "les passionnés et professionnels")
    tone = campaign.get("branding", {}).get("tone", "Professionnel")

    return {
        "hero": {
            "title": f"Maîtrisez {formation_name} dès aujourd'hui",
            "subtitle": f"La formation référence conçue par {user_name} pour propulser {audience}.",
            "cta_text": "Je m'inscris maintenant"
        },
        "problem_solution": {
            "problem_title": "Vous faites face à ces obstacles ?",
            "problem_text": f"Trouver une méthode claire pour apprendre {formation_name} peut s'avérer complexe et frustrant sans accompagnement structuré.",
            "solution_title": "Notre Solution Clé en Main",
            "solution_text": f"Grâce à notre programme guidé étape par étape, transformez vos compétences rapidement avec une approche 100% pratique."
        },
        "program": {
            "intro": "Un programme complet et progressif pour atteindre vos objectifs rapidement.",
            "skills": [
                f"Maîtrise des principes de {formation_name}",
                "Mise en pratique sur projets réels",
                "Autonomie et bonnes pratiques professionnelles"
            ]
        },
        "social_proof": {
            "headline": "Rejoignez une communauté d'apprenants satisfaits",
            "highlight_stat": "98% de satisfaction apprenants • +500 personnes formées"
        },
        "pricing": {
            "headline": "Investissez dans vos compétences d'avenir",
            "value_proposition": "Accédez à l'intégralité du contenu, aux ressources téléchargeables et au support individuel.",
            "cta_text": "Réserver ma place",
            "guarantee": "Garantie satisfait ou remboursé sous 14 jours"
        },
        "instructor": {
            "headline": "Votre formateur expert",
            "bio_highlight": f"{user_name} vous guide personnellement à chaque étape de votre apprentissage."
        }
    }


async def generate_section_content(prompt: str, campaign: dict = None) -> dict:
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 2048},
                },
            )
            response.raise_for_status()
            raw = response.json().get("response", "")

        cleaned_raw = re.sub(r"```json\s*", "", raw)
        cleaned_raw = re.sub(r"```\s*", "", cleaned_raw).strip()

        match = re.search(r"\{.*\}", cleaned_raw, re.DOTALL)
        if match:
            return json.loads(match.group())

        logger.warning("Ollama response didn't contain valid JSON structure. Using fallback.")
    except Exception as e:
        logger.warning(f"Ollama generation call failed ({e}). Utilizing copywriting fallback engine.")

    if campaign:
        return generate_fallback_content(campaign)
    raise ValueError("Impossible de générer le contenu et aucun objet campaign fourni.")

