from datetime import datetime
from typing import Any, Literal, Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.db.mongodb import get_campaigns_collection
from app.services.generation import generate_page, render_html
from app.services.openai_service import OpenAIError, edit_page_state
from app.services.page_state import apply_updates
from app.services.skills import SKILLS, Skill, get_skill

router = APIRouter(prefix="/api/campaigns", tags=["chat"])
skills_router = APIRouter(prefix="/api/skills", tags=["skills"])


@skills_router.get("", response_model=list[Skill])
async def list_skills():
    return SKILLS


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str
    history: list[ChatMessage] = []
    # When set, the message is replaced by the skill's prompt and an edit is forced.
    skill_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    changed: list[str]
    page_state: dict[str, Any]
    html: Optional[str] = None


@router.post("/{campaign_id}/chat", response_model=ChatResponse)
async def chat_edit(campaign_id: str, body: ChatRequest):
    skill = get_skill(body.skill_id) if body.skill_id else None
    if body.skill_id and not skill:
        raise HTTPException(404, "Skill inconnu")
    if not skill and not body.message.strip():
        raise HTTPException(400, "Message vide")

    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(404, "Campagne introuvable")

    campaign = {k: v for k, v in doc.items() if k != "_id"}
    page_state = doc.get("page_state")
    if not page_state:
        # Older campaigns only have generated_html: rebuild the structured state with Ollama.
        page_state, html = await generate_page(campaign)
        await col.update_one(
            {"_id": doc["_id"]},
            {"$set": {"page_state": page_state, "generated_html": html, "status": "generated"}},
        )

    try:
        result = await edit_page_state(
            skill.prompt if skill else body.message,
            page_state,
            [] if skill else [m.model_dump() for m in body.history],
            force_edit=skill is not None,
        )
    except OpenAIError as exc:
        raise HTTPException(502, str(exc)) from exc

    updated_state, changed = apply_updates(page_state, result["updates"], result["visibility"])
    if skill and skill.language and changed:
        updated_state["meta"] = {**updated_state.get("meta", {}), "language": skill.language}
    if not changed:
        return ChatResponse(reply=result["reply"], changed=[], page_state=page_state)

    html = render_html(campaign, updated_state)
    await col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "page_state": updated_state,
                "generated_html": html,
                "status": "generated",
                "updated_at": datetime.utcnow(),
            }
        },
    )
    return ChatResponse(reply=result["reply"], changed=changed, page_state=updated_state, html=html)
