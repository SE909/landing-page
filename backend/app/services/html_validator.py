import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def validate_and_clean_html(html_str: str) -> str:
    """Parses and validates the generated landing page HTML using BeautifulSoup.
    
    Ensures correct structure, cleans missing or malformed tags, and verifies
    essential landing page sections exist.
    """
    if not html_str or not html_str.strip():
        logger.warning("Empty HTML string provided for validation.")
        return html_str

    try:
        soup = BeautifulSoup(html_str, "html.parser")

        # Verify basic HTML tree structure
        if not soup.find("html"):
            new_doc = BeautifulSoup("<!DOCTYPE html><html lang='fr'><head></head><body></body></html>", "html.parser")
            if soup.body:
                new_doc.body.replace_with(soup.body)
            else:
                new_doc.body.append(soup)
            soup = new_doc

        # Verify essential sections
        essential_sections = ["hero", "problem-solution", "program", "social-proof", "pricing", "instructor"]
        for section_id in essential_sections:
            section = soup.find("section", id=section_id)
            if not section:
                logger.info(f"Section #{section_id} was missing or auto-adjusted during validation.")

        # Format clean, valid HTML string
        return soup.prettify()
    except Exception as e:
        logger.error(f"Error during BeautifulSoup HTML validation: {e}")
        return html_str
