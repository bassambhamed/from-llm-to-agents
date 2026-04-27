# TP 4.b — AI Research Assistant en **no-code** avec n8n

> **Suite du Notebook 1 du TP 4.a** (`tp4a-agent-research-assistant.ipynb`). On reprend **le même use case** (assistant de recherche IA avec 3 outils : RAG local, recherche web, arXiv) et on le reconstruit **sans écrire une ligne de code Python**, avec [n8n](https://n8n.io) self-hosted.
>
> **Durée :** ~ 1 h 15 · **Coût :** 0 € (Groq + Tavily en free tier · n8n self-hosted) · **Format :** runbook pas-à-pas, à suivre dans l'ordre.
>
> 👉 **Pendant du Notebook 2** (briefing matinal Gmail/Calendar/Drive) : voir [`tp4b-n8n-morning-briefing.md`](./tp4b-n8n-morning-briefing.md) — la stack Docker est mutualisée.

---

## Sommaire

- [0. Objectifs & ce que vous allez construire](#0-objectifs--ce-que-vous-allez-construire)
- [1. Architecture cible](#1-architecture-cible)
- [2. Pré-requis](#2-pré-requis)
- [Étape 1 — Lancer la stack Docker (n8n + Qdrant)](#étape-1--lancer-la-stack-docker-n8n--qdrant)
- [Étape 2 — Premier accès à n8n & credentials](#étape-2--premier-accès-à-n8n--credentials)
- [Étape 3 — Ingérer le corpus IA dans Qdrant (RAG)](#étape-3--ingérer-le-corpus-ia-dans-qdrant-rag)
- [Étape 4 — Construire le workflow Agent](#étape-4--construire-le-workflow-agent)
- [Étape 5 — Tester avec le golden set (3 scénarios)](#étape-5--tester-avec-le-golden-set-3-scénarios)
- [Étape 6 — Comparaison TP 4.a (Python) ↔ TP 4.b (n8n)](#étape-6--comparaison-tp-4a-python--tp-4b-n8n)
- [Annexes](#annexes)

---

## 0. Objectifs & ce que vous allez construire

À l'issue du TP, vous aurez :

1. Une **stack Docker** locale `n8n + Qdrant` opérationnelle.
2. Un **workflow n8n** avec un nœud **AI Agent** (LangChain interne) connecté à **3 outils** :
   - `rag_search` → vector store Qdrant alimenté avec le corpus IA du TP 3 ;
   - `web_search` → Tavily (HTTP) ;
   - `arxiv_search` → API arXiv (HTTP).
3. Un **webhook** qui prend en entrée une question et renvoie la réponse de l'agent + ses traces.
4. Un **tableau comparatif** chiffré entre la version Python (TP 4.a) et la version no-code (TP 4.b).

**Pourquoi n8n ?** Même primitive d'agent qu'en TP 4.a (LangChain ReAct sous le capot), mais accessible à un profil **non développeur**, avec un **canvas visuel**, des **connecteurs prêts à l'emploi**, et une exécution **observable** (chaque nœud expose ses entrées/sorties).

---

## 1. Architecture cible

```
                    ┌─────────────────────────┐
   POST /webhook    │   Webhook (trigger)     │
   { "question":… }─▶│   chemin /research     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────────────────┐
                    │           AI Agent node             │
                    │  ┌───────────────────────────────┐  │
                    │  │  LLM : Groq llama-3.3-70b     │  │
                    │  │  Memory : Buffer Window (5)   │  │
                    │  │  System prompt (versionné)    │  │
                    │  └───────────────────────────────┘  │
                    │  Tools déclarés :                   │
                    │   ① rag_search   (Vector Store)     │
                    │   ② web_search   (HTTP → Tavily)    │
                    │   ③ arxiv_search (HTTP → arXiv)     │
                    └────────────┬────────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │  Respond to Webhook     │
                    │  (réponse JSON)         │
                    └─────────────────────────┘
```

Stockage :
- **Qdrant** (port `6333`) — embeddings du corpus IA du TP 3 (4 fichiers Markdown).
- **Postgres** (port `5432`) — base interne de n8n (workflows, exécutions, credentials chiffrés).

---

## 2. Pré-requis

| Élément | Détail |
|---|---|
| **Docker Desktop** | installé et démarré (Mac / Windows / Linux) |
| **~ 4 Go RAM libres** | pour la stack n8n + Qdrant + Postgres |
| **Ports libres** | `5678` (n8n), `6333` (Qdrant), `5432` (Postgres) |
| **Clé API Groq** | gratuite sur https://console.groq.com → format `gsk_...` |
| **Clé API Tavily** | gratuite (1 000 req/mois) sur https://tavily.com → format `tvly-...` |
| **Corpus du TP 3** | les 4 `.md` dans `03 RAG/rag-app/sample_data/` |

> Si Docker pose problème, l'alternative **n8n Cloud** (free trial 14 j) fait tourner exactement le même workflow — Qdrant peut être remplacé par un node **In-Memory Vector Store** dans n8n (limite : la base se vide à chaque redémarrage du workflow).

---

## Étape 1 — Lancer la stack Docker (n8n + Qdrant)

### 1.1 Créer le dossier de travail

```bash
mkdir -p ~/tp4b-n8n && cd ~/tp4b-n8n
```

### 1.2 Créer `docker-compose.yml`

Copier le fichier suivant à la racine de `~/tp4b-n8n/` :

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_USER: n8n
      POSTGRES_PASSWORD: n8npass
      POSTGRES_DB: n8n
    volumes:
      - postgres_data:/var/lib/postgresql/data

  qdrant:
    image: qdrant/qdrant:latest
    restart: unless-stopped
    ports:
      - "6333:6333"      # API REST
      - "6334:6334"      # gRPC
    volumes:
      - qdrant_data:/qdrant/storage

  n8n:
    image: n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      DB_POSTGRESDB_DATABASE: n8n
      DB_POSTGRESDB_USER: n8n
      DB_POSTGRESDB_PASSWORD: n8npass
      N8N_HOST: localhost
      N8N_PORT: 5678
      N8N_PROTOCOL: http
      WEBHOOK_URL: http://localhost:5678/
      GENERIC_TIMEZONE: Europe/Paris
    depends_on:
      - postgres
      - qdrant
    volumes:
      - n8n_data:/home/node/.n8n

volumes:
  postgres_data:
  qdrant_data:
  n8n_data:
```

### 1.3 Démarrer la stack

```bash
docker compose up -d
```

Attendre ~ 30 s puis vérifier :

```bash
docker compose ps
# Les 3 services doivent être 'Up'

curl -s http://localhost:6333/collections   # → {"result": ..., "status": "ok"}
curl -s http://localhost:5678               # → page de connexion n8n
```

---

## Étape 2 — Premier accès à n8n & credentials

### 2.1 Créer le compte propriétaire

Ouvrir <http://localhost:5678> dans le navigateur. n8n demande de créer le **owner account** (email + mot de passe) — uniquement local, aucun envoi à l'extérieur.

### 2.2 Déclarer les credentials

**Settings → Credentials → New** (deux credentials à créer) :

#### A. Groq API

- **Type** : `Groq API` (ou `OpenAI API` si Groq n'est pas listé — voir astuce ci-dessous).
- **API Key** : votre clé `gsk_...`.
- **Save**.

> 💡 **Astuce compatibilité Groq** : si vous utilisez le credential `OpenAI`, mettez :
> - **Base URL** : `https://api.groq.com/openai/v1`
> - **API Key** : votre `gsk_...`
> Groq expose une API **OpenAI-compatible**, donc le node `OpenAI Chat Model` fonctionne sans modification.

#### B. Qdrant (vector store)

- **Type** : `Qdrant API`.
- **URL** : `http://qdrant:6333` (nom du service Docker, **pas** `localhost` car n8n est dans le même réseau Compose).
- **API Key** : laisser vide (Qdrant local sans auth en dev).
- **Save**.

#### C. (optionnel) HTTP Header Auth pour Tavily

Tavily se consomme via HTTP, on peut soit passer la clé en header par requête, soit la stocker comme credential `Header Auth` :
- **Type** : `Header Auth`.
- **Name** : `Authorization`.
- **Value** : `Bearer tvly-...`.

---

## Étape 3 — Ingérer le corpus IA dans Qdrant (RAG)

On va créer un **petit workflow d'ingestion** séparé (à exécuter une seule fois) qui lit les 4 fichiers Markdown du TP 3, les découpe, les embedde et les stocke dans une collection Qdrant `ai_corpus`.

### 3.1 Créer le workflow `Ingest KB`

**Workflows → + Add workflow → renommer "Ingest KB"**.

### 3.2 Ajouter les nœuds (dans l'ordre)

| # | Node | Paramètres clés |
|---|---|---|
| 1 | **Manual Trigger** | (aucun) |
| 2 | **Read/Write Files from Disk** (`Read`) | `File Selector` : `/data/sample_data/*.md` (voir 3.3) |
| 3 | **Default Data Loader** | Type : `Text` · `Text from`: `Binary` · `Binary property`: `data` |
| 4 | **Recursive Character Text Splitter** | `Chunk Size` : `500` · `Chunk Overlap` : `50` |
| 5 | **Embeddings HuggingFace Inference** *(ou OpenAI/Groq)* | Modèle : `sentence-transformers/all-MiniLM-L6-v2` |
| 6 | **Qdrant Vector Store** | Mode : `Insert documents` · Collection : `ai_corpus` · Credential : Qdrant |

### 3.3 Monter le corpus dans le conteneur n8n

Pour que n8n « voie » les fichiers `.md` du TP 3, on monte le dossier en volume. **Stopper la stack** :

```bash
docker compose down
```

Éditer `docker-compose.yml`, dans le service `n8n`, ajouter sous `volumes:` :

```yaml
      - "/ABSOLUTE/PATH/TO/from-llm-to-agent/03 RAG/rag-app/sample_data:/data/sample_data:ro"
```

Remplacer `/ABSOLUTE/PATH/TO/...` par le chemin réel sur votre machine. Puis :

```bash
docker compose up -d
```

### 3.4 Exécuter l'ingestion

Dans le workflow `Ingest KB`, cliquer **Execute Workflow** (en bas du canvas).

✅ **Vérification** :

```bash
curl -s http://localhost:6333/collections/ai_corpus | python3 -m json.tool
# "points_count" doit être > 0 (typiquement 30-80 chunks pour 4 fichiers)
```

> Si l'ingestion échoue sur les embeddings HuggingFace (rate limit), vous pouvez utiliser `OpenAI Embeddings` (Groq ne propose pas encore d'embeddings → utiliser une vraie clé OpenAI, ou un node Ollama local avec `nomic-embed-text`).

---

## Étape 4 — Construire le workflow Agent

C'est le **cœur** du TP. On crée un nouveau workflow `AI Research Assistant`.

### 4.1 Vue d'ensemble

7 nœuds à brancher :

```
[Webhook] → [AI Agent] → [Respond to Webhook]
                ▲ ▲ ▲
                │ │ └─── Tool 3: arxiv_search   (HTTP)
                │ └────── Tool 2: web_search    (HTTP → Tavily)
                └──────── Tool 1: rag_search    (Vector Store)
            (sub-nodes)
                ├─── LLM   : Groq Chat Model
                └─── Memory: Window Buffer (k=5)
```

### 4.2 Webhook (trigger)

- Node : **Webhook**.
- HTTP Method : `POST`.
- Path : `research`.
- Response Mode : `Using 'Respond to Webhook' Node`.

URL générée (en Test) : `http://localhost:5678/webhook-test/research`.

### 4.3 AI Agent node

- Ajouter un node **AI Agent** (catégorie *Advanced AI*).
- **Agent Type** : `Tools Agent` (équivalent ReAct côté LangChain).
- **Prompt Source** : `Define below` → coller le system prompt (§ 4.4).
- **Text** (input) : `={{ $json.body.question }}` (extrait la question du payload webhook).

### 4.4 System prompt (à coller dans le champ *System Message*)

```
Tu es un AI Research Assistant spécialisé en intelligence artificielle.

Ton objectif : répondre à des questions techniques sur les LLMs, RAG, embeddings,
fine-tuning, agents IA, en t'appuyant sur 3 outils complémentaires :

• rag_search    → corpus IA local (priorité, source de vérité interne)
• web_search    → recherche web généraliste (pour combler les manques du corpus)
• arxiv_search  → papiers scientifiques récents (questions pointues, dates)

Règles de raisonnement :
1. TOUJOURS commencer par interroger rag_search.
2. Si la réponse RAG est insuffisante (vide, hors sujet, partielle) → utiliser
   web_search puis arxiv_search.
3. Citer tes sources à la fin sous forme : "Sources: [rag_search], [web_search], ..."
4. Si la question est hors périmètre IA, répondre poliment que ce n'est pas
   ta spécialité.
5. Ne jamais inventer une référence ; si aucune source ne couvre la question,
   le dire explicitement.

Format de réponse : 2-4 paragraphes, ton pédagogique, en français.
```

### 4.5 Sub-node : LLM (Groq)

Sur le nœud AI Agent, cliquer le **+** sous *Chat Model* :
- Node : **OpenAI Chat Model** (compatible Groq).
- **Credential** : OpenAI (configuré avec base URL Groq en § 2.2).
- **Model** : `llama-3.3-70b-versatile`.
- **Options → Temperature** : `0.2` (factuel, peu de hallucinations).

### 4.6 Sub-node : Memory

Cliquer le **+** sous *Memory* :
- Node : **Window Buffer Memory**.
- **Context Window Length** : `5` (5 derniers échanges).

### 4.7 Tool 1 — `rag_search` (Vector Store retriever)

Cliquer le **+** sous *Tool* :
- Node : **Vector Store Question Answer Tool** (ou `Vector Store Tool`).
- **Name** : `rag_search`.
- **Description** : `Recherche dans le corpus IA local (Transformer, RAG, fine-tuning, vector DBs). À utiliser EN PREMIER pour toute question IA.`
- Sub-node **Vector Store** → `Qdrant Vector Store` :
  - Mode : `Retrieve documents`.
  - Collection : `ai_corpus`.
  - Credential : Qdrant.
  - Top K : `4`.
- Sub-node **Embeddings** → même que pour l'ingestion (HuggingFace MiniLM L6 v2).

### 4.8 Tool 2 — `web_search` (Tavily via HTTP)

Cliquer le **+** sous *Tool* :
- Node : **HTTP Request Tool** (ou `Custom n8n Workflow Tool` si vous préférez wrapper).
- **Name** : `web_search`.
- **Description** : `Recherche web généraliste via Tavily. À utiliser quand rag_search ne donne pas de résultat satisfaisant.`
- **Method** : `POST`.
- **URL** : `https://api.tavily.com/search`.
- **Authentication** : `None` (clé dans le body).
- **Body Parameters** (JSON) :
  ```json
  {
    "api_key": "tvly-VOTRE_CLE",
    "query": "{query}",
    "search_depth": "basic",
    "max_results": 3
  }
  ```
- Dans le bloc **Tool Parameters**, déclarer un input nommé `query` (string) que l'agent passera à l'appel.

### 4.9 Tool 3 — `arxiv_search` (HTTP)

Cliquer le **+** sous *Tool* :
- Node : **HTTP Request Tool**.
- **Name** : `arxiv_search`.
- **Description** : `Recherche de papiers scientifiques récents sur arXiv. À utiliser pour des questions très pointues ou récentes.`
- **Method** : `GET`.
- **URL** : `http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=3`.
- Réponse en XML — le LLM sait extraire les titres/abstracts.

### 4.10 Respond to Webhook

- Node : **Respond to Webhook**.
- Response Code : `200`.
- Response Body :
  ```json
  {
    "question": "={{ $('Webhook').item.json.body.question }}",
    "answer": "={{ $json.output }}",
    "tools_used": "={{ $json.intermediateSteps }}"
  }
  ```

### 4.11 Sauvegarder & activer

`Save` (en haut à droite) puis bouton **Activate** (toggle).

---

## Étape 5 — Tester avec le golden set (3 scénarios)

On reprend 3 questions du golden set du TP 4.a — chacune sollicite des outils différents.

### Scénario 1 — Question couverte par le RAG

```bash
curl -X POST http://localhost:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelle est la différence entre BM25 et un retriever dense ?"}'
```

🎯 **Comportement attendu** : l'agent appelle **uniquement** `rag_search` (la réponse est dans `03 RAG/rag-app/sample_data/`). Citer la section *Vector DBs*.

### Scénario 2 — Question nécessitant le web

```bash
curl -X POST http://localhost:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{"question": "Quelles sont les nouveautés de Claude 4.7 publiées en 2026 ?"}'
```

🎯 **Comportement attendu** : `rag_search` retourne peu/rien → l'agent **fallback** sur `web_search`. Réponse avec citation Tavily.

### Scénario 3 — Question scientifique pointue

```bash
curl -X POST http://localhost:5678/webhook/research \
  -H "Content-Type: application/json" \
  -d '{"question": "Cite-moi 2 papiers récents sur Mixture-of-Experts et résume-en un."}'
```

🎯 **Comportement attendu** : `arxiv_search` est sélectionné. L'agent cite 2 titres + auteurs + année.

### 5.1 Lire les traces

Dans n8n : **Executions** (panneau gauche) → cliquer la dernière exécution → chaque nœud affiche **Input / Output** en JSON. Le sous-nœud AI Agent montre la séquence **Thought → Action → Observation** (équivalent ReAct).

> 💡 Pour partager une trace : *clic droit → Copy execution URL*.

---

## Étape 6 — Comparaison TP 4.a (Python) ↔ TP 4.b (n8n)

Remplir ce tableau après vos 3 tests :

| Critère | TP 4.a (LangChain Python) | TP 4.b (n8n no-code) |
|---|---|---|
| Lignes de code écrites | ~ 200 lignes Python | **0** (config uniquement) |
| Temps de mise en place | 30-45 min (env + deps) | 60-75 min (Docker + UI) |
| Latence moyenne / question | ~ 3-6 s | ~ 4-7 s (overhead UI) |
| Observabilité par défaut | logs `verbose=True` | **Executions UI** + diff par nœud |
| Versionning | git (`.ipynb`) | export `workflow.json` (à versionner) |
| Profil cible | Data Scientist / AI Dev | **Data Engineer / Ops / métier** |
| Multi-environnement | venv + requirements.txt | Docker Compose **portable** |
| Scaling | manuel | n8n **queue mode** (workers Redis) |
| Limite principale | maintenance code | logique complexe → custom node JS |

**Question d'arbitrage** (à débattre en groupe) :
> *Pour un PoC interne destiné à 5-10 utilisateurs métier, lequel choisiriez-vous, et pourquoi ?*

---

## Annexes

### A. Variables d'environnement utiles

| Variable | Valeur | Effet |
|---|---|---|
| `N8N_LOG_LEVEL=debug` | dans `n8n.environment` | logs verbeux côté serveur |
| `N8N_DIAGNOSTICS_ENABLED=false` | idem | désactive la télémétrie |
| `EXECUTIONS_DATA_PRUNE=true` | idem | purge auto des vieilles exécutions |

### B. Exporter / importer le workflow

- **Export** : sur un workflow ouvert, *menu ⋯ → Download* → fichier `.json`.
- **Import** : *Workflows → Import from File* → recharger le `.json` (les credentials doivent être recréés à la main, ils ne sont jamais exportés en clair).

### C. Dépannage

| Symptôme | Cause probable | Solution |
|---|---|---|
| `connection refused` sur Qdrant | URL `localhost` au lieu de `qdrant` | Utiliser le **nom du service Docker** dans le credential |
| Webhook → 404 | workflow non *Activated* | Toggle Activate (en haut à droite) |
| AI Agent boucle (max iterations) | system prompt ambigu, ou outil mal décrit | Renforcer la *Description* de chaque tool, baisser `max_iterations` à 5 |
| Erreur 401 Tavily | clé invalide ou en dehors du free tier | Vérifier la clé, basculer sur web_search via DuckDuckGo HTML scraping (tool de secours) |
| Embeddings HF rate-limited | trop d'appels en local | Réduire `Chunk Size` à 800 → moins de chunks, ou passer à Ollama `nomic-embed-text` |

### D. Pour aller plus loin

- **AI Agent avec output parser structuré** (JSON schema) → pour intégrer la sortie dans un autre système.
- **Sub-workflows** réutilisables : extraire les 3 tools dans un workflow séparé pour les partager entre agents.
- **n8n + LangSmith** : ajouter un node HTTP qui POST chaque step dans LangSmith pour tracer l'agent comme en TP 4.a.
- **Authentification du webhook** : ajouter un *Header Auth* sur le node Webhook (clé partagée) avant tout déploiement.

### E. Arrêter / nettoyer la stack

```bash
docker compose down            # stop, volumes conservés
docker compose down -v         # stop + suppression des données (Qdrant + Postgres + n8n)
```

---

## Livrables attendus

1. ✅ Stack `docker compose ps` → 3 services `Up`.
2. ✅ Collection Qdrant `ai_corpus` peuplée (`points_count > 0`).
3. ✅ Workflow `AI Research Assistant` **actif**.
4. ✅ 3 exécutions enregistrées (une par scénario), traces visibles dans **Executions**.
5. ✅ Tableau comparatif **TP 4.a ↔ TP 4.b** rempli (§ Étape 6).
6. ✅ Export `workflow.json` du runbook (livrable individuel).
