from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException

from app.db.mongodb import get_campaigns_collection
from app.models.campaign import CampaignCreate, CampaignResponse

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignResponse)
async def create_campaign(data: CampaignCreate):
    col = get_campaigns_collection()
    now = datetime.utcnow()
    doc = data.model_dump()
    doc.update(status="draft", generated_html=None, created_at=now, updated_at=now)
    result = await col.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return doc


@router.get("", response_model=list[CampaignResponse])
async def list_campaigns():
    col = get_campaigns_collection()
    cursor = col.find().sort("created_at", -1)
    results = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        results.append(doc)
    return results


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: str):
    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(404, "Campagne introuvable")
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.delete("/{campaign_id}")
async def delete_campaign(campaign_id: str):
    col = get_campaigns_collection()
    res = await col.delete_one({"_id": ObjectId(campaign_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Campagne introuvable")
    return {"message": "Campagne supprimée avec succès"}
