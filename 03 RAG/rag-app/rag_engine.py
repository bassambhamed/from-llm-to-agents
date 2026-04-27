"""
Moteur RAG — version alignée sur le notebook tp3-rag-pipeline-complet.ipynb.

Briques :
  * LangChain pour les loaders et splitters (Document standard, RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter)
  * sentence-transformers pour les embeddings (Bi-encoder) et le reranker (Cross-encoder)
  * ChromaDB (HNSW cosine) + BM25 pour la recherche hybride
  * Groq (API OpenAI-compatible) + llama-3.3-70b-versatile pour la génération

Techniques Advanced RAG exposées :
  * Hybrid + RRF (par défaut)
  * Re-ranking cross-encoder
  * Query Rewriting
  * Multi-Query Retrieval (RRF de N reformulations)
  * HyDE (Hypothetical Document Embeddings)
  * Lost-in-the-middle reorder
  * Contextual Retrieval (préfixage par LLM, à la demande)
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import warnings
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import networkx as nx
from networkx.algorithms.community import greedy_modularity_communities
from sklearn.decomposition import PCA
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from rank_bm25 import BM25Okapi
from openai import OpenAI

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader, WebBaseLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OBJC_DISABLE_INITIALIZE_FORK_SAFETY"] = "YES"
warnings.filterwarnings("ignore")

# ─── Configuration ────────────────────────────────────────────────────────
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
RERANKER_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"
LLM_MODEL = "llama-3.3-70b-versatile"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def _load_model(loader, model_name: str):
    """Charge un modèle HuggingFace : cache local d'abord, puis téléchargement."""
    try:
        os.environ["HF_HUB_OFFLINE"] = "1"
        return loader(model_name)
    except Exception:
        pass
    finally:
        os.environ.pop("HF_HUB_OFFLINE", None)

    try:
        return loader(model_name)
    except Exception as e:
        print(
            f"\n[ERREUR] Impossible de charger le modèle '{model_name}'.\n"
            f"  → {e}\n\n"
            f"  Lancer une fois avec accès internet :\n"
            f"    python -c \"from sentence_transformers import SentenceTransformer, CrossEncoder; "
            f"SentenceTransformer('{EMBED_MODEL_NAME}'); "
            f"CrossEncoder('{RERANKER_MODEL_NAME}')\"\n",
            file=sys.stderr,
        )
        sys.exit(1)


# ─── Data classes pour le graphe de connaissances ────────────────────────
@dataclass
class Entity:
    name: str
    entity_type: str
    description: str = ""


@dataclass
class Relationship:
    source: str
    target: str
    relation: str
    description: str = ""


# ═════════════════════════════════════════════════════════════════════════
class RAGEngine:
    """Pipeline RAG complet : Basic + Advanced + Graph (bonus)."""

    def __init__(self, data_dir: str = "sample_data"):
        self.data_dir = Path(data_dir)

        # Documents et chunks (LangChain Document standard)
        self.documents: List[Document] = []
        self.chunks: List[Document] = []
        self.embeddings: Optional[np.ndarray] = None
        self.chunk_texts: List[str] = []

        # Modèles
        self.embed_model = _load_model(SentenceTransformer, EMBED_MODEL_NAME)
        self.reranker = _load_model(CrossEncoder, RERANKER_MODEL_NAME)

        # Indices
        self.chroma_client = chromadb.Client()
        self.collection = None
        self.bm25_index = None

        # Graph RAG
        self.kg: Optional[nx.DiGraph] = None
        self.communities: List[Dict] = []
        self.all_entities: List[Entity] = []
        self.all_relationships: List[Relationship] = []

        # LLM (Groq, compatible OpenAI)
        self.groq_api_key = os.environ.get("GROQ_API_KEY", "")
        self.api_available = bool(self.groq_api_key) and self.groq_api_key != "VOTRE_CLE_GROQ_ICI"
        self.llm_client: Optional[OpenAI] = None
        if self.api_available:
            try:
                self.llm_client = OpenAI(api_key=self.groq_api_key, base_url=GROQ_BASE_URL)
            except Exception:
                self.api_available = False

        # Splitters LangChain
        self.recursive_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2"), ("###", "h3")],
            strip_headers=False,
        )

        self._ingested = False

    # ─── Ingestion (LangChain loaders) ─────────────────────────────────
    @staticmethod
    def _doc_id(text: str) -> str:
        return hashlib.md5(text[:200].encode()).hexdigest()[:8]

    def load_markdown(self, path: str) -> List[Document]:
        docs = TextLoader(path, encoding="utf-8").load()
        for d in docs:
            d.metadata["format"] = "markdown"
            d.metadata["source"] = Path(path).name
            d.metadata["doc_id"] = self._doc_id(d.page_content)
        return docs

    def load_pdf(self, path: str) -> List[Document]:
        docs = PyPDFLoader(path).load()
        for d in docs:
            d.metadata["format"] = "pdf"
            d.metadata["source"] = Path(path).name
            d.metadata["doc_id"] = self._doc_id(d.page_content)
        return docs

    def load_web(self, url: str) -> List[Document]:
        docs = WebBaseLoader(url).load()
        for d in docs:
            d.metadata["format"] = "web"
            d.metadata["source"] = url
            d.metadata["doc_id"] = self._doc_id(d.page_content)
        return docs

    def ingest_all(self) -> Dict:
        self.documents = []
        for md_file in sorted(self.data_dir.glob("*.md")):
            self.documents.extend(self.load_markdown(str(md_file)))
        for pdf_file in sorted(self.data_dir.glob("*.pdf")):
            self.documents.extend(self.load_pdf(str(pdf_file)))

        self._chunk_documents()
        self._embed_chunks()
        self._build_indices()
        self._build_graph()
        self._ingested = True

        return {
            "documents": len(self.documents),
            "chunks": len(self.chunks),
            "embedding_dim": self.embeddings.shape[1] if self.embeddings is not None else 0,
            "graph_nodes": self.kg.number_of_nodes() if self.kg else 0,
            "graph_edges": self.kg.number_of_edges() if self.kg else 0,
            "communities": len(self.communities),
        }

    # ─── Chunking (LangChain splitters) ─────────────────────────────────
    def _chunk_documents(self):
        out: List[Document] = []
        for doc in self.documents:
            sub_chunks = self.recursive_splitter.split_documents([doc])
            source = doc.metadata.get("source", "doc")
            for i, c in enumerate(sub_chunks):
                seed = f"{source}|{i}|{c.page_content}"
                c.metadata = {
                    **doc.metadata,
                    **c.metadata,
                    "chunk_index": i,
                    "chunk_strategy": self.recursive_splitter.__class__.__name__,
                    "chunk_id": hashlib.md5(seed.encode()).hexdigest()[:10],
                }
            out.extend(sub_chunks)
        self.chunks = out
        self.chunk_texts = [c.page_content for c in self.chunks]

    # ─── Embeddings ────────────────────────────────────────────────────
    def _embed_chunks(self):
        self.embeddings = self.embed_model.encode(
            self.chunk_texts, show_progress_bar=False, normalize_embeddings=True
        )

    # ─── Indices (Chroma + BM25) ───────────────────────────────────────
    @staticmethod
    def _flatten_meta(m: Dict) -> Dict:
        return {k: (v if isinstance(v, (str, int, float, bool)) else str(v))
                for k, v in m.items()}

    def _build_indices(self):
        try:
            self.chroma_client.delete_collection("rag_app")
        except Exception:
            pass

        self.collection = self.chroma_client.create_collection(
            name="rag_app",
            metadata={"hnsw:space": "cosine"},
        )
        self.collection.add(
            ids=[c.metadata["chunk_id"] for c in self.chunks],
            embeddings=self.embeddings.tolist(),
            documents=self.chunk_texts,
            metadatas=[self._flatten_meta(c.metadata) for c in self.chunks],
        )

        tokenized = [t.lower().split() for t in self.chunk_texts]
        self.bm25_index = BM25Okapi(tokenized)

    # ─── Retrieval ─────────────────────────────────────────────────────
    def retrieve_dense(self, query: str, top_k: int = 5) -> List[Dict]:
        query_emb = self.embed_model.encode([query], normalize_embeddings=True).tolist()
        results = self.collection.query(
            query_embeddings=query_emb,
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {"text": doc, "metadata": meta, "score": round(1 - dist, 4), "method": "dense"}
            for doc, meta, dist in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0]
            )
        ]

    def retrieve_sparse(self, query: str, top_k: int = 5) -> List[Dict]:
        scores = self.bm25_index.get_scores(query.lower().split())
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {"text": self.chunks[i].page_content, "metadata": dict(self.chunks[i].metadata),
             "score": round(float(scores[i]), 4), "method": "sparse"}
            for i in top_indices if scores[i] > 0
        ]

    def retrieve_hybrid(self, query: str, top_k: int = 5, rrf_k: int = 60) -> List[Dict]:
        dense_results = self.retrieve_dense(query, top_k=top_k * 2)
        sparse_results = self.retrieve_sparse(query, top_k=top_k * 2)

        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict] = {}

        for rank, r in enumerate(dense_results):
            key = r["text"][:100]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (rrf_k + rank + 1)
            doc_map[key] = r
        for rank, r in enumerate(sparse_results):
            key = r["text"][:100]
            rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (rrf_k + rank + 1)
            doc_map[key] = r

        sorted_keys = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]
        return [
            {**doc_map[k], "score": round(rrf_scores[k], 4), "method": "hybrid"}
            for k in sorted_keys
        ]

    def rerank(self, query: str, results: List[Dict], top_k: int = 3) -> List[Dict]:
        if not results:
            return []
        pairs = [(query, r["text"]) for r in results]
        scores = self.reranker.predict(pairs)
        for r, score in zip(results, scores):
            r["rerank_score"] = round(float(score), 4)
        return sorted(results, key=lambda x: x["rerank_score"], reverse=True)[:top_k]

    @staticmethod
    def reorder_for_attention(ranked: List[Dict]) -> List[Dict]:
        """Lost-in-the-middle proof : best en tête, 2nd best en queue, le reste au milieu."""
        if len(ranked) <= 2:
            return ranked
        head = [ranked[0]]
        tail = [ranked[1]]
        middle = ranked[2:]
        return head + middle + tail

    # ─── LLM (Groq) ────────────────────────────────────────────────────
    def _llm(self, prompt: str, *, temperature: float = 0.1, max_tokens: int = 500,
             json_mode: bool = False) -> str:
        if not self.api_available or self.llm_client is None:
            return ("[Clé GROQ_API_KEY manquante — la génération est désactivée.]\n\n"
                    "Créez une clé gratuite sur https://console.groq.com puis exportez-la "
                    "via `export GROQ_API_KEY=\"gsk_...\"`.")
        try:
            kwargs = {
                "model": LLM_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            resp = self.llm_client.chat.completions.create(**kwargs)
            return resp.choices[0].message.content
        except Exception as e:
            return f"[Échec LLM Groq : {e}]"

    # ─── Advanced RAG ──────────────────────────────────────────────────
    def rewrite_query(self, query: str) -> str:
        prompt = (
            "Tu réécris une requête utilisateur pour qu'elle soit plus efficace en "
            "recherche documentaire. Garde le sens, élimine le bruit conversationnel, "
            "ajoute les termes techniques implicites. Renvoie UNIQUEMENT la requête "
            "réécrite, sans préambule ni guillemets.\n\n"
            f"Requête originale : {query}\n\nRequête réécrite :"
        )
        out = self._llm(prompt, temperature=0.0, max_tokens=80)
        if out.startswith("["):  # erreur
            return query
        return out.strip().strip('"').strip("'")

    def generate_query_variants(self, query: str, n: int = 3) -> List[str]:
        prompt = (
            f"Génère exactement {n} reformulations alternatives de la requête ci-dessous "
            "(synonymes, sous-questions, niveaux d'abstraction). Réponds UNIQUEMENT par "
            "les reformulations, une par ligne, sans numérotation ni préambule.\n\n"
            f"Requête : {query}"
        )
        out = self._llm(prompt, temperature=0.4, max_tokens=200)
        if out.startswith("["):
            return []
        variants = [l.strip(" -•\t") for l in out.strip().split("\n") if l.strip()]
        return variants[:n]

    def retrieve_multi_query(self, query: str, top_k: int = 5,
                             rrf_k: int = 60) -> Tuple[List[Dict], List[str]]:
        variants = [query] + self.generate_query_variants(query, n=3)
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict] = {}
        for v in variants:
            for rank, r in enumerate(self.retrieve_hybrid(v, top_k=top_k * 2)):
                key = r["text"][:100]
                rrf_scores[key] = rrf_scores.get(key, 0) + 1 / (rrf_k + rank + 1)
                doc_map[key] = r
        sorted_keys = sorted(rrf_scores, key=rrf_scores.get, reverse=True)[:top_k]
        results = [{**doc_map[k], "score": round(rrf_scores[k], 4), "method": "multi_query"}
                   for k in sorted_keys]
        return results, variants

    def hyde_retrieve(self, query: str, top_k: int = 5) -> Tuple[List[Dict], str]:
        prompt = (
            "Réponds en 2-3 phrases techniques à la question ci-dessous, comme si tu "
            "écrivais un extrait de documentation. Peu importe l'exactitude.\n\n"
            f"Question : {query}\n\nRéponse :"
        )
        out = self._llm(prompt, temperature=0.3, max_tokens=150)
        hypothetical = query if out.startswith("[") else out.strip()

        hyde_emb = self.embed_model.encode([hypothetical], normalize_embeddings=True).tolist()
        results = self.collection.query(
            query_embeddings=hyde_emb,
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = [
            {"text": doc, "metadata": meta, "score": round(1 - dist, 4), "method": "hyde"}
            for doc, meta, dist in zip(
                results["documents"][0], results["metadatas"][0], results["distances"][0]
            )
        ]
        return docs, hypothetical

    def contextualize_chunk(self, chunk_text: str, parent_text: str) -> str:
        prompt = (
            f"<document>\n{parent_text[:4000]}\n</document>\n\n"
            f"Voici un chunk extrait de ce document :\n<chunk>\n{chunk_text}\n</chunk>\n\n"
            "Donne UNIQUEMENT un court contexte (1-2 phrases, max 50 tokens) qui situe "
            "ce chunk dans le document global. Pas d'introduction."
        )
        out = self._llm(prompt, temperature=0.0, max_tokens=80)
        if out.startswith("["):
            return chunk_text
        return f"[Contexte: {out.strip()}]\n\n{chunk_text}"

    # ─── Prompt construction ───────────────────────────────────────────
    @staticmethod
    def build_rag_prompt(query: str, retrieved: List[Dict]) -> str:
        blocks = []
        for i, c in enumerate(retrieved):
            src = c["metadata"].get("source", "unknown")
            sect = c["metadata"].get("section") or c["metadata"].get("h2") or ""
            tag = f"{src}:{sect}" if sect else src
            blocks.append(f"[Source {i+1}: {tag}]\n{c['text']}")
        ctx = "\n\n---\n\n".join(blocks)

        return (
            "Tu es un assistant expert. Réponds à la question UNIQUEMENT à partir du "
            "contexte fourni.\n\n"
            "Règles :\n"
            "- Réponds UNIQUEMENT à partir du contexte ci-dessous.\n"
            "- Si insuffisant, dis exactement : « Éléments insuffisants dans le contexte fourni. »\n"
            "- Chaque affirmation doit citer au moins une source au format [Source N].\n"
            "- Réponds en français, soigné et concis.\n\n"
            f"Contexte :\n{ctx}\n\nQuestion : {query}\n\nRéponse :"
        )

    # ─── Pipeline complet (Basic + Advanced selon options) ─────────────
    def query(
        self,
        question: str,
        method: str = "hybrid",                  # dense | sparse | hybrid
        top_k: int = 5,
        rerank_top_k: int = 3,
        use_reranking: bool = True,
        use_query_rewriting: bool = False,
        use_multi_query: bool = False,
        use_hyde: bool = False,
        use_lim_reorder: bool = False,
    ) -> Dict:
        if not self._ingested:
            return {"error": "Aucun document indexé. Appelez d'abord /ingest."}

        steps = {}
        effective_query = question

        # 1) Query Rewriting (optionnel)
        if use_query_rewriting:
            rewritten = self.rewrite_query(question)
            steps["rewritten_query"] = rewritten
            effective_query = rewritten

        # 2) Retrieval — la stratégie dépend de l'option Advanced choisie
        variants = None
        hypothetical = None

        if use_hyde:
            retrieved, hypothetical = self.hyde_retrieve(effective_query, top_k=top_k)
            steps["hypothetical_doc"] = hypothetical
            method_used = "hyde"
        elif use_multi_query:
            retrieved, variants = self.retrieve_multi_query(effective_query, top_k=top_k)
            steps["query_variants"] = variants
            method_used = "multi_query"
        else:
            if method == "dense":
                retrieved = self.retrieve_dense(effective_query, top_k=top_k)
            elif method == "sparse":
                retrieved = self.retrieve_sparse(effective_query, top_k=top_k)
            else:
                retrieved = self.retrieve_hybrid(effective_query, top_k=top_k)
            method_used = method

        # 3) Reranking
        if use_reranking and retrieved:
            final_chunks = self.rerank(effective_query, retrieved, top_k=rerank_top_k)
            reranked = True
        else:
            final_chunks = retrieved[:rerank_top_k]
            reranked = False

        # 4) Lost-in-the-middle reorder (sortie finale)
        if use_lim_reorder and len(final_chunks) > 2:
            final_chunks = self.reorder_for_attention(final_chunks)
            steps["lim_reorder"] = True

        # 5) Génération
        prompt = self.build_rag_prompt(effective_query, final_chunks)
        answer = self._llm(prompt, temperature=0.1, max_tokens=600)

        return {
            "query": question,
            "effective_query": effective_query,
            "answer": answer,
            "method_used": method_used,
            "retrieval_method": method,
            "reranked": reranked,
            "advanced": {
                "query_rewriting": use_query_rewriting,
                "multi_query": use_multi_query,
                "hyde": use_hyde,
                "lim_reorder": use_lim_reorder,
                "reranking": use_reranking,
            },
            "steps": steps,
            "sources": [
                {
                    "source": c["metadata"].get("source", ""),
                    "section": c["metadata"].get("section", "") or c["metadata"].get("h2", ""),
                    "chunk_index": c["metadata"].get("chunk_index", ""),
                    "score": c.get("rerank_score", c.get("score", 0)),
                    "rerank_score": c.get("rerank_score"),
                    "text": c["text"][:300] + "..." if len(c["text"]) > 300 else c["text"],
                    "full_text": c["text"],
                }
                for c in final_chunks
            ],
            "prompt_length_words": len(prompt.split()),
        }

    # ─── Graph RAG (extraction LLM avec fallback rules) ────────────────
    @staticmethod
    def _canonicalize_name(name: str) -> str:
        n = name.strip()
        return n if n.isupper() else n.title()

    def _extract_entities_rules(self, text: str) -> Tuple[List[Entity], List[Relationship]]:
        known_entities = {
            "Transformer": "TECHNOLOGY", "BERT": "TECHNOLOGY", "GPT": "TECHNOLOGY",
            "T5": "TECHNOLOGY", "BART": "TECHNOLOGY", "RNN": "TECHNOLOGY",
            "LSTM": "TECHNOLOGY", "LoRA": "METHOD", "QLoRA": "METHOD",
            "RLHF": "METHOD", "DPO": "METHOD", "PPO": "METHOD",
            "RAG": "CONCEPT", "self-attention": "CONCEPT", "cross-attention": "CONCEPT",
            "fine-tuning": "CONCEPT", "embedding": "CONCEPT", "chunking": "CONCEPT",
            "BM25": "METHOD", "HNSW": "METHOD", "RoPE": "METHOD", "ALiBi": "METHOD",
            "hybrid retrieval": "CONCEPT", "reranking": "CONCEPT",
            "ChromaDB": "TECHNOLOGY", "Chroma": "TECHNOLOGY", "FAISS": "TECHNOLOGY",
            "Pinecone": "TECHNOLOGY", "Weaviate": "TECHNOLOGY",
            "Qdrant": "TECHNOLOGY", "Milvus": "TECHNOLOGY",
            "cosine similarity": "METRIC", "Recall@k": "METRIC",
            "MRR": "METRIC", "nDCG": "METRIC", "Faithfulness": "METRIC",
            "Ragas": "FRAMEWORK", "LangChain": "FRAMEWORK",
        }
        known_relations = [
            ("RAG", "embedding", "uses"), ("RAG", "chunking", "uses"),
            ("RAG", "BM25", "uses"), ("RAG", "reranking", "uses"),
            ("Transformer", "self-attention", "uses"),
            ("BERT", "Transformer", "is_a"), ("GPT", "Transformer", "is_a"),
            ("T5", "Transformer", "is_a"),
            ("HNSW", "FAISS", "part_of"), ("LoRA", "fine-tuning", "is_a"),
            ("QLoRA", "LoRA", "improves"), ("DPO", "RLHF", "improves"),
            ("hybrid retrieval", "BM25", "uses"),
            ("hybrid retrieval", "embedding", "uses"),
            ("Ragas", "RAG", "evaluates"),
            ("RoPE", "Transformer", "part_of"),
            ("cross-attention", "Transformer", "part_of"),
        ]
        text_lower = text.lower()
        found = [Entity(n, t) for n, t in known_entities.items() if n.lower() in text_lower]
        names = {e.name.lower() for e in found}
        rels = [Relationship(s, t, r) for s, t, r in known_relations
                if s.lower() in names and t.lower() in names]
        return found, rels

    def _extract_entities_llm(self, text: str) -> Tuple[List[Entity], List[Relationship]]:
        if not self.api_available:
            return self._extract_entities_rules(text)

        prompt = (
            "Extract entities and relationships from the following text. Return a JSON "
            "object with two arrays:\n"
            '- "entities": list of {"name": str, "type": str, "description": str}\n'
            "  Types: TECHNOLOGY, CONCEPT, METHOD, PERSON, METRIC, FRAMEWORK\n"
            '- "relationships": list of {"source": str, "target": str, "relation": str}\n'
            "  Relations: is_a, uses, part_of, improves, compares_to, evaluates, depends_on\n\n"
            f"Text:\n{text[:2000]}\n\n"
            "Return ONLY valid JSON."
        )
        out = self._llm(prompt, temperature=0.0, max_tokens=1500, json_mode=True)
        if out.startswith("["):
            return self._extract_entities_rules(text)
        try:
            content = re.sub(r"```json?\n?", "", out)
            content = re.sub(r"```", "", content)
            data = json.loads(content)
            entities = [Entity(e["name"], e.get("type", "UNKNOWN"), e.get("description", ""))
                        for e in data.get("entities", [])]
            rels = [Relationship(r["source"], r["target"], r["relation"],
                                 r.get("description", ""))
                    for r in data.get("relationships", [])]
            return entities, rels
        except Exception:
            return self._extract_entities_rules(text)

    def _build_graph(self, use_llm: bool = False):
        """Construit le graphe. Par défaut, utilise les règles (rapide, déterministe).
        Passer use_llm=True pour utiliser l'extraction par LLM (lent, plus riche)."""
        self.all_entities = []
        self.all_relationships = []
        extractor = self._extract_entities_llm if use_llm else self._extract_entities_rules
        for doc in self.documents:
            ents, rels = extractor(doc.page_content)
            self.all_entities.extend(ents)
            self.all_relationships.extend(rels)

        G = nx.DiGraph()
        seen = set()
        for e in self.all_entities:
            n = self._canonicalize_name(e.name)
            if n.lower() not in seen:
                G.add_node(n, type=e.entity_type, description=e.description)
                seen.add(n.lower())
        for r in self.all_relationships:
            s = self._canonicalize_name(r.source)
            t = self._canonicalize_name(r.target)
            if s.lower() in seen and t.lower() in seen:
                G.add_edge(s, t, relation=r.relation, description=r.description)
        self.kg = G

        if G.number_of_nodes() > 0:
            comms = list(greedy_modularity_communities(G.to_undirected()))
            self.communities = []
            for i, comm in enumerate(comms):
                self.communities.append({
                    "community_id": i,
                    "entities": sorted(comm),
                    "summary": self._summarize_community(comm),
                })

    def _summarize_community(self, community: set) -> str:
        ents = [f"- {n} ({self.kg.nodes[n].get('type', 'UNKNOWN')})" for n in community]
        rels = [f"- {u} --[{d['relation']}]--> {v}"
                for u, v, d in self.kg.edges(data=True)
                if u in community and v in community]
        s = f"Communauté de {len(community)} entités :\nEntités :\n" + "\n".join(ents)
        if rels:
            s += "\nRelations :\n" + "\n".join(rels)
        return s

    def find_anchor_entities(self, query: str, threshold: float = 0.4) -> List[Tuple[str, float]]:
        if not self.kg or self.kg.number_of_nodes() == 0:
            return []
        q_emb = self.embed_model.encode([query], normalize_embeddings=True)
        names = list(self.kg.nodes())
        n_emb = self.embed_model.encode(names, normalize_embeddings=True)
        sims = np.dot(q_emb, n_emb.T)[0]
        anchors = [(names[i], float(sims[i])) for i in range(len(names)) if sims[i] > threshold]
        anchors.sort(key=lambda x: -x[1])
        return anchors

    def retrieve_local_graph(self, query: str, hops: int = 2,
                             max_entities: int = 5) -> Dict:
        anchors = self.find_anchor_entities(query)
        if not anchors:
            return {"entities": [], "triples": [], "context": "Aucune entité pertinente."}
        relevant = set()
        for name, _ in anchors[:max_entities]:
            if name in self.kg:
                relevant.add(name)
                for _ in range(hops):
                    nbrs = set()
                    for n in relevant:
                        nbrs.update(self.kg.successors(n))
                        nbrs.update(self.kg.predecessors(n))
                    relevant.update(nbrs)
        triples = [{"source": u, "relation": d["relation"], "target": v}
                   for u, v, d in self.kg.edges(data=True)
                   if u in relevant and v in relevant]
        ctx = [f"Entités : {', '.join(sorted(relevant))}", "\nRelations :"]
        ctx += [f"  - {t['source']} --[{t['relation']}]--> {t['target']}" for t in triples]
        return {
            "entities": sorted(relevant),
            "triples": triples,
            "anchors": [(a, round(s, 3)) for a, s in anchors[:max_entities]],
            "context": "\n".join(ctx),
        }

    def retrieve_global_graph(self, query: str, top_k: int = 2) -> Dict:
        if not self.communities:
            return {"communities": [], "context": "Aucune communauté détectée."}
        q_emb = self.embed_model.encode([query], normalize_embeddings=True)
        s_emb = self.embed_model.encode([c["summary"] for c in self.communities],
                                        normalize_embeddings=True)
        sims = np.dot(q_emb, s_emb.T)[0]
        idxs = np.argsort(sims)[::-1][:top_k]
        rel = []
        for i in idxs:
            rel.append({
                "community_id": self.communities[i]["community_id"],
                "similarity": round(float(sims[i]), 3),
                "summary": self.communities[i]["summary"],
                "entities": self.communities[i]["entities"],
            })
        ctx = "\n\n".join(f"[Communauté {c['community_id']+1}]\n{c['summary']}" for c in rel)
        return {"communities": rel, "context": ctx}

    def query_graph_rag(self, question: str, top_k_vector: int = 3) -> Dict:
        if not self._ingested:
            return {"error": "Aucun document indexé."}
        local = self.retrieve_local_graph(question)
        glob = self.retrieve_global_graph(question, top_k=2)
        vec = self.retrieve_hybrid(question, top_k=top_k_vector)
        vec_reranked = self.rerank(question, vec, top_k=top_k_vector)

        graph_ctx = (
            "=== Contexte du graphe de connaissances ===\n"
            f"{local['context']}\n\n"
            "=== Résumés des communautés ===\n"
            f"{glob['context']}"
        )
        vec_ctx = "\n\n---\n\n".join(
            f"[Chunk issu de {r['metadata'].get('source', '?')}]\n{r['text']}"
            for r in vec_reranked
        )

        prompt = (
            "Tu es un assistant expert ayant accès à un graphe de connaissances et à "
            "des chunks de documents. Réponds en français, ancre chaque affirmation "
            "sur le contexte (graphe ou chunk).\n\n"
            f"{graph_ctx}\n\n=== Chunks ===\n{vec_ctx}\n\n"
            f"Question : {question}\n\nRéponse :"
        )
        answer = self._llm(prompt, temperature=0.1, max_tokens=600)

        return {
            "query": question,
            "answer": answer,
            "graph_entities": local["entities"],
            "graph_triples": local["triples"],
            "communities_used": len(glob.get("communities", [])),
            "vector_chunks": len(vec_reranked),
            "method": "graph_rag",
            "sources": [
                {
                    "source": r["metadata"].get("source", ""),
                    "section": r["metadata"].get("section", "") or r["metadata"].get("h2", ""),
                    "score": r.get("rerank_score", r.get("score", 0)),
                    "text": r["text"][:300] + "..." if len(r["text"]) > 300 else r["text"],
                }
                for r in vec_reranked
            ],
        }

    # ─── Données pour le dashboard ─────────────────────────────────────
    def get_embeddings_pca(self, n_components: int = 2) -> Dict:
        if self.embeddings is None:
            return {"error": "Aucun embedding."}
        pca = PCA(n_components=n_components, random_state=42)
        coords = pca.fit_transform(self.embeddings)
        points = []
        for i, c in enumerate(self.chunks):
            points.append({
                "x": round(float(coords[i, 0]), 4),
                "y": round(float(coords[i, 1]), 4),
                "source": c.metadata.get("source", "unknown"),
                "section": c.metadata.get("section", "") or c.metadata.get("h2", ""),
                "text_preview": c.page_content[:120],
            })
        return {
            "points": points,
            "explained_variance": [round(float(v), 4) for v in pca.explained_variance_ratio_],
            "n_chunks": len(self.chunks),
            "embedding_dim": int(self.embeddings.shape[1]),
        }

    def get_embeddings_pca_3d(self) -> Dict:
        if self.embeddings is None:
            return {"error": "Aucun embedding."}
        pca = PCA(n_components=3, random_state=42)
        coords = pca.fit_transform(self.embeddings)
        points = []
        for i, c in enumerate(self.chunks):
            points.append({
                "x": round(float(coords[i, 0]), 4),
                "y": round(float(coords[i, 1]), 4),
                "z": round(float(coords[i, 2]), 4),
                "source": c.metadata.get("source", "unknown"),
                "section": c.metadata.get("section", "") or c.metadata.get("h2", ""),
                "text_preview": c.page_content[:120],
            })
        return {
            "points": points,
            "explained_variance": [round(float(v), 4) for v in pca.explained_variance_ratio_],
        }

    def get_graph_data(self) -> Dict:
        if not self.kg:
            return {"error": "Aucun graphe."}
        nodes = [{"id": n, "type": d.get("type", "UNKNOWN"), "degree": self.kg.degree(n)}
                 for n, d in self.kg.nodes(data=True)]
        edges = [{"source": u, "target": v, "relation": d.get("relation", "")}
                 for u, v, d in self.kg.edges(data=True)]
        type_counts: Dict[str, int] = {}
        for n in nodes:
            type_counts[n["type"]] = type_counts.get(n["type"], 0) + 1
        return {
            "nodes": nodes,
            "edges": edges,
            "type_counts": type_counts,
            "communities": [
                {"id": c["community_id"], "entities": c["entities"], "size": len(c["entities"])}
                for c in self.communities
            ],
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        }

    def get_stats(self) -> Dict:
        return {
            "ingested": self._ingested,
            "documents": len(self.documents),
            "chunks": len(self.chunks),
            "embedding_dim": int(self.embeddings.shape[1]) if self.embeddings is not None else 0,
            "graph_nodes": self.kg.number_of_nodes() if self.kg else 0,
            "graph_edges": self.kg.number_of_edges() if self.kg else 0,
            "communities": len(self.communities),
            "llm_model": LLM_MODEL,
            "llm_provider": "Groq",
            "api_available": self.api_available,
            "embed_model": EMBED_MODEL_NAME,
            "reranker_model": RERANKER_MODEL_NAME,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
        }

    def evaluate_retrieval(self) -> Dict:
        golden_set = [
            {"query": "Qu'est-ce que le self-attention dans les Transformers ?",
             "expected_source": "transformers.md"},
            {"query": "Quelles stratégies de chunking existent en RAG ?",
             "expected_source": "rag_systems.md"},
            {"query": "Qu'est-ce que le fine-tuning LoRA ?",
             "expected_source": "finetuning.md"},
            {"query": "Comment fonctionne l'indexation HNSW ?",
             "expected_source": "vector_databases.md"},
            {"query": "Quels sont les bénéfices du retrieval hybride ?",
             "expected_source": "rag_systems.md"},
            {"query": "Qu'est-ce que le DPO dans l'alignement des LLM ?",
             "expected_source": "finetuning.md"},
        ]
        methods = {
            "Dense": self.retrieve_dense,
            "Sparse (BM25)": self.retrieve_sparse,
            "Hybrid (RRF)": self.retrieve_hybrid,
        }
        results: Dict[str, Dict[str, float]] = {}
        for name, fn in methods.items():
            hits, mrrs = [], []
            for item in golden_set:
                retrieved = fn(item["query"], top_k=5)
                sources = [r["metadata"].get("source", "") for r in retrieved]
                hits.append(1 if item["expected_source"] in sources else 0)
                try:
                    rank = sources.index(item["expected_source"]) + 1
                    mrrs.append(1.0 / rank)
                except ValueError:
                    mrrs.append(0.0)
            results[name] = {
                "hit_rate": round(float(np.mean(hits)), 3),
                "mrr": round(float(np.mean(mrrs)), 3),
            }
        return {"methods": results, "golden_set_size": len(golden_set)}
