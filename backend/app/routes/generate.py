from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.db.mongodb import get_campaigns_collection
from app.services.html_assembler import assemble_html
from app.services.html_validator import validate_and_clean_html
from app.services.ollama_service import generate_section_content
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
    ai_content = await generate_section_content(prompt, campaign=campaign)
    raw_html = assemble_html(campaign, ai_content)
    html = validate_and_clean_html(raw_html)

    await col.update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {
                "generated_html": html,
                "status": "generated",
                "updated_at": datetime.utcnow(),
            }
        },
    )
    return {"html": html, "status": "generated"}


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
