# TP 4.a — Agents IA : LangChain + LangGraph

Module 4 — **Jour 3** (~ 2 h 15 + 2 h 30 optionnel pour l'agent productivité).

Le TP 4.a est composé de **deux notebooks** qui se complètent :

| Notebook | Use case | Durée | Difficulté |
|---|---|---|---|
| **`tp4a-agent-research-assistant.ipynb`** | AI Research Assistant — 3 outils (RAG local, Tavily, arXiv) | 2 h 15 | ★★☆ |
| **`tp4a-agent-morning-briefing.ipynb`** | Briefing matinal — 8 outils Gmail + Calendar + Drive + Slack | 2 h 30 | ★★★ |

Les deux notebooks suivent la même progression pédagogique : **agent ReAct simple → workflow LangGraph contrôlé → comparaison**. Le second monte d'un cran en réalisme (OAuth, lecture **et** écriture, multi-services Google).

---

## Notebook 1 — `tp4a-agent-research-assistant.ipynb`

### Use case

Un agent qui répond à des questions de recherche IA en consultant **3 outils** :

1. **Retriever Chroma** local — corpus IA du TP 3 (Transformer, RAG, fine-tuning, vector DBs).
2. **Tavily Search** — recherche web LLM-friendly (free tier 1 000 req/mois).
3. **arXiv** — papiers scientifiques.

### Plan

| Partie | Sujet | Durée |
|---|---|---|
| 0 | Setup (Groq, dépendances, retriever) | 15 min |
| 1 | LangChain ReAct sur 5 questions du golden set | 50 min |
| 2 | Limites observées de ReAct | 15 min |
| 3 | LangGraph Adaptive RAG (6 nodes, edges conditionnels) | 60 min |
| 4 | Comparaison ReAct vs Adaptive RAG | 20 min |
| 5 | Synthèse & transition vers TP 4.b (n8n) | 5 min |

### Pré-requis

- **Python 3.10+** avec Jupyter.
- **Clé API Groq** (gratuite) — <https://console.groq.com> → variable `GROQ_API_KEY`.
- **Clé API Tavily** (gratuite, 1 000 req/mois) — <https://tavily.com> → variable `TAVILY_API_KEY`.
- TP 1, 2 et 3 conseillés (mais ce notebook est **autonome** — il reconstruit le retriever localement).

### Installation

```bash
export GROQ_API_KEY="gsk_..."
export TAVILY_API_KEY="tvly-..."

pip install langchain langchain-community langchain-groq langchain-huggingface
pip install langgraph
pip install tavily-python arxiv
pip install chromadb sentence-transformers tiktoken
```

### Lancement

```bash
jupyter notebook tp4a-agent-research-assistant.ipynb
```

Puis **Run All**. Le notebook fonctionne aussi sans clé Tavily : les cellules concernées affichent `[Tavily désactivé]` et le workflow Adaptive RAG saute la branche web fallback.

### Livrables attendus

- Notebook exécuté de bout en bout.
- 5 traces ReAct + 5 traces LangGraph commentées.
- Tableau comparatif (latence, outils, succès) sur le golden set.
- *(Optionnel)* Activation de LangSmith pour inspecter les traces.

---

## Notebook 2 — `tp4a-agent-morning-briefing.ipynb` *(plus réaliste)*

### Use case

> *"Tous les matins à 8 h 30, l'agent me produit un briefing : mes 3 prochaines réunions avec leur contexte (mails récents + docs Drive liés), mes mails urgents non lus avec un brouillon de réponse, et mes deadlines à risque cette semaine."*

Cas réaliste, multi-tools, **lecture + écriture** — il soulève les vraies questions opérationnelles : OAuth, idempotence, sandbox, gouvernance.

### Outils déclarés à l'agent (8)

| # | Outil | API | R/W |
|---|---|---|---|
| 1 | `calendar_list_events` | Google Calendar | R |
| 2 | `gmail_search` | Gmail | R |
| 3 | `gmail_get_thread` | Gmail | R |
| 4 | `gmail_create_draft` | Gmail | **W** (draft jamais send) |
| 5 | `drive_search` | Google Drive | R |
| 6 | `drive_read_file` | Google Drive | R |
| 7 | `rag_search_internal` | Vector store interne | R (stub) |
| 8 | `slack_post_summary` | Slack incoming webhook | **W** |

### Plan

| Partie | Sujet | Durée |
|---|---|---|
| 0 | Setup : **OAuth Google pas-à-pas (Étapes A→F)** + variables d'environnement + dépendances | 30 min |
| 1 | Implémentation des 8 outils + wrap LangChain | 30 min |
| 2 | Agent ReAct (LangGraph prebuilt) sur le golden set (5 demandes) | 30 min |
| 3 | Limites observées de ReAct sur un briefing complet | 10 min |
| 4 | Workflow LangGraph `MorningBriefing` (8 nodes, routing, reflection, retry) | 50 min |
| 5 | Comparaison & synthèse + 6 patterns Anthropic mappés | 10 min |

### Pré-requis

- **Python 3.10+** avec Jupyter.
- **Clé API Groq** — <https://console.groq.com> → `GROQ_API_KEY`.
- **Compte Google dédié bootcamp** (jamais perso/pro pour ce TP).
- **`credentials.json`** Google OAuth — la procédure complète est **dans le notebook (§ 0.1)**, ~ 15 min, une seule fois.
- *(Optionnel)* Webhook Slack pour `slack_post_summary` — sinon stub console.

### Installation

```bash
export GROQ_API_KEY="gsk_..."
export GOOGLE_CREDENTIALS_PATH="./credentials.json"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/..."   # optionnel

pip install langchain langchain-community langchain-groq langgraph
pip install google-auth google-auth-oauthlib google-api-python-client
pip install python-dotenv requests pandas
```

> 💡 Préférer un fichier **`.env`** à côté du notebook (chargé via `python-dotenv`) — voir § 0.2 du notebook.

### Lancement

```bash
jupyter notebook tp4a-agent-morning-briefing.ipynb
```

Au **premier run**, la cellule § 0.5 ouvre un onglet navigateur pour le consentement OAuth (3 scopes : `gmail.modify`, `calendar.readonly`, `drive.readonly`). Un `token.json` est créé et réutilisé ensuite (refresh automatique).

### ⚠️ Sécurité

| Fichier | À commit ? | Pourquoi |
|---|---|---|
| `credentials.json` | ❌ jamais | Contient `client_id` + `client_secret` |
| `token.json` | ❌ jamais | Équivalent à un mot de passe sur votre compte Google |
| `.env` | ❌ jamais | Contient `GROQ_API_KEY` |

Ajouter ces 3 fichiers à votre `.gitignore`.

### Livrables attendus

- Stack OAuth opérationnelle (`token.json` généré, 3 sanity checks Calendar/Gmail/Drive verts).
- 5 demandes du golden set exécutées avec l'agent ReAct (traces commentées).
- Briefing matinal généré par le workflow LangGraph (markdown + post Slack — réel ou stub).
- Tableau comparatif ReAct ↔ MorningBriefing rempli (Partie 5).

### Régénérer le notebook

Le notebook est généré par un script idempotent — utile si vous voulez le modifier en versionnant les changements de structure :

```bash
python /tmp/build_briefing_nb.py
```

---

## Suite — TP 4.b (no-code n8n)

Chaque notebook du TP 4.a a son **pendant n8n** dans le TP 4.b :

| Notebook 4.a | Runbook 4.b |
|---|---|
| `tp4a-agent-research-assistant.ipynb` | [`../TP4-b/tp4b-n8n-research-assistant.md`](../TP4-b/tp4b-n8n-research-assistant.md) — recherche IA, 3 outils |
| `tp4a-agent-morning-briefing.ipynb` | [`../TP4-b/tp4b-n8n-morning-briefing.md`](../TP4-b/tp4b-n8n-morning-briefing.md) — briefing Gmail/Calendar/Drive, 8 outils |

La stack Docker (`n8n + Postgres + Qdrant`) est mutualisée — décrite dans le premier runbook, réutilisée par le second.
