import asyncio

from app.services.chatbot_service import process_conversation


PAGE_STATE = {
    "hero": {"title": "Hi", "subtitle": "Hello", "cta_text": "Join now"},
    "problem_solution": {"problem_title": "P", "problem_text": "P", "solution_title": "S", "solution_text": "S"},
    "program": {"intro": "I", "skills": ["skill"]},
    "social_proof": {"headline": "H", "highlight_stat": "Stat"},
    "pricing": {"headline": "Price", "value_proposition": "Value", "cta_text": "Buy", "guarantee": "Guarantee"},
    "instructor": {"headline": "Instructor", "bio_highlight": "Bio"},
}


async def main():
    result = await process_conversation(
        PAGE_STATE,
        "Rends le titre plus direct et ajoute un CTA puissant",
    )
    print(result["message"])


if __name__ == "__main__":
    asyncio.run(main())
