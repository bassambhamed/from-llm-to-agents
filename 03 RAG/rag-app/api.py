"""
Backend FastAPI — API de l'application RAG.

Expose les endpoints de :
  - indexation (/ingest)
  - requêtage RAG simple et avec techniques Advanced RAG (Query Rewriting,
    Multi-Query, HyDE, Lost-in-the-middle reorder, reranking)
  - prévisualisation des transformations (/preview/rewrite, /preview/multi-query, /preview/hyde)
  - Graph RAG (/query/graph)
  - données pour le tableau de bord (PCA, graphe, évaluation)
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from rag_engine import RAGEngine

# ─── Instance globale ──────────────────────────────────────────────────────

engine = RAGEngine(data_dir="sample_data")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Indexation automatique au démarrage."""
    result = engine.ingest_all()
    print(f"[démarrage] Indexation : {result}")
    yield


app = FastAPI(
    title="API Pipeline RAG — TP 3",
    description=(
        "Système RAG complet : Basic RAG + Advanced RAG (Query Rewriting, "
        "Multi-Query, HyDE, Lost-in-the-middle) + Graph RAG (bonus). "
        "LLM : llama-3.3-70b-versatile via Groq."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Modèles ───────────────────────────────────────────────────────────────


class QueryRequest(BaseModel):
    question: str
    method: str = Field(default="hybrid", description="dense | sparse | hybrid")
    top_k: int = Field(default=5, ge=1, le=20)
    rerank_top_k: int = Field(default=3, ge=1, le=10)
    use_reranking: bool = True
    # Advanced RAG (toggles)
    use_query_rewriting: bool = False
    use_multi_query: bool = False
    use_hyde: bool = False
    use_lim_reorder: bool = False


class GraphQueryRequest(BaseModel):
    question: str
    top_k_vector: int = Field(default=3, ge=1, le=10)


class TextRequest(BaseModel):
    text: str


# ─── Endpoints ─────────────────────────────────────────────────────────────


@app.get("/")
def root():
    return {"status": "ok", "message": "API Pipeline RAG — TP 3 (v2)"}


@app.post("/ingest")
def ingest():
    """Ré-indexe tous les documents du dossier sample_data/."""
    result = engine.ingest_all()
    return {"status": "ok", **result}


@app.post("/query")
def query(req: QueryRequest):
    """Requête RAG complète avec toggles Advanced RAG.

    Combinaisons exclusives au niveau du retrieval : si `use_hyde` est vrai, il
    prime ; sinon `use_multi_query` ; sinon `method` (dense/sparse/hybrid).
    `use_query_rewriting`, `use_reranking`, `use_lim_reorder` s'appliquent en plus.
    """
    return engine.query(
        question=req.question,
        method=req.method,
        top_k=req.top_k,
        rerank_top_k=req.rerank_top_k,
        use_reranking=req.use_reranking,
        use_query_rewriting=req.use_query_rewriting,
        use_multi_query=req.use_multi_query,
        use_hyde=req.use_hyde,
        use_lim_reorder=req.use_lim_reorder,
    )


@app.post("/preview/rewrite")
def preview_rewrite(req: TextRequest):
    """Prévisualise la requête réécrite par le LLM (sans retrieval)."""
    return {"original": req.text, "rewritten": engine.rewrite_query(req.text)}


@app.post("/preview/multi-query")
def preview_multi_query(req: TextRequest):
    """Prévisualise les N reformulations générées (sans retrieval)."""
    variants = engine.generate_query_variants(req.text, n=3)
    return {"original": req.text, "variants": variants}


@app.post("/preview/hyde")
def preview_hyde(req: TextRequest):
    """Prévisualise la réponse hypothétique générée pour HyDE (sans retrieval)."""
    prompt = (
        "Réponds en 2-3 phrases techniques à la question ci-dessous, comme si tu "
        "écrivais un extrait de documentation.\n\n"
        f"Question : {req.text}\n\nRéponse :"
    )
    out = engine._llm(prompt, temperature=0.3, max_tokens=150)
    return {"original": req.text, "hypothetical_doc": out}


@app.post("/query/graph")
def query_graph(req: GraphQueryRequest):
    """Graph RAG (graphe de connaissances + retrieval vectoriel)."""
    return engine.query_graph_rag(question=req.question, top_k_vector=req.top_k_vector)


@app.get("/embeddings")
def get_embeddings():
    """Projection PCA 2D des embeddings."""
    return engine.get_embeddings_pca()


@app.get("/embeddings/3d")
def get_embeddings_3d():
    """Projection PCA 3D des embeddings."""
    return engine.get_embeddings_pca_3d()


@app.get("/graph")
def get_graph():
    """Données du graphe de connaissances (nœuds, arêtes, communautés)."""
    return engine.get_graph_data()


@app.get("/stats")
def get_stats():
    """Statistiques système (modèles utilisés, état d'indexation, dispo API)."""
    return engine.get_stats()


@app.get("/evaluate")
def evaluate():
    """Évaluation Hit@5 / MRR sur le golden set."""
    return engine.evaluate_retrieval()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
