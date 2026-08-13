from datetime import datetime, timezone
import logging
import uuid

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request

from app.config import settings
from app.db.mongodb import get_campaigns_collection
from app.services.ai_generation_service import generate_section_content
from app.services.chatbot_service import MAX_HISTORY_MESSAGES, process_conversation
from app.services.html_assembler import assemble_html
from app.services.html_validator import validate_and_clean_html
from app.services.prompt_builder import build_content_prompt

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/campaigns", tags=["chatbot"])


def _conversation_history(existing: list[dict] | None, user_text: str, assistant_text: str) -> list[dict]:
    history = list(existing or [])
    history.extend(
        [
            {"role": "user", "text": user_text, "created_at": datetime.now(timezone.utc)},
            {"role": "assistant", "text": assistant_text, "created_at": datetime.now(timezone.utc)},
        ]
    )
    return history[-(MAX_HISTORY_MESSAGES * 2) :]


def _validated_preview(campaign: dict, page_state: dict) -> str:
    """Assemble once after the complete tool batch, then validate with BeautifulSoup."""
    preview_campaign = {
        **campaign,
        "branding": {**campaign.get("branding", {}), **page_state.get("branding", {})},
        "page_state": page_state,
    }
    raw_html = assemble_html(preview_campaign, page_state)
    html_preview = validate_and_clean_html(raw_html)
    if not html_preview or not html_preview.strip():
        # validate_and_clean_html already handles malformed markup. This second
        # attempt only protects against an unexpected empty validator result.
        html_preview = validate_and_clean_html(raw_html)
    if not html_preview or not html_preview.strip():
        raise ValueError("La prévisualisation HTML n’a pas pu être générée.")
    return html_preview


@router.post("/{campaign_id}/chat")
async def chat_with_campaign(campaign_id: str, payload: dict, request: Request):
    apply_changes = bool(payload.get("apply", False))
    instruction = payload.get("instruction")
    col = get_campaigns_collection()
    doc = await col.find_one({"_id": ObjectId(campaign_id)})
    if not doc:
        raise HTTPException(404, "Campagne introuvable")

    if apply_changes:
        return await _apply_pending_proposal(col, doc, payload, request)

    if not isinstance(instruction, str) or not instruction.strip():
        raise HTTPException(400, "Instruction manquante")

    campaign = {key: value for key, value in doc.items() if key != "_id"}
    page_state = doc.get("page_state")
    if page_state is None:
        prompt = build_content_prompt(campaign)
        page_state = await generate_section_content(prompt, campaign=campaign)

    try:
        result = await process_conversation(page_state, instruction, doc.get("chat_history", []))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except Exception:
        logger.exception("Unexpected error while processing chatbot instruction.")
        raise HTTPException(status_code=500, detail="Erreur interne du chatbot. Consultez les logs du serveur.")

    message = result["message"]
    history = _conversation_history(doc.get("chat_history"), instruction.strip(), message)
    update_fields = {"chat_history": history, "updated_at": datetime.now(timezone.utc)}

    if not result["edited"]:
        await col.update_one({"_id": doc["_id"]}, {"$set": update_fields})
        return {"message": message}

    try:
        html_preview = _validated_preview(campaign, result["page_state"])
    except ValueError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    proposal_id = uuid.uuid4().hex
    pending = {
        "proposal_id": proposal_id,
        "tools": result["tools"],
        "changes": result["changes"],
        "page_state": result["page_state"],
        "html_preview": html_preview,
        "message": message,
        "created_at": datetime.now(timezone.utc),
    }
    await col.update_one(
        {"_id": doc["_id"]},
        {
            "$push": {"pending_proposals": pending},
            "$set": update_fields,
        },
    )
    return {
        "message": message,
        "proposal": {"id": proposal_id, "html_preview": html_preview},
    }


async def _apply_pending_proposal(col, doc: dict, payload: dict, request: Request):
    proposal_id = payload.get("proposal_id")
    if not isinstance(proposal_id, str) or not proposal_id:
        raise HTTPException(400, "proposal_id requis pour appliquer les modifications")

    api_key = request.headers.get("x-api-key")
    if settings.admin_api_key and api_key != settings.admin_api_key:
        raise HTTPException(401, "Clé API invalide pour l'application des modifications")
    if not settings.admin_api_key:
        logger.warning("Aucune admin_api_key configurée; application autorisée sans authentification")

    pending_list = doc.get("pending_proposals", []) or []
    pending = next((proposal for proposal in pending_list if proposal.get("proposal_id") == proposal_id), None)
    if not pending:
        raise HTTPException(404, "Proposition introuvable ou expirée")

    applied_message = "La modification est maintenant appliquée à votre landing page."
    history = list(doc.get("chat_history", []))
    history.append({"role": "assistant", "text": applied_message, "created_at": datetime.now(timezone.utc)})
    page_state = pending["page_state"]
    await col.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "page_state": page_state,
                "generated_html": pending["html_preview"],
                "branding": {**doc.get("branding", {}), **page_state.get("branding", {})},
                "chat_history": history[-(MAX_HISTORY_MESSAGES * 2) :],
                "updated_at": datetime.now(timezone.utc),
            },
            "$pull": {"pending_proposals": {"proposal_id": proposal_id}},
            "$push": {
                "change_log": {
                    "proposal_id": proposal_id,
                    "applied_by": api_key or "development-mode",
                    "applied_at": datetime.now(timezone.utc),
                    "changes": pending.get("changes", []),
                }
            },
        },
    )
    return {"message": applied_message, "html": pending["html_preview"]}
