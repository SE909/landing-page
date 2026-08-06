import json


def build_content_prompt(campaign: dict) -> str:
    return f"""Tu es un expert copywriter de landing pages de formations en ligne.

À partir des données suivantes, génère UNIQUEMENT un JSON valide (sans markdown, sans texte avant/après) avec cette structure exacte :

{{
  "hero": {{
    "title": "titre accrocheur avec bénéfice",
    "subtitle": "sous-titre explicatif",
    "cta_text": "Je m'inscris"
  }},
  "problem_solution": {{
    "problem_title": "Le problème",
    "problem_text": "2-3 phrases sur les difficultés du public cible",
    "solution_title": "La solution",
    "solution_text": "2-3 phrases sur comment la formation résout ces blocages"
  }},
  "program": {{
    "intro": "phrase d'introduction du programme",
    "skills": ["compétence 1", "compétence 2", "compétence 3"]
  }},
  "social_proof": {{
    "headline": "Ce que disent nos élèves",
    "highlight_stat": "statistique percutante"
  }},
  "pricing": {{
    "headline": "Investissez dans votre avenir",
    "value_proposition": "2 phrases sur la valeur",
    "cta_text": "Je m'inscris maintenant",
    "guarantee": "phrase de réassurance"
  }},
  "instructor": {{
    "headline": "Votre formateur",
    "bio_highlight": "2 phrases mettant en valeur le formateur"
  }}
}}

Données du formulaire :
{json.dumps(campaign, ensure_ascii=False, indent=2, default=str)}

Ton de voix : {campaign["branding"]["tone"]}
Langue : français
Réponds UNIQUEMENT avec le JSON."""
