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

## Changer de modèle Ollama

Dans `backend/.env` :

```env
OLLAMA_MODEL=llama3.2:7b
```

Puis : `ollama pull llama3.2:7b`

## Structure

- **Wizard 5 étapes** : formateur, formation, branding, preuve sociale, récap
- **Génération IA** : Ollama produit du contenu JSON, assemblé dans un template HTML fixe
- **Preview live** + **Export HTML** + **Régénérer**
