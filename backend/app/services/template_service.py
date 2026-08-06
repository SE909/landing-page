from pathlib import Path
from jinja2 import Template

# Template path (supports root /templates or backend/templates)
ROOT_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = Path(__file__).resolve().parents[2]

TEMPLATE_PATHS = [
    ROOT_DIR / "templates" / "formation-default.html",
    BACKEND_DIR / "templates" / "formation-default.html",
]

def get_template_path() -> Path:
    for path in TEMPLATE_PATHS:
        if path.exists():
            return path
    raise FileNotFoundError("Aucun template HTML n'a été trouvé.")

def assemble_html(campaign: dict, ai_content: dict) -> str:
    template_path = get_template_path()
    template_str = template_path.read_text(encoding="utf-8")
    template = Template(template_str)

    return template.render(
        formation_name=campaign["formation"]["name"],
        primary_color=campaign["branding"].get("primary_color", "#2563eb"),
        secondary_color=campaign["branding"].get("secondary_color", "#1e40af"),
        style=campaign["branding"].get("style", "Moderne"),
        user_name=campaign["user_info"]["full_name"],
        user_photo=campaign["user_info"].get("photo_url") or "",
        user_bio=campaign["user_info"]["bio"],
        modules=campaign["formation"]["modules"],
        price=campaign["formation"]["price"],
        currency=campaign["formation"].get("currency", "EUR"),
        bonuses=campaign["formation"].get("bonuses") or "",
        duration_hours=campaign["formation"]["duration_hours"],
        format=campaign["formation"].get("format", "En ligne"),
        testimonials=campaign["social_proof"].get("testimonials", []),
        stats=campaign["social_proof"].get("stats")
        or ai_content.get("social_proof", {}).get("highlight_stat", ""),
        content=ai_content,
    )
