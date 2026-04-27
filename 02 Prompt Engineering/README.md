# Module 02 — Prompt Engineering

**Jour 1 · Partie 2 · 1 h 30 (cours) + 3 h (TP 2)**

Second module de la formation *IA générative · LLMs · Prompt Engineering · RAG · Agents IA & Automatisation*. Il transforme la capacité acquise au Module 01 (appeler un LLM) en **compétence productive** : formuler des prompts robustes, reproductibles et versionnés, capables de tenir en production.

Le prompt est l'**interface de programmation des LLMs**. La qualité d'un système RAG (Module 03) ou d'un agent IA (Module 04) dépend directement de la qualité des prompts qui les pilotent — system prompt d'agent, prompt d'augmentation RAG, prompts de techniques avancées (Query Rewriting, Multi-Query, HyDE).

---

## Public & prérequis

- **Cible** : ingénieurs DATA, data scientists, développeurs IA, profils techniques travaillant avec des LLMs.
- **Prérequis** : **Module 01 validé** — savoir appeler un LLM via API, comprendre `temperature` / `top-p`, avoir manipulé un notebook Python.
- **Matériel** :
  - Python 3.10+ avec Jupyter.
  - **Clé API Groq** (gratuite, free tier) — création en 30 secondes sur **https://console.groq.com**.

---

## Objectifs pédagogiques

À l'issue du module, le participant est capable de :

1. **Structurer** un prompt selon l'anatomie *Rôle / Contexte / Instructions / Contraintes / Exemples* et évaluer sa qualité.
2. **Choisir et appliquer** la technique adaptée : Zero-Shot, Few-Shot, Chain-of-Thought, Self-Consistency, Role Prompting, balises XML, Generate Knowledge, Prompt Chaining, Tree of Thoughts, Directional Stimulus, ReAct, Indice de confiance, Active-Prompt.
3. **Construire** des prompts production-ready pour 5 cas d'usage concrets (résumé multi-niveau, classification multi-labels, extraction JSON, génération de code, Q&A RAG).
4. **Détecter et mitiger** les risques : prompt injection, fuite de secrets (clés API, tokens), hallucinations.
5. **Versionner** une bibliothèque de prompts comme un artefact logiciel (id, version, tests, métriques).

---

## Contenu

### Cours — 1 h 30 (slides : `slides/prompt-engineering.pdf`)

Le support couvre **4 parties** :

| # | Partie | Contenu clé |
|---|---|---|
| 1 | **Fondamentaux** | Anatomie du prompt (4 éléments), 4 qualités (clarté, spécificité, contexte, testabilité), prompt naïf vs structuré |
| 2 | **Techniques de base** | Zero-Shot, Few-Shot, Chain-of-Thought, Self-Consistency |
| 3 | **Techniques avancées** | Role Prompting, balises XML, Generate Knowledge, Prompt Chaining, Tree of Thoughts, Directional Stimulus, ReAct, Indice de confiance, Active-Prompt |
| 4 | **Applications pratiques** | 5 prompts production-ready, anti-patterns, sécurité (prompt injection, fuite de secrets), bibliothèque versionnée, checklist production |

### TP 2 — Prompt Engineering : du basique à l'avancé (3 h)

Notebook : **`TP/tp2-prompt-engineering.ipynb`** (10 parties)

| Partie | Sujet | Durée |
|---|---|---|
| 0 | Mise en place (API Groq, helpers, config) | 10 min |
| 1 | Anatomie et qualités d'un prompt | 20 min |
| 2 | Techniques de base — Zero-Shot & Few-Shot | 25 min |
| 3 | Chain-of-Thought & Self-Consistency | 25 min |
| 4 | Role Prompting & balises XML | 20 min |
| 5 | Generate Knowledge, Prompt Chaining, Directional Stimulus | 20 min |
| 6 | ReAct & Indice de confiance | 20 min |
| 7 | 5 applications IA / LLM production-ready | 30 min |
| 8 | Anti-patterns & sécurité (prompt injection, fuite de secrets) | 15 min |
| 9 | Bibliothèque de prompts & checklist production | 10 min |
| 10 | Synthèse et transition vers TP3 (RAG) | 5 min |

> **Domaine d'application** : tous les exemples sont orientés **ingénierie IA** — sélection de modèles, fine-tuning (LoRA / QLoRA), RAG, évaluation, MLOps, AI safety, red-teaming. Les patterns se transposent à d'autres domaines (santé, juridique, retail, support technique, etc.).

---

## Stack technique

| Outil | Rôle |
|---|---|
| **Python 3.10+** + Jupyter | Environnement d'exécution |
| **`openai` SDK** | Client API (compatible Groq, OpenAI, Azure OpenAI, Mistral, Anthropic) |
| **`llama-3.3-70b-versatile` via Groq** | LLM principal — gratuit (free tier), ultra-rapide (LPU), 70B paramètres |
| **`llama-3.1-8b-instant` via Groq** | LLM rapide pour Self-Consistency (× N appels) |
| `pandas`, `matplotlib`, `tabulate` | Comparaison et visualisation des sorties |

> **Pourquoi Groq ?** API **gratuite** (free tier), **OpenAI-compatible** (pattern réutilisable avec OpenAI / Azure / Anthropic / Mistral), **inférence ultra-rapide** (LPUs). Modèle utilisé : `llama-3.3-70b-versatile` (excellent suivi d'instructions et JSON, idéal pour l'apprentissage du prompt engineering).

---

## Contenu du dossier

```
02 Prompt Engineering/
├── README.md                          ← ce fichier
├── slides/
│   ├── prompt-engineering.tex         ← source LaTeX (44 slides)
│   └── prompt-engineering.pdf         ← support de cours
└── TP/
    └── tp2-prompt-engineering.ipynb   ← notebook du TP 2 (10 parties)
```

---

## Lancement rapide

```bash
# 1. Créer une clé Groq gratuite : https://console.groq.com
export GROQ_API_KEY="gsk_..."

# 2. Installer les dépendances (cf. cellule pip install au début du notebook)
pip install -q openai pandas matplotlib tabulate

# 3. Lancer Jupyter
jupyter notebook TP/tp2-prompt-engineering.ipynb
```

> ⚠️ **Sécurité** — Ne jamais coller une clé API dans une cellule de code Jupyter. Toujours via `os.environ.get()` après un `export` shell ou un fichier `.env` git-ignoré. Le notebook contient une démo de **masquage de secrets** (`sk-...`, `gsk_...`, `hf_...`, JWT) pour ce risque précis.

---

## Lien avec la suite

Ce module est un **pivot** de la formation :

- **Module 03 — RAG** : le **prompt d'augmentation** RAG (*« réponds UNIQUEMENT à partir du contexte »*) et les garde-fous anti-hallucination sont directement réutilisés. Les techniques **Advanced RAG** (Query Rewriting, Multi-Query, HyDE) sont essentiellement des **patterns de prompts** sur la requête utilisateur.
- **Module 04 — Agents IA** :
  - **TP 4.a (LangChain)** — le pattern **ReAct** vu ici est implémenté nativement par `create_react_agent`. Le system prompt de l'agent reprend tous les patterns du Module 02 (rôle, contraintes, format, garde-fous).
  - **TP 4.b (LangGraph)** — l'**Adaptive RAG** (grade docs / grade answer) repose sur des prompts d'évaluation auto-critique, technique vue dans la partie *Indice de confiance*.
  - **TP 4.c (n8n)** — le node `AI Agent` reprend le même pattern ReAct en no-code, avec des system prompts qu'il faut savoir rédiger.

> *Aujourd'hui : un humain prompte un LLM. Demain : un agent prompte un LLM en boucle. Les bons prompts deviennent l'infrastructure de l'IA.*
