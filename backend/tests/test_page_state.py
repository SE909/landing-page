import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.html_assembler import assemble_html
from app.services.html_validator import validate_and_clean_html
from app.services.page_state import build_page_state, page_state_to_content

CAMPAIGN = {
    "user_info": {"full_name": "Sara E.", "email": "sara@example.com", "bio": "Formatrice IA."},
    "formation": {
        "name": "Prompt Engineering",
        "category": "IA",
        "target_audience": "les développeurs",
        "level": "Débutant",
        "duration_hours": 12,
        "format": "En ligne",
        "short_description": "Formation IA",
        "objectives": "Maîtriser les prompts",
        "modules": [{"title": "Bases", "description": "Intro", "duration": "2h"}],
        "price": 499.0,
        "currency": "EUR",
    },
    "branding": {"tone": "Professionnel", "primary_color": "#2563eb", "secondary_color": "#1e40af", "style": "Moderne"},
    "social_proof": {"testimonials": [], "stats": None},
}

SECTION_IDS = ["hero", "problem_solution", "program", "social_proof", "pricing", "instructor"]


def _check(page_state):
    assert page_state["version"] == 1
    assert [s["id"] for s in page_state["sections"]] == SECTION_IDS
    for section in page_state["sections"]:
        for value in section["props"].values():
            assert value, f"empty prop in {section['id']}"
    html = validate_and_clean_html(assemble_html(CAMPAIGN, page_state_to_content(page_state)))
    assert "<html" in html.lower()
    return html


def test_page_state_format():
    raw = {
        "sections": [
            {"id": "hero", "props": {"title": "Devenez expert du prompt", "subtitle": "En 12h", "cta_text": "Je m'inscris"}},
            {"id": "program", "props": {"intro": "Programme complet", "skills": ["Prompting", "Évaluation"]}},
        ]
    }
    page_state = build_page_state(CAMPAIGN, raw)
    hero = page_state["sections"][0]["props"]
    assert hero["title"] == "Devenez expert du prompt"
    # missing sections are filled from the fallback content
    assert page_state["sections"][SECTION_IDS.index("pricing")]["props"]["cta_text"]
    assert "Devenez expert du prompt" in _check(page_state)


def test_legacy_flat_format():
    raw = {"hero": {"title": "Titre legacy", "subtitle": "Sous-titre", "cta_text": "Go"}}
    page_state = build_page_state(CAMPAIGN, raw)
    assert page_state["sections"][0]["props"]["title"] == "Titre legacy"
    _check(page_state)


def test_garbage_input_falls_back():
    page_state = build_page_state(CAMPAIGN, {"unexpected": "<h1>HTML</h1>"})
    _check(page_state)


def test_hidden_section_excluded_from_html():
    page_state = build_page_state(CAMPAIGN, {})
    page_state["sections"][0]["visible"] = False
    assert "hero" not in page_state_to_content(page_state)


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_"):
            fn()
            print(f"{name}: OK")
