import asyncio
import json
from app.config import settings
from app.services.chatbot_service import process_instruction
page_state = {
    'hero': {'title': 'Hi', 'subtitle': 'Hello', 'cta_text': 'Join now'},
    'problem_solution': {'problem_title': 'P', 'problem_text': 'P', 'solution_title': 'S', 'solution_text': 'S'},
    'program': {'intro': 'I', 'skills': ['skill']},
    'social_proof': {'headline': 'H', 'highlight_stat': 'Stat'},
    'pricing': {'headline': 'Price', 'value_proposition': 'Value', 'cta_text': 'Buy', 'guarantee': 'Guarantee'},
    'instructor': {'headline': 'Instructor', 'bio_highlight': 'Bio'}
}
print('OPENAI_KEY', repr(settings.openai_api_key))
print('OPENAI_URL', settings.openai_base_url)
print('OLLAMA_URL', settings.ollama_base_url)
print('Starting process_instruction')
async def main():
    try:
        result = await process_instruction(page_state, 'Rends le titre plus direct et ajoute un CTA puissant')
        print('RESULT', result)
    except Exception as e:
        import traceback
        traceback.print_exc()
asyncio.run(main())
