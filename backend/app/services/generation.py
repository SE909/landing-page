"""Shared pipeline: campaign -> page_state (Ollama) -> generated_html (assembler)."""

from app.services.html_assembler import assemble_html
from app.services.html_validator import validate_and_clean_html
from app.services.ollama_service import generate_section_content
from app.services.page_state import build_page_state, page_state_to_content
from app.services.prompt_builder import build_content_prompt


def render_html(campaign: dict, page_state: dict) -> str:
    return validate_and_clean_html(assemble_html(campaign, page_state_to_content(page_state)))


async def generate_page(campaign: dict) -> tuple[dict, str]:
    """Generate a structured page_state with Ollama, then derive the HTML from it."""
    raw_content = await generate_section_content(build_content_prompt(campaign), campaign=campaign)
    page_state = build_page_state(campaign, raw_content)
    return page_state, render_html(campaign, page_state)
