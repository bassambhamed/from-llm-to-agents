# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

This is a **3-day intensive training course** (18 h) designed by Bassem Ben Hamed for DATA engineering teams (BI, Data Engineering & Operations). The course covers:

- **LLM fundamentals** — tokenisation, transformers (vulgarized), API/HuggingFace usage
- **Prompt Engineering** — from basics to advanced (Zero/Few-Shot, CoT, Self-Consistency, ReAct)
- **RAG** — both **Vector RAG** and **Graph RAG**, with comparison on the same corpus
- **AI Agents** design, tool-use, and workflow integration
- **Automation orchestration** — Microsoft Power Automate (free tier) + n8n (self-hosted agent runtime)

**Target audience:** DATA engineers with solid SQL/Power Query knowledge and general Microsoft 365 familiarity.
**Delivery:** French language, presentiel or remote, 8–12 participants. TP 1–3 = Python notebooks + API keys. TP 4.a = browser (M365 institutional account suffices). TP 4.b = Docker Desktop + browser.

## Course Structure (Revised)

Progression: `IA générative → LLMs → Prompt Engineering → RAG (Vector + Graph) → Agents IA + Automatisation`

| Day | Focus | TP |
|-----|-------|----|
| Day 1 | Intro IA, LLMs, Prompt Engineering | **TP1** LLM via API / HuggingFace · **TP2** Prompt Engineering (basique → avancé) |
| Day 2 | RAG principles, Vector vs Graph RAG | **TP3** Vector RAG + Graph RAG on same corpus |
| Day 3 | Agents IA architecture, integration patterns | **TP4.a** Workflow gratuit Power Automate (règles) · **TP4.b** Migration vers agent IA n8n (RAG + tool-use) |

**No fil rouge project** — the course is structured around hands-on TPs, not an end-to-end capstone.
**TP 4 is split in two complementary parts** — 4.a first to constitute a free baseline accessible to any institutional M365 account, then 4.b to demonstrate the value added by an AI agent by contrast.
**Common TP 4 case study:** *Assistant Support IT* — ticket triage. Neutral and universal (not banking-specific). Same scenario in 4.a and 4.b for direct comparison.

**Final deliverables per participant:**
- TP 1–3 Python notebooks, versioned
- TP 4.a : MS Forms + SharePoint list + active Power Automate flow + observed-limits fiche
- TP 4.b : Docker stack (`docker-compose.yml`) + exported n8n workflow JSON + Qdrant KB + Postgres journal + comparative table 4.a↔4.b
- Annotated and versioned prompt library

## Materials to Produce

When creating course materials, target these artifact types:

- **Hands-on lab guides (TP1–TP4):** step-by-step instructions
  - TP1–TP3 may use Python notebooks, API keys (OpenAI/Azure OpenAI), or HuggingFace Inference API
  - TP4.a is browser-only (make.powerautomate.com + Microsoft Forms + SharePoint + Teams + Outlook) — works on any institutional M365 account, no Premium licensing required
  - TP4.b is Docker-based (n8n self-hosted + Postgres + Qdrant) + OpenAI API + OAuth Microsoft Graph for M365 connectors
- **Prompt templates:** reusable, versioned, annotated with role/context/instructions/constraints/examples structure
- **RAG reference implementations:** Vector RAG (embeddings + vector store) and Graph RAG (entity/relation extraction + knowledge graph)
- **Flow diagrams / architecture schemas:** illustrating the two TP 4 variants and their migration delta
- **Evaluation rubrics:** prompt quality, RAG choice pertinence, triage quality (rules vs agent), robustness, documented 4.a↔4.b comparison

## Key Technical Stack

**LLM layer (TP 1–3):**
- OpenAI / Azure OpenAI API — primary for API-based labs
- HuggingFace Hub + Inference API — open-source models (Mistral, Llama)
- Vector stores — Azure AI Search, or LangChain/LlamaIndex equivalents (FAISS, Chroma)
- Graph RAG tooling — Microsoft GraphRAG, Neo4j, or LangChain graph retrievers

**TP 4.a — workflow baseline (free, institutional M365):**
- **Microsoft Forms** — ticket intake
- **Power Automate** (standard connectors only — no Premium, no HTTP, no Dataverse)
- **SharePoint list** — ticket storage
- **Teams + Outlook** — notifications

**TP 4.b — AI agent runtime (self-hosted, ~2 $/month):**
- **n8n** (self-hosted via Docker) — orchestrator with built-in AI Agent node (LangChain-based)
- **OpenAI API** — `gpt-4o-mini` + `text-embedding-3-small` (Ollama as offline alternative)
- **Qdrant** — vector store for the knowledge base (Chroma as embedded alternative)
- **Postgres** — n8n metadata DB + `journal_agent` table (audit log)
- **Microsoft Graph OAuth** — SharePoint / Teams / Outlook connectors (works on institutional M365 without Premium)
- **Docker Compose** — entire stack in one file

**Pricing baseline (2026) referenced in TP 4.a README and slides:**
- Power Automate per user ≈ 15 €/u/mo · Copilot Studio ≈ 200 $/tenant/mo · AI Builder credits ≈ 500 €/mo
- Full Microsoft stack for 11 users ≈ 450 €/mo
- n8n self-hosted equivalent ≈ 2 $/mo (OpenAI usage only)
- This 225× cost delta is the core of the economic justification discussed in Day 3

## Architecture Patterns Taught

### TP 4.a — workflow-first (no AI)
```
Microsoft Forms → Power Automate (trigger)
                    → Switch (rule-based keyword matching)
                    → SharePoint + Teams + Outlook
                    → Scope CATCH → Teams #oncall
```

### TP 4.b — agent-first (AI inside the workflow)
```
Form Trigger (n8n) → AI Agent node
                       ├─ tool: rag_search  (Qdrant)
                       ├─ tool: lookup_user (HTTP)
                       └─ tool: log_decision (Postgres)
                     → SharePoint + Teams + Outlook (OAuth Graph)
                     → Error Trigger (separate workflow)
```

### Migration delta (what changes between 4.a and 4.b)
- Trigger : MS Forms → n8n Form Trigger (or webhook)
- Classification : `contains(keyword)` Switch → **AI Agent** (LLM + RAG)
- Actions downstream (SharePoint, Teams, mail) : unchanged conceptually, just re-expressed via OAuth Graph connectors in n8n
- Logging : SharePoint list → Postgres table (exploitable via Metabase/Grafana)
- Multi-language, injection resistance, confidence score : only present in 4.b

## Core Concepts Covered

LLM mechanics (tokenisation, attention, generation), prompt engineering patterns, RAG strategies (Vector vs Graph — when to pick which), context window management, agent anatomy (system prompt + planner + memory + tools), tool-use and ReAct, DLP governance, GDPR compliance, error handling (try/catch + Teams notifications), cost/governance trade-off between Power Automate (M365 governance, DLP, audit) and n8n (portability, cost, transparency).

## Repository Layout Convention

```
<RepoRoot>/
├── CLAUDE.md                     ← this file
├── plan.md                       ← overall course plan (3 days, 4 TPs)
├── Fondamentaux LLM/             ← Day 1 – slides + TP 1 notebook
├── Prompt Engineering/           ← Day 1 – slides + TP 2 notebook + guide PDF
├── RAG/                          ← Day 2 – slides + TP 3 notebook + rag-app
└── Agents IA/                    ← Day 3
    ├── plan.md                   ← Day 3 detailed plan
    ├── QUICKSTART.md             ← 3-hour minute-by-minute runbook for TP 4
    ├── présentation/agents.tex   ← Beamer slides (compiles to agents.pdf)
    ├── TP4-a-PowerAutomate/      ← free baseline deliverable
    │   ├── README.md · SETUP.md · TESTS.md
    │   └── assets/ (forms-schema, rules-dictionary)
    └── TP4-b-n8n/                ← AI-enriched deliverable
        ├── README.md · SETUP.md · MIGRATION.md · TESTS.md
        └── assets/ (docker-compose.yml, init-db.sql, system-prompt, knowledge-base, workflow.json, ingest-kb)
```
