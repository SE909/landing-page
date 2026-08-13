# Landing Page Creator

Application full-stack pour créer, personnaliser et exporter des landing pages de formations. Elle associe un assistant de rédaction IA, un éditeur conversationnel et un aperçu responsive (ordinateur, tablette et mobile).

## Fonctionnalités

- Assistant de création en 5 étapes : formateur, formation, identité visuelle, preuve sociale et récapitulatif.
- Génération de contenus par IA avec Ollama, puis assemblage dans un template HTML.
- Aperçu en direct avec formats ordinateur, tablette et mobile.
- Éditeur conversationnel pour ajuster le hero, les CTA, les couleurs, les sections et les textes.
- Historique des campagnes, import d’images et export HTML ou React.
- Propositions de modifications pouvant être confirmées avant d’être enregistrées.

## Technologies

| Partie | Technologies |
| --- | --- |
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| Backend | FastAPI, Pydantic, Motor |
| Données | MongoDB |
| IA | Ollama pour la génération ; API OpenAI pour le chat d’édition |

## Prérequis

- Python 3.11 ou supérieur
- Node.js 18 ou supérieur
- MongoDB, local ou MongoDB Atlas
- [Ollama](https://ollama.com/) avec un modèle téléchargé
- Une clé API OpenAI pour utiliser l’assistant de modification

Téléchargez le modèle Ollama par défaut :

```powershell
ollama pull llama3.2:3b
```

## Installation

### 1. Configurer le backend

Depuis le dossier `backend`, créez un environnement Python et installez les dépendances :

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Créez ensuite un fichier `backend/.env` :

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=landing_page_creator

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5

CORS_ORIGINS=http://localhost:5173
```

`OPENAI_API_KEY` est nécessaire pour le chat d’édition. La génération initiale de la landing utilise Ollama.

### 2. Configurer le frontend

Dans un second terminal :

```powershell
cd frontend
npm install
```

## Lancer le projet

Assurez-vous que MongoDB et Ollama sont démarrés, puis lancez :

```powershell
# Terminal 1 — backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
npm run dev
```

Ouvrez ensuite [http://localhost:5173](http://localhost:5173). L’état de l’API est disponible sur [http://localhost:8000/api/health](http://localhost:8000/api/health).

## Utiliser l’éditeur IA

L’éditeur utilise le *tool calling* natif d’OpenAI. À chaque message, le modèle décide lui-même s’il doit répondre directement en texte naturel (question ou clarification), ou appeler un ou plusieurs outils de modification :

- `edit_hero` : titre, sous-titre et CTA du hero ;
- `edit_cta` : libellés des boutons et appels à l’action ;
- `edit_colors` : palette de couleurs ;
- `add_section` et `remove_section` : structure de la page ;
- `improve_copy` : amélioration du texte.

Les appels d’outils sont validés par le backend. Le chat ne présente que la réponse naturelle de l’assistant, jamais les paramètres JSON internes. Une modification reste une proposition : elle met à jour l’aperçu, puis doit être confirmée avant son enregistrement. Le même contenu est utilisé pour les aperçus ordinateur, tablette et mobile ; seule la mise en page responsive change.

## Sécuriser l’application des propositions

Pour exiger une clé avant d’enregistrer une proposition, ajoutez cette variable à `backend/.env` :

```env
ADMIN_API_KEY=une-cle-secrete
```

L’appel qui applique une proposition doit alors inclure l’en-tête suivant :

```http
X-API-KEY: une-cle-secrete
```

Sans `ADMIN_API_KEY`, l’application des propositions est autorisée sans clé : ce mode est réservé au développement.

## Scripts utiles

```powershell
# Frontend
cd frontend
npm run dev       # serveur de développement
npm run build     # vérification TypeScript et build de production
npm run preview   # aperçu du build

# Backend
cd backend
pytest            # tests backend
```

## Structure du projet

```text
backend/
  app/
    routes/       # API campagnes, génération, chat, export et upload
    services/     # IA, assemblage HTML et validation
    skills/       # compétences de l’éditeur conversationnel
  templates/      # template de landing page
frontend/
  src/
    components/   # assistant, aperçu, export et wizard
    pages/        # création, aperçu et historique
templates/        # template HTML utilisé en priorité par le backend
```

## Dépannage

- **L’IA ne répond pas** : vérifiez que le service Ollama est actif et que le modèle défini par `OLLAMA_MODEL` est installé.
- **Le chat d’édition échoue** : vérifiez `OPENAI_API_KEY` et redémarrez le backend après toute modification de `.env`.
- **Le frontend ne peut pas appeler l’API** : vérifiez que le backend écoute sur le port `8000` et que `CORS_ORIGINS` contient l’URL du frontend.
