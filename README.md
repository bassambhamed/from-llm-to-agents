<div align="center">

<img src="from-llm-to-agents.png" alt="From LLMs to Agents — bootcamp banner" width="100%"/>

# From LLMs to Agents

**Bootcamp intensif de 3 jours · LLMs → Prompt Engineering → RAG → Agents IA**

[![Language](https://img.shields.io/badge/lang-fran%C3%A7ais-blue)](#)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![LLM](https://img.shields.io/badge/LLM-Groq%20%C2%B7%20llama--3.3--70b-FF6B35)](https://console.groq.com)
[![Frameworks](https://img.shields.io/badge/frameworks-LangChain%20%C2%B7%20LangGraph%20%C2%B7%20n8n-2C8EBB)](#)
[![Modules](https://img.shields.io/badge/modules-4-success)](#contenu-du-bootcamp)
[![Format](https://img.shields.io/badge/format-Jupyter%20%C2%B7%20FastAPI%20%C2%B7%20Streamlit%20%C2%B7%20Docker-orange)](#stack-technique)

*Auteur : **[Bassem Ben Hamed](#auteur)** · Université de Sfax · Digital Innovation Partner · DataCamp*

</div>

---

> Bootcamp opérationnel pour profils techniques (data engineers, data scientists, devs IA) couvrant les fondamentaux des LLMs jusqu'à la mise en production d'**agents IA autonomes** : ReAct en Python avec LangChain, workflows contrôlés avec LangGraph, et automatisation no-code avec n8n.
>
> *Aujourd'hui : on appelle un LLM. Demain : on prompte mieux. Après-demain : on l'ancre sur des données. Au final : on l'orchestre dans un agent.*

## Table des matières

- [From LLMs to Agents](#from-llms-to-agents)
  - [Table des matières](#table-des-matières)
  - [À qui s'adresse ce bootcamp](#à-qui-sadresse-ce-bootcamp)
    - [Progression pédagogique](#progression-pédagogique)
  - [Ce que vous allez construire](#ce-que-vous-allez-construire)
  - [Quick start](#quick-start)
    - [Lancer l'app de référence (TP 3)](#lancer-lapp-de-référence-tp-3)
  - [Contenu du bootcamp](#contenu-du-bootcamp)
    - [Jour 1 — Fondamentaux LLM + Prompt Engineering](#jour-1--fondamentaux-llm--prompt-engineering)
      - [Cours](#cours)
      - [TP 1 — Fondamentaux LLM (3 h)](#tp-1--fondamentaux-llm-3-h)
      - [Cours](#cours-1)
      - [TP 2 — Prompt Engineering (3 h)](#tp-2--prompt-engineering-3-h)
    - [Jour 2 — RAG](#jour-2--rag)
      - [Cours](#cours-2)
      - [TP 3 — Pipeline RAG complet (3 h)](#tp-3--pipeline-rag-complet-3-h)
      - [App de référence — `03 RAG/rag-app/`](#app-de-référence--03-ragrag-app)
    - [Jour 3 — Agents IA](#jour-3--agents-ia)
      - [Cours](#cours-3)
      - [TP 4 — Deux use cases × deux implémentations (3 h)](#tp-4--deux-use-cases--deux-implémentations-3-h)
  - [Structure du dépôt](#structure-du-dépôt)
  - [Stack technique](#stack-technique)
  - [Livrables par participant](#livrables-par-participant)
  - [Sécurité \& gouvernance](#sécurité--gouvernance)
  - [Liens entre modules](#liens-entre-modules)
  - [Auteur](#auteur)
  - [Licence](#licence)

---

## À qui s'adresse ce bootcamp

|  |  |
|---|---|
| **Cible** | Data engineers, data scientists, développeurs IA, profils techniques découvrant les LLMs |
| **Durée** | 3 jours intensifs · 6 h / jour · **18 h** au total |
| **Format** | Exposés + démonstrations + **4 TPs hands-on** (~ 60 % du temps en pratique) |
| **Effectif** | 8 à 12 participants |
| **Langue** | Français (code identifiers en anglais) |
| **Pré-requis** | Python de base · notion d'API REST · **aucune** connaissance préalable en ML / NLP |
| **Matériel** | Python 3.10+ (recommandé : conda env `gai` avec Python 3.11 — voir [`setup.md`](setup.md)) · Jupyter · clé API **Groq gratuite** ([console.groq.com](https://console.groq.com)) · Docker Desktop pour TP 4.b |

### Progression pédagogique

```
LLMs ──▶ Prompt Engineering ──▶ RAG ──▶ Agents IA (LangChain + LangGraph + n8n)
 J1            J1                J2          J3
```

Chaque module **capitalise** sur le précédent — l'agent du Jour 3 réutilise le retriever du Jour 2, les prompts du Jour 1 après-midi et les patterns ReAct du Jour 1 matin.

---

## Ce que vous allez construire

| Jour | Livrable concret | Stack |
|---|---|---|
| **J1** | Comparaison de **3 LLMs locaux** + Groq sur 6 cas d'usage (résumé, classification de tickets, traduction, extraction JSON, SQL, reformulation) | HuggingFace Transformers, Groq |
| **J1** | Bibliothèque de **prompts versionnés** + démo de masquage de secrets | LangChain `PromptTemplate` |
| **J2** | **Pipeline RAG complet** (Basic + Advanced + Eval) + une **app de référence FastAPI + Streamlit** avec 6 pages dashboard | ChromaDB, RAGas, LangSmith, FastAPI, Streamlit |
| **J3** | **2 agents IA** (recherche IA + briefing matinal Gmail/Drive/Calendar) en **code** *et* en **no-code** | LangChain, LangGraph, n8n, Google APIs |

---

## Quick start

> Pour la procédure complète (Git, Anaconda, kernel Jupyter, dépannage), voir **[`setup.md`](setup.md)**.

```bash
# 1. Cloner le dépôt
git clone https://github.com/bassambhamed/from-llm-to-agent.git
cd from-llm-to-agent

# 2. Créer l'environnement conda et installer les dépendances (root requirements.txt)
conda create -n gai python=3.11 -y
conda activate gai
pip install -r requirements.txt

# 3. Renseigner ses clés API dans .env (à la racine, fichier déjà fourni)
#    GROQ_API_KEY=gsk_...           ← obligatoire (https://console.groq.com)
#    TAVILY_API_KEY=...             ← TP 4-a Research Assistant
#    GOOGLE_CLIENT_ID=... etc.      ← TP 4-a Morning Briefing
# Le .env est chargé automatiquement par python-dotenv dans chaque notebook.

# 4. Lancer le premier notebook
jupyter notebook "01 Fondamentaux LLM/TP/tp1-llm-fondamentaux.ipynb"
```

> ⚠️ **Sécurité** — Ne jamais coller une clé API dans une cellule de code. Toujours via `os.environ.get()` après `load_dotenv()`. Le `.env` doit rester git-ignoré dès qu'il contient de vraies clés. Le TP 2 contient une démo de **masquage de secrets** (`sk-...`, `gsk_...`, `hf_...`, JWT).

### Lancer l'app de référence (TP 3)

```bash
cd "03 RAG/rag-app"
# La GROQ_API_KEY est lue depuis rag-app/.env (chargé par python-dotenv)
# Éditer ce fichier au besoin :
#   GROQ_API_KEY=gsk_...

python api.py                  # Terminal 1 — backend FastAPI sur :8000
streamlit run dashboard.py     # Terminal 2 — UI Streamlit sur :8501
```

---

## Contenu du bootcamp

### Jour 1 — Fondamentaux LLM + Prompt Engineering

<details>
<summary><b>🎓 Module 1 — Fondamentaux LLM</b> · 3 h cours + 3 h TP</summary>

#### Cours

**§ 1.1 — Introduction à l'IA générative** (1 h) — Panorama IA / ML / DL / NLP / LLM, types d'apprentissage, IA discriminative vs générative, multimodal, métriques (BLEU / ROUGE / perplexité), écosystème LLM 2026 (GPT-4o, Claude 4.x, Gemini 2.x, Llama 3.x, Mistral, Phi-4) et critères de choix (coût, latence, contexte, conformité).

**§ 1.2 — Le Transformer pas à pas** (2 h) — Fil rouge *« je suis étudiant » → « I am a student »*. **7 étapes détaillées** : embeddings de tokens · encodage positionnel · self-attention scaled dot-product · multi-head attention · FFN + Add & Norm · masked self-attention décodeur · cross-attention. Plus prédiction token-par-token, températures, top-k/top-p, fenêtre de contexte.

#### TP 1 — Fondamentaux LLM (3 h)

3 modèles locaux (`SmolLM2-135M`, `Qwen2.5-0.5B`, `Qwen2.5-1.5B`) + `llama-3.3-70b-versatile` via Groq · tokenisation comparative · embeddings (PCA, similarité, arithmétique vectorielle) · stratégies de décodage · **6 cas d'usage** : résumé, classification de tickets plateforme IA, traduction technique, extraction JSON, génération SQL sur schema MLOps, reformulation.

</details>

<details>
<summary><b>🎓 Module 2 — Prompt Engineering</b> · 1 h 30 cours + 3 h TP</summary>

#### Cours

Anatomie d'un prompt (4 éléments) · Zero/Few-Shot · CoT · Self-Consistency · Role Prompting · balises XML · Generated Knowledge · Prompt Chaining · Tree of Thoughts · Directional Stimulus · ReAct · Indice de confiance · Active-Prompt.

#### TP 2 — Prompt Engineering (3 h)

10 parties · 12 techniques en hands-on · 5 applications production-ready · sécurité (prompt injection, masquage de secrets `sk-...` / `gsk_...` / `hf_...` / JWT) · bibliothèque de prompts versionnée (`PromptTemplate`).

</details>

### Jour 2 — RAG

<details open>
<summary><b>🎓 Module 3 — RAG : Basic + Advanced + Évaluation (+ Graph bonus)</b> · 3 h cours + 3 h TP</summary>

#### Cours

**§ 3.1 — Principes & Basic RAG** (1 h) — LangChain loaders catalog · chunking + Contextual Retrieval (Anthropic 2024) · Bi-encoder + MTEB · vector stores HNSW vs IVF · retrieval hybride BM25 + dense + RRF · reranking Cross-encoder vs Bi-encoder.

**§ 3.2 — Advanced RAG, Évaluation & Observabilité** (1 h 30) — Lost in the Middle · Query Rewriting · Multi-Query · HyDE · récap coût/gain · **RAGas** (4 métriques + LLM-as-a-judge) · TruLens / DeepEval / Phoenix · **LangSmith** · *(bonus)* **Graph RAG** : extraction entités/relations, communautés, retrieval local/global.

**§ 3.3 — Pont vers Module 4** (30 min) — Comparaison & **Agentic RAG** : decision tree, hybride, anatomie agent, ReAct, 6 design patterns, Adaptive RAG.

#### TP 3 — Pipeline RAG complet (3 h)

Notebook **97 cellules**, 4 parties :

- **Partie A — Basic RAG** (1 h 15) : 8 étapes — loaders LangChain (Markdown + démos exécutées **PDF arXiv** et **Web**) · chunking récursif → length-based (`TokenTextSplitter`, `SentenceTransformersTokenTextSplitter`, démo *Tokenizer Mismatch*) → structure-aware → Contextual Retrieval → **Chonkie Semantic + Agentic** (`SlumberChunker` sur Groq) · embeddings MiniLM + similarité cosine/dot/L2 + choix du modèle (BGE-M3, Jina v2…) + **multimodal** (théorique) · vector store Chroma + **démo FAISS `IndexFlatL2`** · retrieval hybride BM25 + RRF · reranker Cross-encoder · prompt augmenté · génération via LangChain **+ variante Python pur (SDK Groq direct)**.
- **Partie B — Advanced RAG** (45 min) : Lost-in-the-middle reorder + Query Rewriting + Multi-Query + HyDE.
- **Partie C — Évaluation & Observabilité** (30 min) : RAGas avec LLM-juge Llama 3.3 + cellule LangSmith.
- **Partie D — Graph RAG (bonus)** (30 min) : extraction entités/relations + graphe NetworkX + retrieval local/global.

#### App de référence — `03 RAG/rag-app/`

FastAPI + Streamlit, **6 pages dashboard** :

| Page | Fonctionnalité |
|---|---|
| 💬 Chat | Menus déroulants pour chaque technique Advanced RAG |
| 🧪 Comparateur | Side-by-side de 2-3 techniques sur la même question |
| 🕸️ Graph RAG | Mode dédié, retrieval local/global |
| 📊 Embeddings | Projection PCA 2D / 3D |
| 🌐 Knowledge Graph | Graphe interactif (NetworkX) |
| 📈 Évaluation | Hit@5 / MRR sur golden set |

</details>

### Jour 3 — Agents IA

<details open>
<summary><b>🎓 Module 4 — Agents IA : LangChain → LangGraph → n8n</b> · 3 h cours + 3 h TP</summary>

#### Cours

**§ 4.1 — Anatomie & patterns d'un Agent IA** (1 h 30) — Brain (LLM) / Memory / Tools / Reasoning Loop · **Agent vs Agentic Workflow** · ReAct pattern · **6 Agentic Design Patterns** (Anthropic 2024) :

| # | Pattern | Idée |
|---|---|---|
| 1 | Prompt chaining | sortie d'un LLM → entrée du suivant |
| 2 | Parallélisation | multi-source en parallèle, agrégation |
| 3 | Routing | classifier puis dispatcher vers une branche |
| 4 | Reflection loop | auto-évaluation + retry contrôlé |
| 5 | Orchestrator-workers | un orchestrateur délègue à N workers |
| 6 | Tool use | le LLM choisit et appelle des outils externes |

**§ 4.2 — Adaptive RAG & frameworks** (1 h 30) — Self-RAG (Asai 2023) · CRAG (Yan 2024) · Adaptive RAG (Jeong 2024). Frameworks : **LangChain** (`Tool`, retriever wrapping), **LangGraph** (`StateGraph`, edges conditionnels, `create_react_agent` prebuilt), **n8n** (AI Agent node, Tools Agent, no-code). Gouvernance, sécurité, *write tools en draft only*.

#### TP 4 — Deux use cases × deux implémentations (3 h)

|  | **Use case 1 — AI Research Assistant** | **Use case 2 — Briefing matinal** |
|---|---|---|
| **Outils** | 3 (RAG TP3, Tavily web, arXiv) | 8 (Gmail, Calendar, Drive, Slack…) |
| **Lecture / Écriture** | lecture seule | **lecture + écriture** (drafts Gmail) |
| **Code Python** | `tp4a-agent-research-assistant.ipynb` | `tp4a-agent-morning-briefing.ipynb` |
| **No-code n8n** | `tp4b-n8n-research-assistant.md` | `tp4b-n8n-morning-briefing.md` |
| **Difficulté** | ★★ | ★★★ (OAuth Google + idempotence) |

Voir [`04 Agents IA/README.md`](04%20Agents%20IA/README.md) pour le détail des 2 notebooks et 2 runbooks. Stack Docker n8n + Postgres + Qdrant **mutualisée** entre les 2 runbooks.

</details>

---

## Structure du dépôt

```
from-llm-to-agent/
├── README.md                                        ← ce fichier
├── setup.md                                         ← procédure d'installation détaillée (Git, conda gai, kernel, dépannage)
├── requirements.txt                                 ← dépendances unifiées de tout le bootcamp
├── .env                                             ← clés API centralisées (chargées par python-dotenv)
├── from-llm-to-agents.png                           ← image hero
│
├── 01 Fondamentaux LLM/                             ← Jour 1 matin
│   ├── slides/fondamentaux-llm.pdf           (33 pages, Transformer pas-à-pas)
│   └── TP/tp1-llm-fondamentaux.ipynb                (7 parties, ~85 cellules)
│
├── 02 Prompt Engineering/                           ← Jour 1 après-midi
│   ├── slides/prompt-engineering.pdf         (44 pages)
│   └── TP/tp2-prompt-engineering.ipynb              (10 parties, ~54 cellules)
│
├── 03 RAG/                                          ← Jour 2
│   ├── README.md                                    ← overview du module 3
│   ├── slides/rag.pdf                         (66 pages)
│   ├── TP/tp3-rag-pipeline-complet.ipynb            (97 cellules, 4 parties)
│   └── rag-app/                                     ← app de référence FastAPI + Streamlit
│       ├── README.md · .env · requirements.txt
│       ├── api.py · dashboard.py · rag_engine.py
│       └── sample_data/
│
└── 04 Agents IA/                                    ← Jour 3
    ├── slides/agents.pdf                            (~ 50 pages)
    ├── README.md                                    ← overview du module
    ├── TP4-a/                                       ← notebooks Python
    │   ├── README.md
    │   ├── tp4a-agent-research-assistant.ipynb      (29 cellules, LangChain + LangGraph)
    │   └── tp4a-agent-morning-briefing.ipynb        (48 cellules, Gmail+Drive+Calendar)
    └── TP4-b/                                       ← runbooks no-code n8n
        ├── tp4b-n8n-research-assistant.md           (stack Docker + recherche IA)
        └── tp4b-n8n-morning-briefing.md             (cron 8h30 + OAuth Web)
```

---

## Stack technique

| Couche | Outil | Pourquoi |
|---|---|---|
| **LLM cloud** | **Groq** + `llama-3.3-70b-versatile` | API gratuite, OpenAI-compatible, inférence ultra-rapide (LPUs) |
| **LLM locaux (TP 1)** | `SmolLM2-135M`, `Qwen2.5-0.5B`, `Qwen2.5-1.5B` | Démo tokenisation et stratégies de décodage sans GPU |
| **Embeddings** | `sentence-transformers/all-MiniLM-L6-v2` · `multilingual-MiniLM` · option `bge-m3` · multimodal (théorie : CLIP, Qwen2-VL) | Compromis qualité/vitesse, 384 dims |
| **Chunking avancé (TP 3)** | `chonkie` (`SemanticChunker`, `SlumberChunker` + `GroqGenie` agentique) | Coupe sémantique et **agentique** au-delà du splitter récursif |
| **Vector store (notebooks)** | **ChromaDB** + démo **FAISS** (`IndexFlatL2`) | HNSW cosine in-memory, zéro setup ; FAISS pour comparaison exacte |
| **Vector store (n8n)** | **Qdrant** | Persistance Docker, API REST, intégration n8n native |
| **Sparse retrieval** | `rank-bm25` | Lexical, pour hybride avec dense |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Réordonne top-k retrieval |
| **Évaluation RAG** | **RAGas** | Faithfulness, Answer Relevancy, Context Precision/Recall |
| **Observabilité** | **LangSmith** | Cellule optionnelle dans chaque TP |
| **Graph RAG (bonus)** | **NetworkX** | Communautés Louvain, viz interactive |
| **Frameworks Agents** | **LangChain** + **LangGraph** + **n8n** | Code → workflow contrôlé → no-code |
| **Outils Agent (TP 4)** | retriever Chroma · Tavily · arXiv · Gmail · Calendar · Drive · Slack | Spectre académique → opérationnel |
| **App de référence (TP 3)** | FastAPI + Streamlit | Pattern réutilisable pour tout RAG en prod |
| **Configuration** | `python-dotenv` + `.env` (racine et `rag-app/`) | Clés API centralisées, chargement automatique |

---

## Livrables par participant

| TP | Livrable |
|---|---|
| **TP 1** | Notebook exécuté + comparaison 3 modèles locaux + Groq sur 6 cas d'usage |
| **TP 2** | Notebook exécuté + bibliothèque de **3 prompts versionnés** (`PromptTemplate`) |
| **TP 3** | Notebook exécuté (parties A + B + C minimum) + résultats **RAGas** sur leur corpus + 1 technique Advanced testée + mini rapport |
| **TP 4.a** | 2 notebooks exécutés + traces ReAct + traces LangGraph + tableaux comparatifs |
| **TP 4.b** | Stack Docker active + 2 workflows n8n importés et testés + comparaison code vs no-code |

---

## Sécurité & gouvernance

| Règle | Pourquoi | Mise en œuvre |
|---|---|---|
| Aucune clé API dans une cellule | Risque de fuite si commit | `os.environ.get()` + `.env` git-ignoré |
| Compte Google **dédié bootcamp** (TP 4) | Le notebook crée des drafts Gmail réels | Compte créé pour l'occasion, supprimable |
| `credentials.json` / `token.json` jamais commit | Équivalents à un mot de passe | `.gitignore` du dossier de travail |
| *Write tools* en **draft only** | Coût d'un envoi mal classé > coût d'un draft à valider | `gmail_create_draft` jamais `send` |
| Sandbox Docker pour n8n | Isolation des credentials Google | Docker Compose dédié, ports locaux |
| Démo masquage de secrets (TP 2) | Sensibiliser dès le début | Détection regex `sk-...`, `gsk_...`, `hf_...`, JWT |

En cas de compromission d'un credential Google : **Google Cloud Console → Credentials → supprimer le client OAuth** (révoque tous les tokens dérivés).

---

## Liens entre modules

| Brique du Jour 3 | Source |
|---|---|
| System prompt de l'agent (rôle, garde-fous, résistance injection) | **Module 2** — patterns ReAct, auto-critique, indice de confiance |
| Outil `retriever.as_tool()` (Chroma) | **Module 3** — pipeline RAG repackagé comme outil d'agent |
| Paramètres de génération (`temperature`, `top-p`) | **Module 1** — API LLM, stratégies de décodage |
| Adaptive workflow (grade docs / grade answer / grade briefing) | **Module 3** — RAGas + auto-critique du Module 2 |

---

## Auteur

**Bassem Ben Hamed**

- Professeur des Universités — *Université de Sfax*
- Tech Lead — *Digital Innovation Partner*
- Data Scientist — *DataCamp Training & Consulting*

📧 bassem.benhamed@enetcom.usf.tn

---

## Licence

Matériel pédagogique © **Bassem Ben Hamed**. Tous droits réservés.

L'utilisation, la reproduction et la diffusion sont soumises à autorisation préalable. Pour toute demande d'usage en formation, en entreprise ou en milieu académique, contacter l'auteur.

---

<div align="center">

**Made with care for the next generation of AI engineers.**

</div>
