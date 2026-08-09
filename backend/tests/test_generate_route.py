"""End-to-end check of POST /api/campaigns/{id}/generate with a stubbed Mongo collection."""

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
from app.routes import generate as generate_route
from tests.test_page_state import CAMPAIGN, SECTION_IDS

OLLAMA_REPLY = {
    "sections": [
        {"id": "hero", "props": {"title": "Titre Ollama", "subtitle": "Sous-titre", "cta_text": "Go"}}
    ]
}


class FakeOllamaHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        assert self.path == "/api/generate" and body["format"] == "json"
        payload = json.dumps({"response": json.dumps(OLLAMA_REPLY)}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *args):
        pass


class FakeCollection:
    def __init__(self, doc):
        self.doc = doc

    async def find_one(self, query):
        return self.doc if query["_id"] == self.doc["_id"] else None

    async def update_one(self, query, update):
        self.doc.update(update["$set"])


async def run_case(expected_hero_title: str):
    doc = {"_id": ObjectId(), **CAMPAIGN, "status": "draft", "page_state": None, "generated_html": None}
    collection = FakeCollection(doc)
    generate_route.get_campaigns_collection = lambda: collection

    app = FastAPI()
    app.include_router(generate_route.router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(f"/api/campaigns/{doc['_id']}/generate")

    assert res.status_code == 200, res.text
    body = res.json()
    assert [s["id"] for s in body["page_state"]["sections"]] == SECTION_IDS
    assert doc["page_state"] == body["page_state"], "page_state must be persisted"
    assert doc["generated_html"] == body["html"] and "<html" in body["html"].lower()
    assert doc["status"] == "generated"
    assert body["page_state"]["sections"][0]["props"]["title"] == expected_hero_title


async def main():
    server = HTTPServer(("127.0.0.1", 0), FakeOllamaHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    settings.ollama_base_url = f"http://127.0.0.1:{server.server_port}"
    await run_case("Titre Ollama")
    print("generate route with Ollama JSON: OK")

    server.shutdown()
    settings.ollama_base_url = "http://127.0.0.1:1"  # Ollama offline -> fallback content
    await run_case("Maîtrisez Prompt Engineering dès aujourd'hui")
    print("generate route with Ollama offline: OK")


if __name__ == "__main__":
    asyncio.run(main())
