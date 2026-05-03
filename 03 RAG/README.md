# Module 03 — RAG : Basic + Advanced + Évaluation (+ Graph bonus)

**Jour 2 · 3 h (cours) + 3 h (TP 3)**

Troisième module de la formation *IA générative · LLMs · Prompt Engineering · RAG · Agents IA & Automatisation*. Il répond à la question opérationnelle la plus fréquente après les Modules 01 et 02 : **comment ancrer un LLM sur des données externes** (documentation technique, base de connaissances, référentiels, papiers scientifiques) **sans ré-entraîner le modèle** ?

Le module couvre **un pipeline RAG complet** — de l'ingestion à la génération sourcée — puis les **techniques avancées** (Query Rewriting, Multi-Query, HyDE, Lost-in-the-middle, Contextual Retrieval), l'**évaluation rigoureuse** (RAGas + LLM-as-a-judge), l'**observabilité** (LangSmith), et en bonus une approche **Graph RAG** sur le même corpus pour comparaison.

---

## Public & prérequis

- **Cible** : ingénieurs DATA (BI, Data Engineering, Opérations), data scientists, développeurs IA.
- **Prérequis** :
  - **Module 01 validé** — manipulation d'un LLM via API, notion d'embeddings.
  - **Module 02 validé** — rédaction de prompts structurés (le *prompt d'augmentation* est central en RAG).
  - Notions Python, manipulation de documents (Markdown, PDF, Web).
- **Matériel** :
  - Python 3.10+ avec Jupyter.
  - **Clé API Groq** (gratuite, free tier) — création en 30 secondes sur **https://console.groq.com**.
  - ~2 Go d'espace disque pour les modèles d'embeddings et de reranking (téléchargés une fois, puis hors-ligne).

---

## Objectifs pédagogiques

À l'issue du module, le participant est capable de :

1. **Expliquer** pourquoi le RAG réduit les hallucinations, garantit la fraîcheur et permet la traçabilité des sources.
2. **Concevoir** un pipeline **Basic RAG** complet : loading (LangChain loaders) → chunking (LangChain splitters) → embeddings (Bi-encoder) → indexation (Chroma + BM25) → retrieval hybride (RRF) → reranking (Cross-encoder) → génération.
3. **Mettre en œuvre les techniques d'Advanced RAG** pour passer du prototype à un outil robuste : Query Rewriting, Multi-Query, HyDE, Lost-in-the-middle reorder, Contextual Retrieval.
4. **Évaluer** un pipeline avec **RAGas** (Faithfulness, Answer Relevancy, Context Precision/Recall) et le concept de **LLM-as-a-judge** ; **tracer** les exécutions avec **LangSmith**.
5. *(Bonus)* **Comprendre** la valeur ajoutée du **Graph RAG** pour les questions multi-hop et relationnelles, et **choisir** entre Basic / Advanced / Graph / Hybride selon le type de question.

---

## Contenu

### Cours — 3 h (slides : `slides/rag.pdf`)

Le support couvre **7 parties** :

| # | Partie | Contenu clé |
|---|---|---|
| 1 | **Principes & Basic RAG** | RAG vs fine-tuning vs long-context, LangChain loaders, chunking + Contextual Retrieval, Bi-encoder + MTEB, Vector stores HNSW vs IVF, retrieval hybride BM25 + RRF, reranking Cross-encoder vs Bi-encoder |
| 2 | **Vector RAG en détail** | Pipeline détaillé, forces, limites, cas d'échec |
| 3 | **Advanced RAG** | Lost in the Middle, Query Rewriting, Multi-Query, HyDE, récap coût/gain |
| 4 | **Évaluation & Observabilité** | RAGas (4 métriques + formules), LLM-as-a-judge, LangSmith |
| 5 | **Graph RAG** *(bonus)* | Motivation, extraction entités/relations, communautés, retrieval local/global |
| 6 | **Comparaison & Agentic RAG** | Vector vs Graph, anatomie d'un Agent IA, ReAct, 6 design patterns, Adaptive RAG |
| 7 | **Préparation TP 3** | Brief, structure 3h, livrables, critères d'évaluation |

### TP 3 — Pipeline RAG complet (3 h)

Notebook : **`TP/tp3-rag-pipeline-complet.ipynb`** *(97 cellules, 4 parties)*

| Temps | Partie | Contenu détaillé |
|---|---|---|
| **1 h 15** | **A — Basic RAG (8 étapes)** | **§1** Loaders LangChain : Markdown + démos exécutées **PDF arXiv** (`PyPDFLoader`) et **Web** (`WebBaseLoader`) · **§2** Chunking : récursif → length-based (`TokenTextSplitter`, `SentenceTransformersTokenTextSplitter`) → démo *Tokenizer Mismatch* (tiktoken vs HF) → `MarkdownHeaderTextSplitter` → Contextual Retrieval → **Chonkie Semantic + Agentic (`SlumberChunker` sur Groq)** · **§3** Embeddings : MiniLM + similarité cosine/dot/L2 + tableau de choix du modèle (BGE-M3, Jina v2…) + **multimodal** (CLIP/Qwen2-VL, théorique) · **§4** Vector store : Chroma + **démo FAISS `IndexFlatL2`** · **§5** Retrieval hybride BM25 + RRF · **§6** Cross-encoder rerank · **§7** Prompt augmenté · **§8** Génération via LangChain **+ variante Python pur (SDK Groq direct)** |
| **45 min** | **B — Advanced RAG** | Lost-in-the-middle reorder + Query Rewriting + Multi-Query + HyDE, mesurés sur le golden set |
| **30 min** | **C — Évaluation & Observabilité** | RAGas (Faithfulness, Answer Relevancy, Context Precision/Recall) avec **LLM-juge Llama 3.3 70B via Groq** + cellule LangSmith (optionnelle) |
| **30 min** | **D — Graph RAG** *(bonus)* | Extraction entités/relations LLM + graphe NetworkX + retrieval local/global + comparaison Vector vs Graph |

Le TP est fourni à la fois comme **notebook pédagogique** (`TP/tp3-rag-pipeline-complet.ipynb`) et comme **application full-stack** de référence (`rag-app/` — API FastAPI + tableau de bord Streamlit avec menus déroulants pour chaque technique Advanced RAG).

---

## Stack technique

| Composant | Outil | Notes |
|---|---|---|
| Loaders | `langchain-community` (`PyPDFLoader`, `WebBaseLoader`, `TextLoader`) | Format `Document` standard |
| Splitters classiques | `langchain-text-splitters` (`RecursiveCharacterTextSplitter`, `TokenTextSplitter`, `SentenceTransformersTokenTextSplitter`, `MarkdownHeaderTextSplitter`) | Chunking caractère / token / structure-aware |
| Splitters avancés | **`chonkie`** (`SemanticChunker`, `SlumberChunker` + `GroqGenie`) | Sémantique et **agentique** (LLM décide les frontières) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384 dim) | Bi-encoder, local, gratuit |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder, local, gratuit |
| Vector store | **ChromaDB** (HNSW, in-memory) + **FAISS** (`IndexFlatL2`, démo) | Démarrage instantané |
| Sparse retrieval | `rank-bm25` | Fusion via RRF |
| **LLM** | **`llama-3.3-70b-versatile` via Groq** (LangChain et SDK direct) | Free tier, OpenAI-compatible, ultra-rapide (LPU) |
| Évaluation | `ragas` + `langchain-groq` | LLM-as-a-judge avec Llama 3.3 70B |
| Observabilité | `langsmith` | Traçage end-to-end (optionnel) |
| Graphe | `networkx` | Détection de communautés (Leiden / Louvain) |
| Tokenizers | `tiktoken` + `transformers` (HuggingFace `AutoTokenizer`) | Démo *Tokenizer Mismatch* |
| Configuration | `python-dotenv` | Chargement automatique du `.env` (rag-app) |

> **Pourquoi Groq ?** API **gratuite** (free tier généreux), **OpenAI-compatible** (pattern réutilisable avec OpenAI / Azure / Anthropic / Mistral), **ultra-rapide** (LPUs). Modèle utilisé : `llama-3.3-70b-versatile` (70B paramètres, excellent suivi d'instructions et JSON).

---

## Contenu du dossier

```
03 RAG/
├── README.md                          ← ce fichier
├── slides/
│   └── rag.pdf                        ← support de cours
├── TP/
│   ├── tp3-rag-pipeline-complet.ipynb ← notebook du TP 3 (4 parties + bonus)
│   └── sample_data/                   ← corpus de démo (Markdown)
│       ├── transformers.md
│       ├── rag_systems.md
│       ├── vector_databases.md
│       └── finetuning.md
└── rag-app/                           ← application de référence (démo + bac à sable)
    ├── README.md                      ← guide d'installation et d'usage détaillé
    ├── .env                           ← variables d'environnement (GROQ_API_KEY, modèles)
    ├── api.py                         ← backend FastAPI (endpoints /query, /preview/*, /graph)
    ├── dashboard.py                   ← UI Streamlit (Chat, Comparateur, Graph RAG, Embeddings, KG, Eval)
    ├── rag_engine.py                  ← moteur RAG (Basic + Advanced + Graph)
    ├── requirements.txt
    └── sample_data/                   ← même corpus que TP/sample_data/
```

---

## Lancement rapide

### Notebook TP 3

```bash
# 1. Créer une clé Groq gratuite : https://console.groq.com
export GROQ_API_KEY="gsk_..."

# 2. Installer les dépendances (cf. cellule pip install au début du notebook)
pip install langchain langchain-community langchain-text-splitters \
            chromadb faiss-cpu sentence-transformers rank_bm25 \
            chonkie groq \
            pypdf beautifulsoup4 requests \
            tiktoken transformers openai \
            ragas datasets \
            networkx matplotlib seaborn scikit-learn

# 3. Lancer Jupyter
jupyter notebook TP/tp3-rag-pipeline-complet.ipynb
```

### Application `rag-app`

```bash
cd rag-app/
pip install -r requirements.txt

# Renseigner GROQ_API_KEY dans rag-app/.env (créé automatiquement, à éditer)
#   GROQ_API_KEY=gsk_...
# Le fichier est chargé automatiquement par python-dotenv au démarrage.

# Terminal 1 — backend FastAPI
python api.py            # ou : uvicorn api:app --reload

# Terminal 2 — dashboard Streamlit
streamlit run dashboard.py
```

L'API tourne sur `http://localhost:8000` (indexation automatique au démarrage). Le dashboard s'ouvre sur `http://localhost:8501` avec **6 pages** : Chat (avec menus déroulants pour chaque technique Advanced RAG), Comparateur de techniques, Graph RAG, Embeddings, Knowledge Graph, Évaluation.

---

## Lien avec la suite (Jour 3)

Le pipeline RAG du TP 3 sert de **brique réutilisable** pour le **Module 04 — Agents IA** :

- **TP 4.a — LangChain ReAct (Python)** : un agent autonome qui utilise le **retriever** du TP 3 via `retriever.as_tool()`, plus une recherche web (**Tavily**) et un outil **arXiv**.
- **TP 4.b — LangGraph Adaptive RAG (Python)** : workflow contrôlé avec **grade docs → rewrite → grade answer → web fallback** (les patterns *Self-RAG* / *CRAG* / *Adaptive RAG*).
- **TP 4.c — n8n no-code** : le même cas d'usage avec le node **AI Agent** de n8n et les mêmes outils — pour comparer code vs no-code et illustrer les **6 agentic design patterns** (Prompt chaining, Parallélisation, Routing, Reflection, Orchestrator-workers, Tool use).

> *Aujourd'hui : RAG **statique**. Demain : RAG **piloté par un agent**.*
