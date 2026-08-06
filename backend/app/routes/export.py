from bson import ObjectId
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from app.db.mongodb import get_campaigns_collection
from app.services.react_export_service import build_react_component

router = APIRouter(prefix="/api/export", tags=["export"])


async def get_generated_campaign(campaign_id: str):
    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc or not doc.get("generated_html"):
        raise HTTPException(404, "Aucune landing page générée pour cette campagne")
    return doc


@router.get("/{campaign_id}/react")
async def export_react_page(campaign_id: str):
    doc = await get_generated_campaign(campaign_id)
    formation_name = doc.get("formation", {}).get("name", "landing-page")
    filename = formation_name.replace(" ", "-").lower()
    component = build_react_component(doc["generated_html"], formation_name)
    return PlainTextResponse(
        component,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}.tsx"'},
    )


@router.get("/{campaign_id}")
async def export_html_page(campaign_id: str):
    doc = await get_generated_campaign(campaign_id)
    filename = doc.get("formation", {}).get("name", "landing-page").replace(" ", "-").lower()
    return PlainTextResponse(
        doc["generated_html"],
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}.html"'},
    )
