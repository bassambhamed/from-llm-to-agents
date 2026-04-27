# Module 01 — Fondamentaux LLM

**Jour 1 · Partie 1 · 3 h (cours) + 3 h (TP 1)**

Premier module de la formation *IA générative · LLMs · Prompt Engineering · RAG · Agents IA & Automatisation*. Il pose les bases conceptuelles et pratiques nécessaires à toute la suite du parcours : sans une compréhension claire de ce qu'est un LLM (tokenisation, embeddings, attention, génération), ni le **Prompt Engineering** (Module 02), ni le **RAG** (Module 03), ni les **Agents IA** (Module 04) ne peuvent être maîtrisés.

---

## Public & prérequis

- **Cible** : ingénieurs DATA, data scientists, développeurs IA, profils techniques découvrant les LLMs.
- **Prérequis** : Python de base (lecture d'un notebook), notion d'API REST.
- **Aucune connaissance préalable en ML / NLP n'est exigée** — les concepts sont vulgarisés et illustrés pas-à-pas.
- **Matériel** :
  - Python 3.10+ avec Jupyter (local ou Colab).
  - **Clé API Groq** (gratuite, free tier) — création en 30 secondes sur **https://console.groq.com**.
  - ~2 Go d'espace disque pour télécharger les petits modèles HuggingFace (SmolLM2, Qwen2.5).

---

## Objectifs pédagogiques

À l'issue du module, le participant est capable de :

1. **Situer** l'IA générative dans le paysage IA (discriminatif vs génératif, multimodal) et citer les grands acteurs LLM (GPT-4o, Claude 4.x, Gemini 2.x, Llama 3.x, Mistral, Phi-4) avec leurs critères de choix (coût, latence, contexte, conformité).
2. **Expliquer pas à pas** comment un Transformer produit du texte : embeddings de tokens → encodage positionnel → encodeur (scaled dot-product attention, multi-head attention, FFN, Add & Norm) → décodeur (masked self-attention, cross-attention, FFN).
3. **Manipuler** la tokenisation (BPE, WordPiece, SentencePiece), comparer les tokenizers, mesurer le coût en tokens par langue.
4. **Extraire et interpréter** les embeddings d'un LLM et d'un sentence-transformer (similarité cosinus, projection PCA, arithmétique vectorielle).
5. **Maîtriser** les stratégies de décodage : greedy, sampling, beam search, température, top-k, top-p, repetition penalty.
6. **Appeler un grand modèle via API** (Groq, compatible OpenAI) et le **comparer** aux modèles locaux sur 6 cas d'usage (résumé, classification, traduction, extraction JSON, génération SQL, reformulation).
7. **Évaluer** les modèles selon qualité, coût, latence et **choisir** le bon outil pour chaque tâche.

---

## Contenu

### Cours — 3 h (slides : `slides/fondamentaux-llm.pdf` — 33 pages)

Le support couvre **2 parties** :

| Partie | Contenu clé |
|---|---|
| **1 — Introduction à l'IA générative** | Panorama IA / ML / DL / NLP / LLM, types d'apprentissage (supervisé, non supervisé, RL), IA discriminative vs IA générative, cas d'usage IA (CNN, NLP, ML tabulaire) puis génératifs (LLM seul, RAG, agents, fine-tuning), métriques (accuracy / F1 vs BLEU / ROUGE / perplexité), historique 70 ans en 1 slide, écosystème LLM 2026 |
| **2 — Le Transformer pas à pas** *(fil rouge : « je suis étudiant » → « I am a student »)* | Tokenisation (BPE), Architecture Encodeur–Décodeur (RNN → Transformer), **vue d'ensemble du Transformer** (image *Vaswani 2017*), puis **7 étapes détaillées** : Embeddings de tokens → Encodage positionnel → Scaled Dot-Product Attention → Multi-Head Attention (interprétation des têtes) → FFN + Add & Norm (bloc encodeur) → Masked Self-Attention (décodeur) → Cross-Attention + FFN + Add & Norm (décodeur). Suivi de la prédiction token-par-token, températures, top-k/top-p, fenêtre de contexte, limites structurelles. |

### TP 1 — Fondamentaux des LLM : de la tokenisation aux cas d'usage (3 h)

Notebook : **`TP/tp1-llm-fondamentaux.ipynb`** (7 parties, 85 cellules)

| Partie | Sujet | Durée |
|---|---|---|
| 0 | Mise en place (libs, config, **clé API Groq**) | 10 min |
| 1 | Panorama des modèles : 3 modèles locaux (SmolLM2-135M, Qwen2.5-0.5B, Qwen2.5-1.5B) + 1 API (Llama 3.3 70B via Groq) | 15 min |
| 2 | Tokenisation en profondeur — comparaison côte-à-côte, multi-langue, cas pathologiques (URL, tokens API, hash, JSON), visualisation colorée, estimation du coût | 25 min |
| 3 | Embeddings — extraction de la matrice d'embedding, similarité cosinus, **PCA sur vocab IA / ML**, sentence-transformers (paraphrases techniques), arithmétique vectorielle (`encoder à BERT comme decoder à ?`) | 25 min |
| 4 | Génération & stratégies de décodage — greedy / sampling / beam, sweep de température, visualisation top-k, entropie, repetition penalty | 20 min |
| 5 | **6 cas d'usage IA / LLM / RAG / dev** : (1) résumé d'un rapport technique, (2) classification de tickets plateforme IA (BUG/FEATURE/PERF/DOCS/QUESTION), (3) traduction phrases techniques, (4) extraction JSON depuis un bug report, (5) génération SQL sur schema MLOps (models / benchmarks / inferences), (6) reformulation d'une annonce de dépréciation API | 35 min |
| 6 | Évaluation comparative — perplexité, benchmark vitesse (tokens/s), grille de recommandation | 15 min |
| 7 | Synthèse et transition vers TP2 (Prompt Engineering) | 5 min |

> **Domaine d'application** : tous les exemples sont orientés **ingénierie IA / ML** (Transformer, fine-tuning, RAG, agents, MLOps). Les patterns se transposent à d'autres domaines (santé, juridique, retail, support technique).

---

## Stack technique

| Outil | Rôle |
|---|---|
| **Python 3.10+** + Jupyter | Environnement d'exécution |
| **`transformers` + `torch`** | Modèles locaux HuggingFace (SmolLM2-135M, Qwen2.5-0.5B, Qwen2.5-1.5B) |
| **`sentence-transformers`** | Sentence embeddings multilingues (paraphrases) |
| **`tiktoken`** | Tokenizer pour estimation de coût |
| **`openai` SDK** | Client API (compatible Groq, OpenAI, Azure, Mistral, Anthropic) |
| **`llama-3.3-70b-versatile` via Groq** | LLM principal — gratuit (free tier), ultra-rapide (LPU) |
| `pandas`, `matplotlib`, `seaborn`, `scikit-learn` | Comparaison, visualisation, PCA |

> **Pourquoi Groq ?** API **gratuite** (free tier généreux), **OpenAI-compatible** (pattern réutilisable avec OpenAI / Azure / Anthropic / Mistral), **inférence ultra-rapide** (LPUs). Modèle utilisé : `llama-3.3-70b-versatile` (70B paramètres, excellent suivi d'instructions et JSON).

---

## Contenu du dossier

```
01 Fondamentaux LLM/
├── README.md                          ← ce fichier
├── slides/
│   ├── fondamentaux-llm.tex           ← source LaTeX (33 slides)
│   ├── fondamentaux-llm.pdf           ← support de cours
│   ├── transformer.png                ← schéma Vaswani 2017 inséré dans les slides
│   └── tutoriel_transformer.tex       ← tutoriel détaillé pas-à-pas (annexe formateur)
└── TP/
    └── tp1-llm-fondamentaux.ipynb     ← notebook du TP 1 (7 parties)
```

---

## Lancement rapide

```bash
# 1. Créer une clé Groq gratuite : https://console.groq.com
export GROQ_API_KEY="gsk_..."

# 2. Installer les dépendances (cf. cellule pip install au début du notebook)
pip install -q transformers accelerate torch sentencepiece protobuf
pip install -q sentence-transformers scikit-learn
pip install -q openai tiktoken
pip install -q matplotlib seaborn pandas numpy

# 3. Lancer Jupyter
jupyter notebook TP/tp1-llm-fondamentaux.ipynb
```

> ⚠️ **Sécurité** — Ne jamais coller une clé API dans une cellule de code Jupyter. Toujours via `os.environ.get()` après un `export` shell ou un fichier `.env` git-ignoré. Le TP2 contient une démo de **masquage de secrets** pour ce risque précis.

---

## Lien avec la suite

Ce module alimente directement les trois suivants :

- **Module 02 — Prompt Engineering** : les helpers `chat()` / `generate_*()` du TP 1 sont réutilisés au TP 2 ; les notions de tokenisation et de décodage sous-tendent toutes les techniques (Zero-Shot / Few-Shot / CoT / Self-Consistency / ReAct).
- **Module 03 — RAG** : la notion d'**embeddings** (introduite ici via `sentence-transformers`) est au cœur du retrieval. Le pattern de **similarité cosinus** vu en § 3.2/3.4 est exactement celui utilisé par Chroma / FAISS / Qdrant.
- **Module 04 — Agents IA** : les paramètres de génération (température, top-p), le **client OpenAI-compatible**, et la notion de "modèle comme outil" sont repris dans l'architecture agent (LangChain ReAct, LangGraph Adaptive RAG, n8n no-code).

> *Aujourd'hui : on appelle un LLM. Demain : on prompte mieux. Après-demain : on l'ancre sur des données. Au final : on l'orchestre dans un agent.*
