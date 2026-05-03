# Setup — Formation "From LLM to Agent"

Ce document décrit pas-à-pas la mise en place de l'environnement de travail
pour les 4 TPs de la formation (TP1 → TP4). Toutes les commandes ont été
testées sur **macOS, Linux et Windows**.

---

## 1. Installation de Git

Git permet de cloner le dépôt et de versionner vos travaux.

### macOS
```bash
# Via Homebrew (recommandé)
brew install git

# Ou via les Command Line Tools Apple
xcode-select --install
```

### Linux (Debian / Ubuntu)
```bash
sudo apt update
sudo apt install -y git
```

### Windows
Télécharger l'installeur officiel :
👉 https://git-scm.com/download/win

Pendant l'installation, accepter les options par défaut (Git Bash inclus).

### Vérification
```bash
git --version
# git version 2.4x.x
```

### Cloner le dépôt
```bash
git clone <URL_DU_DEPOT> from-llm-to-agent
cd from-llm-to-agent
```

---

## 2. Installation d'Anaconda

Anaconda fournit Python + `conda` (gestionnaire d'environnements) +
les principales bibliothèques scientifiques.

### Téléchargement
👉 https://www.anaconda.com/download

Choisir l'installeur correspondant à votre OS (macOS / Linux / Windows)
et à votre architecture (Apple Silicon, Intel x64, etc.).

### Installation
- **macOS / Linux** : exécuter le `.pkg` (macOS) ou le script `.sh` :
  ```bash
  bash Anaconda3-2024.xx-MacOSX-arm64.sh
  ```
- **Windows** : exécuter le `.exe` et suivre l'assistant.
  ✔ Cocher *"Add Anaconda to PATH"* (ou utiliser **Anaconda Prompt**).

### Vérification
Ouvrir un nouveau terminal (ou *Anaconda Prompt* sur Windows) :
```bash
conda --version
# conda 24.x.x
python --version
# Python 3.1x.x
```

---

## 3. Création de l'environnement conda `gai`

> ⚠️ **Important** : on utilise un environnement **conda** (et **non** un
> environnement virtuel `venv`). Conda gère mieux les dépendances binaires
> (PyTorch, sentencepiece, faiss…) sur les 3 OS.

```bash
# Créer l'environnement (Python 3.11 conseillé pour LangChain + Torch)
conda create -n gai python=3.11 -y

# Activer l'environnement
conda activate gai
```

Le prompt doit afficher `(gai)` au début :
```
(gai) user@machine:~/from-llm-to-agent$
```

Pour désactiver plus tard : `conda deactivate`.
Pour supprimer l'environnement : `conda env remove -n gai`.

---

## 4. Installation des dépendances Python

Une fois l'environnement `gai` activé :

```bash
# Mettre pip à jour (recommandé)
pip install --upgrade pip

# Installer toutes les bibliothèques de la formation
pip install -r requirements.txt
```

L'installation prend **5 à 15 minutes** selon la connexion (PyTorch ≈ 800 MB).

### Enregistrer l'environnement comme kernel Jupyter
Pour que les notebooks `.ipynb` voient bien `gai` :
```bash
python -m ipykernel install --user --name gai --display-name "Python (gai)"
```

Au démarrage d'un notebook, sélectionner le kernel **"Python (gai)"**.

### Vérification
```bash
python -c "import torch, transformers, langchain, chromadb; print('OK')"
# OK
```

---

## 5. Configuration des clés API (`.env`)

Toutes les clés API sont centralisées dans un fichier `.env` à la racine du
dépôt. Elles sont chargées automatiquement par `python-dotenv` → `load_dotenv()`
au début de chaque notebook.

### 5.1 Vérifier la présence du fichier `.env`
Le fichier est déjà fourni à la racine du dépôt :
```
from-llm-to-agent/
├── .env                  ← clés API (NE PAS COMMITER)
├── requirements.txt
├── setup.md              ← ce fichier
└── ...
```

### 5.2 Contenu attendu de `.env`
```ini
# Groq (LLM gratuit — TP1, TP2, TP3, TP4)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google OAuth (Gmail / Calendar — TP4-a)
GOOGLE_CLIENT_ID=xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxxxxxxxxxxxxxxxxxxx
GOOGLE_CREDENTIALS_PATH=./credentials.json

# Slack Incoming Webhook (TP4-a)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/Txxxx/Bxxxx/xxxx

# Tavily (recherche web — TP4-a Research Assistant)
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxx

# Optionnels
# LANGSMITH_TRACING=true
# LANGSMITH_API_KEY=lsv2_xxxxxxxx
# LANGSMITH_PROJECT=from-llm-to-agent
# OPENAI_API_KEY=sk-xxxxxxxx
```

### 5.3 Sécurité
Le fichier `.env` **ne doit jamais être commité** dans Git.
Vérifier que `.gitignore` contient bien :
```gitignore
.env
apiKey.txt
credentials.json
token.json
__pycache__/
*.pyc
.DS_Store
```

### 5.4 Obtention des clés
| Service | URL | Usage |
|--------|-----|-------|
| **Groq** | https://console.groq.com | LLM gratuit (Llama 3.3 70B) — **obligatoire** |
| **Tavily** | https://tavily.com | Recherche web — TP4-a (1 000 req/mois gratuites) |
| **Google Cloud** | https://console.cloud.google.com/apis/credentials | OAuth Gmail/Calendar — TP4-a |
| **Slack** | https://api.slack.com/messaging/webhooks | Webhook entrant — TP4-a |
| **LangSmith** | https://smith.langchain.com | Observabilité (optionnel) |

---

## 6. Lancement des notebooks

### Option A — JupyterLab (recommandé)
```bash
conda activate gai
jupyter lab
```
Puis ouvrir un notebook (ex. `01 Fondamentaux LLM/TP/tp1-llm-fondamentaux.ipynb`)
et sélectionner le kernel **"Python (gai)"**.

### Option B — VS Code
- Installer l'extension *Python* + *Jupyter* de Microsoft.
- Ouvrir le dossier `from-llm-to-agent`.
- Ouvrir un notebook → en haut à droite, choisir le kernel **"Python (gai)"**.

---

## 7. Lancement de l'application RAG (TP3)

L'application Streamlit + FastAPI du TP3 se lance en deux terminaux :

```bash
# Terminal 1 — Backend FastAPI
conda activate gai
cd "03 RAG/rag-app"
uvicorn api:app --reload --port 8000

# Terminal 2 — Frontend Streamlit
conda activate gai
cd "03 RAG/rag-app"
streamlit run dashboard.py
```

---

## 8. Tableau récapitulatif des TPs

| TP | Notebook / Dossier | Clés requises |
|----|--------------------|---------------|
| TP1 | `01 Fondamentaux LLM/TP/tp1-llm-fondamentaux.ipynb` | `GROQ_API_KEY` |
| TP2 | `02 Prompt Engineering/TP/tp2-prompt-engineering.ipynb` | `GROQ_API_KEY` |
| TP3 | `03 RAG/TP/tp3-rag-pipeline-complet.ipynb` + `03 RAG/rag-app/` | `GROQ_API_KEY` |
| TP4-a | `04 Agents IA/TP4-a/tp4a-agent-morning-briefing.ipynb` | `GROQ_API_KEY`, `GOOGLE_*`, `SLACK_WEBHOOK_URL` |
| TP4-a bis | `04 Agents IA/TP4-a/tp4a-agent-research-assistant.ipynb` | `GROQ_API_KEY`, `TAVILY_API_KEY` |
| TP4-b | `04 Agents IA/TP4-b/` (Docker) | voir `tp4b-n8n-setup.md` |

---

## 9. Dépannage rapide

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: dotenv` | `pip install python-dotenv` (env `gai` activé) |
| Le notebook n'utilise pas `gai` | Sélectionner le kernel "Python (gai)" en haut à droite |
| `GROQ_API_KEY` vide dans le notebook | Vérifier que `.env` est à la racine et que `load_dotenv()` est appelé |
| `OSError: [E050] Can't find model` | Lié à spaCy — pas utilisé ici, peut être ignoré |
| Erreur PyTorch sur Apple Silicon | `pip install --upgrade torch` (wheel ARM64) |
| Conflit de versions | Recréer l'env : `conda env remove -n gai` puis reprendre §3 |

---

✅ **Vous êtes prêt** : ouvrez `01 Fondamentaux LLM/TP/tp1-llm-fondamentaux.ipynb`
et exécutez la première cellule.
