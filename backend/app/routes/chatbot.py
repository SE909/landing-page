from datetime import datetime
import logging
from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.db.mongodb import get_campaigns_collection
from app.services.ai_generation_service import generate_section_content
from app.services.chatbot_service import process_instruction
from app.services.html_assembler import assemble_html
from app.services.html_validator import validate_and_clean_html
from app.services.prompt_builder import build_content_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/campaigns", tags=["chatbot"])


@router.post("/{campaign_id}/chat")
async def chat_with_campaign(campaign_id: str, payload: dict):
    instruction = payload.get("instruction")
    if not instruction:
        raise HTTPException(400, "Instruction manquante")

    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(404, "Campagne introuvable")

    campaign = {k: v for k, v in doc.items() if k != "_id"}
    page_state = doc.get("page_state")

    if page_state is None:
        prompt = build_content_prompt(campaign)
        page_state = await generate_section_content(prompt, campaign=campaign)

    try:
        result = await process_instruction(page_state, instruction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error while processing chatbot instruction.")
        raise HTTPException(status_code=500, detail="Erreur interne du chatbot. Consultez les logs du serveur.")

    campaign["page_state"] = result["page_state"]
    html = validate_and_clean_html(assemble_html(campaign, result["page_state"]))

    await col.update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "page_state": result["page_state"],
                "generated_html": html,
                "updated_at": datetime.utcnow(),
            }
        },
    )

    return {
        "skill": result["skill"],
        "changes": result["changes"],
        "page_state": result["page_state"],
        "html": html,
    }
