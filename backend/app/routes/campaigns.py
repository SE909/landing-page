from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException
import importlib
from datetime import datetime

from app.services.html_assembler import assemble_html
from app.services.html_validator import validate_and_clean_html

from app.db.mongodb import get_campaigns_collection
from app.models.campaign import CampaignCreate, CampaignResponse

router = APIRouter(prefix="/api/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignResponse)
async def create_campaign(data: CampaignCreate):
    col = get_campaigns_collection()
    now = datetime.utcnow()
    doc = data.model_dump()
    doc.update(
        status="draft",
        page_state=None,
        generated_html=None,
        created_at=now,
        updated_at=now,
    )
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


@router.post("/{campaign_id}/edit")
async def edit_campaign(campaign_id: str, payload: dict):
    """Apply a structured edit to a campaign's page_state.

    payload: { section: str, changes: dict, author?: str }
    """
    section = payload.get("section")
    changes = payload.get("changes")
    author = payload.get("author") or "unknown"

    if not section or not isinstance(changes, dict):
        raise HTTPException(status_code=400, detail="section et changes sont requis")

    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(404, "Campagne introuvable")

    page_state = doc.get("page_state") or {}

    # Map some sections to skill modules when available
    SECTION_SKILL_MAP = {
        "hero": "app.skills.edit_hero",
        "cta": "app.skills.edit_cta",
        "colors": "app.skills.edit_colors",
    }

    updated_state = dict(page_state)
    skill_used = None

    if section in SECTION_SKILL_MAP:
        module = importlib.import_module(SECTION_SKILL_MAP[section])
        # validate changes using skill validator if present
        try:
            if not module.validate(changes):
                raise HTTPException(status_code=400, detail="Changements invalides pour la section")
        except AttributeError:
            # no validate function, continue
            pass

        updated_state = module.apply(updated_state, changes)
        skill_used = getattr(module, "name", section)
    else:
        # Generic merge for unknown sections
        target = dict(updated_state.get(section, {}))
        target.update(changes)
        updated_state[section] = target
        skill_used = "direct"

    # Build new HTML preview and persist
    campaign = {k: v for k, v in doc.items() if k != "_id"}
    campaign["page_state"] = updated_state
    html = validate_and_clean_html(assemble_html(campaign, updated_state))

    change_entry = {
        "author": author,
        "section": section,
        "changes": changes,
        "skill": skill_used,
        "timestamp": datetime.utcnow(),
    }

    await col.update_one(
        {"_id": ObjectId(campaign_id)},
        {
            "$set": {"page_state": updated_state, "generated_html": html, "updated_at": datetime.utcnow()},
            "$push": {"change_log": change_entry},
        },
    )

    return {"page_state": updated_state, "html": html, "change": change_entry}
