import json

import httpx
import pytest
from bson import ObjectId

from app.main import app
from app.routes import chatbot
from app.services import chatbot_service


class FakeCollection:
    def __init__(self, document: dict):
        self.document = document

    async def find_one(self, query: dict):
        requested_id = query.get("_id")
        if requested_id == self.document["_id"]:
            return self.document
        return None

    async def update_one(self, query: dict, update: dict):
        assert query["_id"] == self.document["_id"]
        for key, value in update.get("$set", {}).items():
            self.document[key] = value
        for key, value in update.get("$push", {}).items():
            self.document.setdefault(key, []).append(value)
        for key, value in update.get("$pull", {}).items():
            self.document[key] = [
                item
                for item in self.document.get(key, [])
                if not all(item.get(field) == expected for field, expected in value.items())
            ]


def campaign_document() -> dict:
    return {
        "_id": ObjectId(),
        "formation": {
            "name": "Formation test",
            "duration_hours": 10,
            "format": "En ligne",
            "price": 99,
            "currency": "EUR",
            "modules": [],
        },
        "branding": {
            "primary_color": "#2563EB",
            "secondary_color": "#1E40AF",
            "tone": "professionnel",
            "style": "Moderne",
        },
        "user_info": {"full_name": "Alice", "bio": "Formatrice"},
        "social_proof": {"testimonials": []},
        "page_state": {
            "hero": {"title": "Ancien titre", "subtitle": "Ancien sous-titre", "cta_text": "Réserver"},
            "pricing": {"headline": "Offre", "value_proposition": "Valeur", "cta_text": "Réserver"},
            "branding": {"primary_color": "#2563EB", "secondary_color": "#1E40AF"},
        },
        "pending_proposals": [],
        "change_log": [],
        "chat_history": [],
    }


def assistant_message(content: str = "", tool_calls: list[dict] | None = None) -> dict:
    return {"role": "assistant", "content": content, "tool_calls": tool_calls or []}


def tool_call(call_id: str, name: str, arguments: dict) -> dict:
    return {
        "id": call_id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(arguments)},
    }


def completion_sequence(monkeypatch, responses: list[dict]):
    queued = iter(responses)

    async def fake_completion(payload: dict) -> dict:
        return next(queued)

    monkeypatch.setattr(chatbot_service, "create_chat_completion", fake_completion)


@pytest.fixture
def fake_collection(monkeypatch):
    collection = FakeCollection(campaign_document())
    monkeypatch.setattr(chatbot, "get_campaigns_collection", lambda: collection)
    return collection


@pytest.fixture
async def client():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_question_without_tool_returns_message_without_proposal(monkeypatch, fake_collection, client):
    completion_sequence(monkeypatch, [assistant_message("Cette page propose une formation en ligne.")])

    response = await client.post(
        f"/api/campaigns/{fake_collection.document['_id']}/chat",
        json={"instruction": "Qu'est-ce que cette page propose ?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {"message": "Cette page propose une formation en ligne."}
    assert "proposal" not in body


@pytest.mark.asyncio
async def test_single_tool_call_creates_natural_message_and_preview(monkeypatch, fake_collection, client):
    completion_sequence(
        monkeypatch,
        [
            assistant_message(tool_calls=[tool_call("call_hero", "edit_hero", {"title": "Bienvenue"})]),
            assistant_message("J’ai préparé le nouveau titre « Bienvenue ». Vous pouvez le confirmer."),
        ],
    )

    response = await client.post(
        f"/api/campaigns/{fake_collection.document['_id']}/chat",
        json={"instruction": "Change le titre en Bienvenue"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["message"].startswith("J’ai préparé")
    assert body["proposal"]["html_preview"]
    assert "{" not in body["message"]
    pending = fake_collection.document["pending_proposals"]
    assert len(pending) == 1
    assert pending[0]["page_state"]["hero"]["title"] == "Bienvenue"


@pytest.mark.asyncio
async def test_multiple_tool_calls_are_grouped_in_one_ordered_proposal(monkeypatch, fake_collection, client):
    completion_sequence(
        monkeypatch,
        [
            assistant_message(
                tool_calls=[
                    tool_call("call_hero", "edit_hero", {"title": "Nouveau titre"}),
                    tool_call("call_color", "edit_colors", {"primary_color": "#0000FF"}),
                ]
            ),
            assistant_message("J’ai préparé le nouveau titre et la couleur bleue. Vous pouvez confirmer."),
        ],
    )

    response = await client.post(
        f"/api/campaigns/{fake_collection.document['_id']}/chat",
        json={"instruction": "Change le titre et la couleur principale en bleu"},
    )

    assert response.status_code == 200
    pending = fake_collection.document["pending_proposals"]
    assert len(pending) == 1
    assert [change["tool"] for change in pending[0]["changes"]] == ["edit_hero", "edit_colors"]
    assert pending[0]["page_state"]["hero"]["title"] == "Nouveau titre"
    assert pending[0]["page_state"]["branding"]["primary_color"] == "#0000FF"


@pytest.mark.asyncio
async def test_invalid_tool_arguments_are_rephrased_without_json(monkeypatch, fake_collection, client):
    completion_sequence(
        monkeypatch,
        [
            assistant_message(tool_calls=[tool_call("call_color", "edit_colors", {"primary_color": "super rouge"})]),
            assistant_message("Je ne peux pas utiliser « super rouge ». Donnez-moi une couleur au format #RRGGBB."),
        ],
    )

    response = await client.post(
        f"/api/campaigns/{fake_collection.document['_id']}/chat",
        json={"instruction": "Mets la couleur en super rouge"},
    )

    assert response.status_code == 200
    body = response.json()
    assert "proposal" not in body
    assert body["message"].startswith("Je ne peux pas")
    assert "{" not in body["message"]
    assert not fake_collection.document["pending_proposals"]


@pytest.mark.asyncio
async def test_confirming_proposal_persists_page_state_and_html(monkeypatch, fake_collection, client):
    completion_sequence(
        monkeypatch,
        [
            assistant_message(tool_calls=[tool_call("call_hero", "edit_hero", {"title": "Titre confirmé"})]),
            assistant_message("La modification est prête à être confirmée."),
        ],
    )
    proposal_response = await client.post(
        f"/api/campaigns/{fake_collection.document['_id']}/chat",
        json={"instruction": "Change le titre"},
    )
    proposal_id = proposal_response.json()["proposal"]["id"]

    confirmation = await client.post(
        f"/api/campaigns/{fake_collection.document['_id']}/chat",
        json={"apply": True, "proposal_id": proposal_id},
    )

    assert confirmation.status_code == 200
    assert confirmation.json()["message"] == "La modification est maintenant appliquée à votre landing page."
    assert fake_collection.document["page_state"]["hero"]["title"] == "Titre confirmé"
    assert fake_collection.document["generated_html"] == confirmation.json()["html"]
    assert fake_collection.document["pending_proposals"] == []
