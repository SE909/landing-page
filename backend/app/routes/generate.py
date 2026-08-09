from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.db.mongodb import get_campaigns_collection
from app.services.html_assembler import assemble_html
from app.services.html_validator import validate_and_clean_html
from app.services.ollama_service import generate_section_content
from app.services.page_state import build_page_state, page_state_to_content
from app.services.prompt_builder import build_content_prompt

router = APIRouter(prefix="/api/campaigns", tags=["generate"])


@router.post("/{campaign_id}/generate")
async def generate_landing_page(campaign_id: str):
    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(404, "Campagne introuvable")

    campaign = {k: v for k, v in doc.items() if k != "_id"}
    prompt = build_content_prompt(campaign)
    raw_content = await generate_section_content(prompt, campaign=campaign)
    page_state = build_page_state(campaign, raw_content)
    raw_html = assemble_html(campaign, page_state_to_content(page_state))
    html = validate_and_clean_html(raw_html)

    await col.update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "page_state": page_state,
                "generated_html": html,
                "status": "generated",
                "updated_at": datetime.utcnow(),
            }
        },
    )
    return {"html": html, "page_state": page_state, "status": "generated"}


@router.get("/{campaign_id}/export")
async def export_html(campaign_id: str):
    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc or not doc.get("generated_html"):
        raise HTTPException(404, "Aucune page générée")
    filename = doc["formation"]["name"].replace(" ", "-").lower()
    return PlainTextResponse(
        doc["generated_html"],
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}.html"'},
    )
