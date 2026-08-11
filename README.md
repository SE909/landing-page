# Landing Page Creator

Générateur de landing pages pour formations — FastAPI + React + MongoDB + Ollama.

## Prérequis

- Python 3.11+
- Node.js 18+
- MongoDB (local ou Atlas)
- Ollama avec le modèle `llama3.2:3b`

```powershell
ollama pull llama3.2:3b
```

## Lancement

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Ouvrir http://localhost:5173

## Chatbot de la page (OpenAI)

La génération reste sur Ollama. Le chatbot de l'écran d'aperçu utilise OpenAI et sait :

- répondre aux questions sur la page (conseils, critiques, explications d'une section) sans rien modifier ;
- appliquer une modification, via l'outil `apply_edits`, qui ne touche que le `page_state` structuré ;
  le HTML est ensuite réassemblé par le template.

Il refuse explicitement ce qu'il ne peut pas faire plutôt que de modifier autre chose : les images
(photo du formateur, logo) passent par `/api/upload` et ne sont pas éditables, et une demande dont
aucune modification n'a pu être retenue le dit clairement au lieu de prétendre avoir réussi.

Dans `backend/.env` :

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```

Modèles possibles : `gpt-4o-mini` (le moins cher), `gpt-4.1-mini` (défaut, meilleur raisonnement),
`gpt-4o` / `gpt-4.1` (les plus pertinents pour le copywriting et les conseils).

## Skills

Un skill est une réécriture complète de la page en un clic, affichée sous forme de bouton dans
l'assistant. Techniquement, c'est un prompt enregistré envoyé au même outil `apply_edits` : il ne
peut donc modifier que des propriétés connues du `page_state`.

Skill disponible : **🇬🇧 Traduire en anglais**.

Pour en ajouter un, il suffit d'une entrée dans `SKILLS` (`backend/app/services/skills.py`) ; le
bouton apparaît automatiquement (`GET /api/skills`).

## Changer de modèle Ollama

Dans `backend/.env` :

```env
OLLAMA_MODEL=llama3.2:7b
```

Puis : `ollama pull llama3.2:7b`

## Activation de l'Assistant de modification IA

Pour utiliser le chatbot de modification, ajoutez votre clé OpenAI dans `backend/.env` :

```env
OPENAI_API_KEY=sk-...your-key...
```

Puis redémarrez le backend.

## Structure

- **Wizard 5 étapes** : formateur, formation, branding, preuve sociale, récap
- **Génération IA** : Ollama produit un `page_state` JSON structuré, assemblé dans un template HTML fixe
- **Chatbot** : OpenAI modifie le `page_state`, jamais le HTML
- **Preview live** + **Export HTML** + **Régénérer**

## Tests backend

```powershell
cd backend
python -m tests.test_page_state
python -m tests.test_generate_route
python -m tests.test_chat_route
```
