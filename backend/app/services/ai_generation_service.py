from app.services.ollama_service import generate_with_ollama

async def generate_section_content(prompt: str, campaign: dict = None) -> dict:
    return await generate_with_ollama(prompt, campaign=campaign)
