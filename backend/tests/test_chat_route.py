"""Checks POST /api/campaigns/{id}/chat against a fake OpenAI server and a stubbed Mongo."""

import asyncio
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from bson import ObjectId
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.routes import chat as chat_route
from app.services.generation import generate_page
from tests.test_generate_route import FakeCollection
from tests.test_page_state import CAMPAIGN

NEW_TITLE = "Un titre bien plus percutant"
openai_reply = {
    "reply": "J'ai reformulé le titre principal.",
    "updates": {"hero": {"title": NEW_TITLE}, "unknown": {"x": "y"}},
    "visibility": {},
}
last_request: dict = {}


class FakeOpenAIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        assert self.path == "/chat/completions"
        assert self.headers["Authorization"] == "Bearer test-key"
        assert body["response_format"] == {"type": "json_object"}
        last_request.update(body)
        payload = json.dumps(
            {"choices": [{"message": {"content": json.dumps(openai_reply)}}]}
        ).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


def make_app(doc):
    collection = FakeCollection(doc)
    chat_route.get_campaigns_collection = lambda: collection
    app = FastAPI()
    app.include_router(chat_route.router)
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test"), collection


async def main():
    server = HTTPServer(("127.0.0.1", 0), FakeOpenAIHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    settings.openai_base_url = f"http://127.0.0.1:{server.server_port}"
    settings.openai_api_key = "test-key"
    settings.ollama_base_url = "http://127.0.0.1:1"  # generation stays offline -> fallback

    page_state, html = await generate_page(CAMPAIGN)

    # 1. edit an existing page_state
    doc = {"_id": ObjectId(), **CAMPAIGN, "page_state": page_state, "generated_html": html}
    client, collection = make_app(doc)
    async with client:
        res = await client.post(f"/api/campaigns/{doc['_id']}/chat", json={"message": "titre plus fort"})
    assert res.status_code == 200, res.text
    body = res.json()
    hero = body["page_state"]["sections"][0]["props"]
    assert hero["title"] == NEW_TITLE and body["changed"] == ["hero.title"]
    assert NEW_TITLE in body["html"] and collection.doc["generated_html"] == body["html"]
    assert collection.doc["page_state"] == body["page_state"]
    assert "page_state actuel" in last_request["messages"][1]["content"]
    print("chat edits page_state and re-renders html: OK")

    # 2. legacy campaign without page_state must not fail with the old error
    legacy = {"_id": ObjectId(), **CAMPAIGN, "generated_html": html}
    client, collection = make_app(legacy)
    async with client:
        res = await client.post(f"/api/campaigns/{legacy['_id']}/chat", json={"message": "titre plus fort"})
    assert res.status_code == 200, res.text
    assert res.json()["page_state"]["sections"][0]["props"]["title"] == NEW_TITLE
    print("chat rebuilds a missing page_state: OK")

    # 3. no-op answer keeps the page untouched
    openai_reply["updates"] = {}
    previous_html = collection.doc["generated_html"]
    client, collection = make_app({"_id": ObjectId(), **CAMPAIGN, "page_state": page_state, "generated_html": previous_html})
    async with client:
        res = await client.post(f"/api/campaigns/{collection.doc['_id']}/chat", json={"message": "bonjour"})
    assert res.json()["changed"] == [] and res.json()["html"] is None
    assert collection.doc["generated_html"] == previous_html
    print("chat no-op leaves the page unchanged: OK")

    # 4. missing API key surfaces a clear error
    settings.openai_api_key = ""
    client, collection = make_app({"_id": ObjectId(), **CAMPAIGN, "page_state": page_state, "generated_html": html})
    async with client:
        res = await client.post(f"/api/campaigns/{collection.doc['_id']}/chat", json={"message": "salut"})
    assert res.status_code == 502 and "OPENAI_API_KEY" in res.json()["detail"]
    print("chat reports a missing OpenAI key: OK")


if __name__ == "__main__":
    asyncio.run(main())
