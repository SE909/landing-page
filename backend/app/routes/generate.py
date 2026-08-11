from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.db.mongodb import get_campaigns_collection
from app.services.generation import generate_page

router = APIRouter(prefix="/api/campaigns", tags=["generate"])


@router.post("/{campaign_id}/generate")
async def generate_landing_page(campaign_id: str):
    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(404, "Campagne introuvable")

    campaign = {k: v for k, v in doc.items() if k != "_id"}
    page_state, html = await generate_page(campaign)

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
