# TP 3 — Application RAG (Basic + Advanced + Graph bonus)

Application full-stack de démonstration du **TP 3** de la formation. Implémente :

- **Basic RAG** : ingestion (LangChain loaders) → chunking (`RecursiveCharacterTextSplitter`) → embeddings (`all-MiniLM-L6-v2`) → indexation (Chroma + BM25) → retrieval hybride (RRF) → reranking cross-encoder → génération.
- **Advanced RAG** : Query Rewriting, Multi-Query (RRF de N reformulations), HyDE (*Hypothetical Document Embeddings*), Lost-in-the-middle reorder.
- **Graph RAG** *(bonus)* : extraction d'entités/relations, graphe NetworkX, détection de communautés, retrieval local + global.

## Architecture

```
┌─────────────────┐         ┌─────────────────────┐
│  UI Streamlit   │◄──────► │  Backend FastAPI    │
│  (port 8501)    │  HTTP   │   (port 8000)       │
│                 │         │                     │
│ • Chat          │         │  • /query           │
│ • Comparateur   │         │  • /preview/*       │
│ • Graph RAG     │         │  • /query/graph     │
│ • Embeddings    │         │  • /embeddings      │
│ • Graphe        │         │  • /graph           │
│ • Évaluation    │         │  • /evaluate        │
└─────────────────┘         └──────────┬──────────┘
                                       │
                            ┌──────────▼──────────┐
                            │    RAGEngine        │
                            │                     │
                            │ • LangChain loaders │
                            │ • LangChain         │
                            │   splitters         │
                            │ • SentenceTransf.   │
                            │ • ChromaDB (HNSW)   │
                            │ • BM25 + RRF        │
                            │ • CrossEncoder      │
                            │ • NetworkX graph    │
                            │ • Groq (LLM)        │
                            └─────────────────────┘
```

## Fonctionnalités

| Page | Description |
|---|---|
| **💬 Chat** | Pipeline complet avec menus déroulants : retrieval (dense/sparse/hybrid), technique avancée (Aucune / Query Rewriting / Multi-Query / HyDE), reranking, lost-in-the-middle reorder. Affiche les étapes intermédiaires. |
| **🧪 Comparateur de techniques** | Lance la même question avec plusieurs configurations en parallèle, affiche réponses + sources + variantes/réponse hypothétique côte à côte. |
| **🕸️ Graph RAG** | Mode dédié : retrieval local (entités ancrées) + global (résumés de communautés) + chunks vectoriels. |
| **📊 Embeddings** | Projection PCA 2D et 3D, exploration interactive (Plotly). |
| **🌐 Knowledge Graph** | Visualisation interactive du graphe (entités, relations, communautés, top entités). |
| **📈 Évaluation** | Hit Rate @5 et MRR @5 sur le golden set, comparaison Dense / Sparse / Hybrid. |

## Pré-requis

- **Python 3.10+**
- **Clé API Groq** (gratuite, 30 secondes) :
  1. Aller sur **https://console.groq.com**
  2. Se connecter (Google / GitHub) — pas de carte bancaire
  3. *API Keys → Create API Key* — copier la clé `gsk_...`
  4. Exporter :
     ```bash
     export GROQ_API_KEY="gsk_..."
     ```

## Installation

```bash
cd "03 RAG/rag-app"
pip install -r requirements.txt

# Téléchargement one-shot des modèles HuggingFace (puis utilisable hors-ligne)
python -c "from sentence_transformers import SentenceTransformer, CrossEncoder; \
  SentenceTransformer('all-MiniLM-L6-v2'); \
  CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')"
```

## Lancement

Ouvrir **deux terminaux** depuis ce dossier (avec `GROQ_API_KEY` exportée dans les deux) :

**Terminal 1 — backend FastAPI :**
```bash
export GROQ_API_KEY="gsk_..."
python api.py            # ou : uvicorn api:app --reload --port 8000
```

**Terminal 2 — dashboard Streamlit :**
```bash
streamlit run dashboard.py
```

L'API tourne sur `http://localhost:8000` (indexation automatique au démarrage).
Le dashboard ouvre sur `http://localhost:8501`.

## Endpoints de l'API

| Méthode | Endpoint | Description |
|---|---|---|
| `GET`  | `/`                       | Health check |
| `POST` | `/ingest`                 | Ré-indexe `sample_data/` |
| `POST` | `/query`                  | RAG complet avec toggles Advanced (rewriting, multi-query, hyde, lim_reorder, reranking) |
| `POST` | `/preview/rewrite`        | Aperçu de la requête réécrite |
| `POST` | `/preview/multi-query`    | Aperçu des N reformulations |
| `POST` | `/preview/hyde`           | Aperçu de la réponse hypothétique |
| `POST` | `/query/graph`            | Graph RAG (graphe + retrieval vectoriel) |
| `GET`  | `/embeddings`             | PCA 2D des embeddings |
| `GET`  | `/embeddings/3d`          | PCA 3D des embeddings |
| `GET`  | `/graph`                  | Données du knowledge graph |
| `GET`  | `/stats`                  | Stats système (modèles, état, dispo API) |
| `GET`  | `/evaluate`               | Hit Rate / MRR sur le golden set |

### Exemple — appel `/query` avec Advanced RAG

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Comment fonctionne HNSW ?",
    "method": "hybrid",
    "top_k": 8,
    "rerank_top_k": 3,
    "use_reranking": true,
    "use_query_rewriting": false,
    "use_multi_query": true,
    "use_hyde": false,
    "use_lim_reorder": true
  }'
```

La réponse contient `answer`, `sources`, `effective_query`, `method_used`, et un objet `steps` avec les étapes intermédiaires (variantes générées, réponse hypothétique, etc.).

## Modèles utilisés

| Composant | Modèle | Notes |
|---|---|---|
| Embeddings | `all-MiniLM-L6-v2` (384 dim) | Open-source, local |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Open-source, local |
| **LLM** | **`llama-3.3-70b-versatile`** via **Groq** | Gratuit (free tier), ultra-rapide (LPU) |

## Corpus d'exemple

Le dossier `sample_data/` contient des documents pour la démo :
- `transformers.md` — Transformer, self-attention, encodage positionnel
- `rag_systems.md` — pipeline RAG, chunking, retrieval hybride, évaluation
- `vector_databases.md` — HNSW, similarité, ChromaDB, FAISS
- `finetuning.md` — LoRA, QLoRA, RLHF, DPO
- *(optionnel)* tout PDF déposé dans `sample_data/` est ingéré via `PyPDFLoader`

## Positionnement pédagogique

L'application matérialise le **TP 3** :
- **Partie A — Basic RAG** → page *Chat (Aucune technique avancée)*, *Embeddings*, *Évaluation*.
- **Partie B — Advanced RAG** → page *Chat (techniques avancées)*, *Comparateur*.
- **Partie C — Évaluation** → page *Évaluation*.
- **Partie D — Graph RAG (bonus)** → page *Graph RAG*, *Knowledge Graph*.

Le **Jour 3** réutilisera les endpoints comme **outils** appelés par un **agent ReAct (LangChain)**, puis un **workflow Adaptive RAG (LangGraph)**, puis un **agent no-code (n8n)**.
