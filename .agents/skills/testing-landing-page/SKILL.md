---
name: testing-landing-page
description: How to run and end-to-end test the AI Crafters landing-page app (FastAPI backend + React/Vite frontend) locally, including MongoDB, the Ollama-less generation fallback, and the OpenAI chat panel with a fake OpenAI server.
---

# Testing the landing-page app locally

## Services to start

1. **MongoDB** — usually not installed on the box. Docker is the fastest path:
   ```bash
   docker run -d --name mongo-test -p 27017:27017 mongo:6
   ```
   Backend defaults to `mongodb://localhost:27017`, database `landing_page_creator`,
   collection `campaigns`.
2. **Backend**:
   ```bash
   cd backend && python3 -m venv venv && venv/bin/pip install -r requirements.txt
   venv/bin/uvicorn app.main:app --port 8000       # health: /api/health
   ```
3. **Frontend**:
   ```bash
   cd frontend && npm install && npm run dev       # :5173, vite proxies /api -> :8000
   ```

## Ollama

Ollama is typically unavailable. This is fine: the generation route catches the
connection error and `generate_fallback_content` produces deterministic French copy, so
`POST /api/campaigns/{id}/generate` still yields a full 6-section `page_state`
(hero, problem_solution, program, social_proof, pricing, instructor) plus `generated_html`.
Do not install Ollama just to test generation.

## Chat panel / OpenAI

`POST /api/campaigns/{id}/chat` requires `OPENAI_API_KEY`. Two useful modes:

- **Error path**: leave `OPENAI_API_KEY` empty in `backend/.env`, restart uvicorn, and the
  chat panel shows a red French box "Clé OpenAI manquante : définissez OPENAI_API_KEY dans le
  fichier .env du backend." Good adversarial check; preview should stay unchanged.
- **Happy path with a fake OpenAI** (no real key needed). In `backend/.env` (gitignored,
  never commit):
  ```env
  OPENAI_API_KEY=test-key
  OPENAI_BASE_URL=http://127.0.0.1:8899
  ```
  Run a tiny stub HTTP server answering `POST /chat/completions` with
  `{"choices":[{"message":{"content":"{\"reply\":\"...\",\"updates\":{\"hero\":{\"title\":\"NOUVEAU TITRE\"}},\"visibility\":{}}"}}]}`.
  `backend/tests/test_chat_route.py` contains exactly such a stub to copy. Keying the stub off
  the user prompt (e.g. "bouton" -> `hero.cta_text`, "prix" -> `pricing.headline`) lets you
  exercise several sections deterministically. **Restart uvicorn after every `.env` change** —
  settings are read at import time.

## UI walkthrough (French)

- `/` → wizard. Click "💡 Remplir avec un exemple" to prefill from `sampleFormData`
  (`frontend/src/types/campaign.ts`), then "Suivant →" ×4 and generate; it navigates to
  `/preview/<24-hex-id>`.
- `/preview/:id` renders `LivePreview` with the chat panel passed via the `aside` prop:
  controls "⛶ Plein écran", "Exporter (.html)", viewport toggles, and a transient
  "✓ Aperçu mis à jour" badge (1.5 s) after each chat-driven HTML update.
- The preview is an **iframe with `srcDoc`** whose height is auto-grown to the full content
  height, so the iframe itself never scrolls. The real scrolling element is the **outer window**
  in normal view and the **viewer container** (`viewerRef`, the `flex-1 overflow-auto` div) in
  full screen. Any scroll save/restore logic must target those, not `frame.contentWindow`.

## Testing scroll preservation across chat updates

This is the easiest thing to get wrong or to "pass" by accident:

1. **Wait for the iframe to finish growing** before scrolling (the load/+300ms/+1200ms resize
   passes). Scrolling too early gives a bogus precondition.
2. **Prove the precondition** — don't trust the screenshot alone. Check the real offset in the
   browser console: `window.scrollY` (normal view) or the viewer div's `scrollTop`
   (full screen). If it is 0, the test is inconclusive, not a pass.
3. **Make every edit visibly different.** Have the fake OpenAI stub return a *versioned* value
   (e.g. `NOUVEAU TITRE PERCUTANT V<n>`, `Un investissement serein V<n>`) so a bumped number
   proves the HTML genuinely re-rendered; otherwise a no-op update looks like a pass.
4. Screenshot immediately after the edit **and again ~3 s later**, since the restore logic
   holds a `restoring` flag for ~1.5 s and re-restores on each resize pass.
5. In full screen the chat input scrolls out of view along with the preview. Workaround: click
   the input at the top of the overlay, type the message, scroll the viewer down to the target
   region, then press Enter — focus survives the scroll.
- Escape exits fullscreen and `document.body.style.overflow` should be restored.

## Verifying persistence

```bash
docker exec mongo-test mongosh landing_page_creator --quiet --eval \
 'const d=db.campaigns.findOne({}); print(d.page_state.sections.map(s=>s.id)); print(d.generated_html.length)'
```
Both `page_state` and `generated_html` must be updated after each chat edit, and
"Exporter (.html)" (downloads to `~/Downloads`) must contain the edited copy.

## Devin Secrets Needed

None. Mongo is local and the OpenAI key can be faked with a local stub; a real
`OPENAI_API_KEY` is only needed to test against the actual OpenAI API.
