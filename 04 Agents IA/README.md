# Module 04 — Agents IA : LangChain → LangGraph → n8n

**Jour 3** du bootcamp *From LLMs to Agents* · **~ 6 h** (3 h cours + 3 h TP)

Module final qui **capitalise** sur les modules 01-03 : on prend le LLM (M1), les patterns ReAct du prompt engineering (M2), le retriever du RAG (M3) — et on les assemble en **agent IA opérationnel**, en code et en no-code.

Le module est structuré en **2 use cases × 2 implémentations** :

|  | **Use case 1 — AI Research Assistant** | **Use case 2 — Briefing matinal** |
|---|---|---|
| **Outils** | 3 (RAG TP3, Tavily web, arXiv) | 8 (Gmail, Calendar, Drive, Slack, +) |
| **Lecture / Écriture** | lecture seule | **lecture + écriture (drafts Gmail, posts Slack)** |
| **Code Python** | [`TP4-a/tp4a-agent-research-assistant.ipynb`](TP4-a/tp4a-agent-research-assistant.ipynb) | [`TP4-a/tp4a-agent-morning-briefing.ipynb`](TP4-a/tp4a-agent-morning-briefing.ipynb) |
| **No-code n8n** | [`TP4-b/tp4b-n8n-research-assistant.md`](TP4-b/tp4b-n8n-research-assistant.md) | [`TP4-b/tp4b-n8n-morning-briefing.md`](TP4-b/tp4b-n8n-morning-briefing.md) |
| **Difficulté** | ★★ | ★★★ (OAuth Google + idempotence) |

Le 1er use case est **académique** (corpus IA + recherche web) → idéal pour découvrir agent / tools / boucle ReAct sans surcharge.
Le 2nd est **réaliste** (assistant productivité multi-services Google) → soulève les vraies questions opérationnelles : OAuth, idempotence, sandbox, *human-in-the-loop*.

---

## Public & prérequis

- **Cible** : data engineers, data scientists, devs IA — profils ayant validé les modules 01-03.
- **Pré-requis techniques** :
  - Modules 01-03 du bootcamp validés.
  - Python 3.10+, Jupyter.
  - Clé Groq gratuite (`gsk_...`) — <https://console.groq.com>.
  - Clé Tavily gratuite (`tvly-...`) — pour le notebook 1.
  - Compte Google **dédié bootcamp** + Docker Desktop — pour le notebook 2 et tout TP 4.b.
  - Webhook Slack (optionnel, sinon stub console) — notebook 2.
- **Format** : 3 h cours frontal + 3 h TP. Notebooks et runbooks sont **autonomes**, exécutables individuellement.

---

## Objectifs pédagogiques

À l'issue du module, le participant est capable de :

1. **Décrire** l'anatomie d'un agent IA (system prompt, outils, mémoire, boucle de raisonnement) et choisir entre **agent autonome** (ReAct) et **workflow contrôlé** (LangGraph) selon le besoin.
2. **Construire** un agent ReAct avec **LangChain + LangGraph prebuilt** (`create_react_agent`) sur un cas multi-tools.
3. **Construire** un workflow Adaptive avec **LangGraph** (`StateGraph`, edges conditionnels, reflection loop, retry).
4. **Reconstruire** le même agent en **no-code n8n** (Schedule Trigger, AI Agent node, OAuth Google, Structured Output Parser).
5. **Identifier** les **6 *Agentic Design Patterns*** (Anthropic 2024) à l'œuvre dans son code.
6. **Arbitrer** code Python ↔ no-code n8n selon contexte (profil cible, fréquence d'évolution, gouvernance, idempotence).

---

## Cours (3 h)

### § 4.1 — Anatomie & patterns d'un Agent IA (1 h 30)

Brain (LLM) · Memory · Tools · Reasoning Loop · **Agent autonome vs Agentic Workflow** · rappel ReAct (Module 02). Les **6 Agentic Design Patterns** (Anthropic 2024) :

| # | Pattern | Idée |
|---|---|---|
| 1 | Prompt chaining | sortie d'un LLM → entrée du suivant |
| 2 | Parallélisation | multi-source en parallèle, agrégation |
| 3 | Routing | classifier puis dispatcher vers une branche |
| 4 | Reflection loop | auto-évaluation + retry contrôlé |
| 5 | Orchestrator-workers | un orchestrateur délègue à N workers spécialisés |
| 6 | Tool use | le LLM choisit et appelle des outils externes |

### § 4.2 — Adaptive RAG & frameworks (1 h 30)

- **Self-RAG** (Asai 2023) · **CRAG** (Yan 2024) · **Adaptive RAG** (Jeong 2024).
- **LangChain** : `Tool`, retriever wrapping, `create_react_agent` (héritage).
- **LangGraph** : `StateGraph`, nodes / edges, edges conditionnels, *prebuilt* `create_react_agent` (recommandé).
- **n8n** : AI Agent node, Tools Agent, Schedule Trigger, Structured Output Parser, gestion OAuth visuelle.
- **Gouvernance** : sandbox compte dédié, *human-in-the-loop*, idempotence, **write tools en *draft only***.

---

## TP 4 (3 h)

### TP 4.a — Code Python · [`TP4-a/`](TP4-a/)

Voir [`TP4-a/README.md`](TP4-a/README.md) pour le détail.

| Notebook | Use case | Outils | Durée |
|---|---|---|---|
| `tp4a-agent-research-assistant.ipynb` | Recherche IA | RAG + Tavily + arXiv | 2 h 15 |
| `tp4a-agent-morning-briefing.ipynb` | Productivité quotidienne | Gmail + Calendar + Drive + Slack | 2 h 30 |

Progression de **chaque** notebook : `agent ReAct simple → workflow LangGraph contrôlé → comparaison`.

### TP 4.b — No-code n8n · [`TP4-b/`](TP4-b/)

| Runbook | Use case | Stack | Durée |
|---|---|---|---|
| `tp4b-n8n-research-assistant.md` | Recherche IA | n8n + Qdrant + Postgres | 1 h 15 |
| `tp4b-n8n-morning-briefing.md` | Productivité (cron 8h30) | n8n + Postgres + OAuth Web Google | 1 h 30 |

La **stack Docker est mutualisée** entre les 2 runbooks (décrite dans le premier, réutilisée par le second).

---

## Architectures cibles

### Use case 1 — AI Research Assistant

```
question ─▶ Agent (LangChain ReAct  OR  n8n AI Agent)
              ├─ rag_search       (Chroma TP3 / Qdrant)
              ├─ tavily_search    (web)
              └─ arxiv_search     (papiers)
            ─▶ réponse + sources citées
```

### Use case 2 — Morning Briefing (workflow LangGraph)

```
cron 8h30 ─▶ MorningBriefingGraph
              ├─ fetch_calendar           Google Calendar
              ├─ enrich_meetings          Gmail + Drive (1 sub-task / event)
              ├─ scan_inbox               Gmail (is:unread newer_than:1d)
              ├─ classify_urgency         LLM (JSON urgent/non)
              ├─ [if urgent] draft_replies   Gmail Draft (jamais send)
              ├─ extract_deadlines        LLM (NER + dates)
              ├─ assemble_briefing        LLM → markdown final
              ├─ grade_briefing           LLM (reflection, retry × 1)
              └─ post_to_slack            DM perso
```

**8 nodes · 2 edges conditionnels · 1 reflection loop · couvre les 6 patterns Anthropic.**

---

## Structure du dossier

```
04 Agents IA/
├── README.md                                       ← ce fichier
├── slides/
│   └── agents.pdf                                  ← support de cours (~ 50 pages)
├── TP4-a/                                          ← notebooks Python
│   ├── README.md                                   ← détail par notebook + setup OAuth
│   ├── tp4a-agent-research-assistant.ipynb         ← Notebook 1 — 29 cellules
│   └── tp4a-agent-morning-briefing.ipynb           ← Notebook 2 — 48 cellules (OAuth Google § 0.1)
└── TP4-b/                                          ← runbooks no-code n8n
    ├── tp4b-n8n-research-assistant.md              ← stack Docker + workflow recherche
    └── tp4b-n8n-morning-briefing.md                ← réutilise la stack + OAuth Web client
```

---

## Stack technique

| Couche | Outil |
|---|---|
| **LLM** | Groq + `llama-3.3-70b-versatile` (free tier, OpenAI-compatible) |
| **Frameworks Python** | LangChain (`Tool`), **LangGraph** (`create_react_agent`, `StateGraph`) |
| **No-code** | **n8n** self-hosted (Docker) |
| **Vector store (TP 4.b)** | Qdrant |
| **Outils Notebook 1** | Chroma (retriever TP3), Tavily, arXiv |
| **Outils Notebook 2** | Google Gmail / Calendar / Drive APIs (OAuth 2.0), Slack incoming webhook |
| **Observabilité** | LangSmith (cellules optionnelles), n8n *Executions panel* |

---

## Livrables attendus

### TP 4.a — Python

- ✅ 2 notebooks exécutés de bout en bout.
- ✅ Notebook 1 — 5 traces ReAct + 5 traces LangGraph commentées + tableau comparatif (latence, outils, succès).
- ✅ Notebook 2 — `token.json` Google généré, 5 demandes du golden set traitées, briefing markdown produit + posté sur Slack (réel ou stub).

### TP 4.b — n8n

- ✅ Stack `docker compose ps` → 3 services *Up*.
- ✅ Workflow `Research Assistant` actif, 3 scénarios testés (RAG / web / arXiv).
- ✅ Workflow `Morning Briefing` exécutable manuellement, **draft Gmail vérifié dans la boîte Drafts**.
- ✅ Tableau comparatif Python ↔ n8n rempli (1 par use case).
- ✅ Exports `workflow.json` des deux workflows.

---

## Sécurité — règles non négociables

| Fichier | À commit ? | Pourquoi |
|---|---|---|
| `credentials.json` (Google OAuth) | ❌ jamais | `client_id` + `client_secret` |
| `token.json` (Google) | ❌ jamais | équivalent à un mot de passe sur votre Gmail/Drive/Calendar |
| `.env` (clés API) | ❌ jamais | `GROQ_API_KEY`, `TAVILY_API_KEY`, `SLACK_WEBHOOK_URL` |

À ajouter au `.gitignore` du dossier de travail. En cas de compromission : **Google Cloud Console → Credentials → supprimer le client OAuth** (révoque tous les tokens dérivés).

**Compte Google** : utiliser un compte **dédié bootcamp**, jamais un compte perso ou pro. Le notebook 2 crée des drafts Gmail réels — un mauvais paramétrage de sandbox = risque de spam.

---

## Lien avec les modules précédents

| Brique du Module 04 | Source |
|---|---|
| System prompt de l'agent (rôle, garde-fous, *refuse hors-domaine*) | **Module 02** — patterns ReAct, auto-critique, indice de confiance |
| Outil `rag_search` (corpus IA local) | **Module 03** — pipeline RAG repackagé comme outil d'agent |
| Paramètres `temperature`, `top-p`, choix de modèle | **Module 01** — API LLM, stratégies de décodage |
| Reflection loop (`grade_docs`, `grade_answer`, `grade_briefing`) | **Module 03** — RAGas + auto-critique du Module 02 |

---

## Synthèse & clôture (fin de Jour 3)

- Récap des 4 briques : **LLM → Prompt Engineering → RAG → Agents IA**.
- Démo formateur sur les 2 use cases (Python + n8n).
- Discussion ouverte : *« Quel agent allez-vous prototyper la semaine prochaine dans votre équipe ? »*
- Remise des livrables, bibliothèque de prompts consolidée, questionnaire de satisfaction.
