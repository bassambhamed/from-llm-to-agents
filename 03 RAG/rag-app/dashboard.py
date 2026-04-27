"""
Tableau de bord Streamlit — Application RAG (TP 3).

Pages :
  - 💬 Chat : RAG Vectoriel + Advanced RAG (Query Rewriting, Multi-Query, HyDE, LIM reorder)
              avec menus déroulants pour configurer la stratégie.
  - 🧪 Comparateur de techniques : exécute la même question avec/sans chaque technique
              et compare les réponses + chunks sources.
  - 🕸️ Graph RAG : mode dédié (entités + relations + communautés).
  - 📊 Embeddings : projection PCA 2D/3D.
  - 🌐 Graphe : visualisation interactive du knowledge graph.
  - 📈 Évaluation : Hit Rate / MRR sur le golden set.
"""

import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx

API_URL = "http://localhost:8000"

# ─── Configuration de la page ──────────────────────────────────────────────

st.set_page_config(
    page_title="TP 3 — RAG Pipeline complet",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ───────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00539C;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    .technique-pill {
        display: inline-block;
        background: #e8f4f8;
        color: #00539C;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 4px;
    }
    .technique-pill-active {
        background: #27AE60;
        color: white;
    }
    .step-card {
        background: #fafafa;
        border-left: 3px solid #00539C;
        padding: 0.6rem 0.8rem;
        margin: 0.3rem 0;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helpers HTTP ──────────────────────────────────────────────────────────

def api_get(endpoint: str):
    try:
        r = requests.get(f"{API_URL}{endpoint}", timeout=60)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre l'API (FastAPI sur le port 8000).")
        return None
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None


def api_post(endpoint: str, data: dict):
    try:
        r = requests.post(f"{API_URL}{endpoint}", json=data, timeout=180)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("Impossible de joindre l'API (FastAPI sur le port 8000).")
        return None
    except Exception as e:
        st.error(f"Erreur API : {e}")
        return None


# ─── Sidebar ───────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## TP 3 — RAG")
    st.caption("Basic + Advanced + Graph (bonus)")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        [
            "💬 Chat",
            "🧪 Comparateur de techniques",
            "🕸️ Graph RAG",
            "📊 Embeddings",
            "🌐 Knowledge Graph",
            "📈 Évaluation",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")

    stats = api_get("/stats")
    if stats:
        st.markdown("### Système")
        st.markdown(f"**Documents :** {stats['documents']}")
        st.markdown(f"**Chunks :** {stats['chunks']}")
        st.markdown(f"**Dim. embeddings :** {stats['embedding_dim']}")
        st.markdown(f"**Nœuds graphe :** {stats['graph_nodes']}")
        st.markdown(f"**Arêtes graphe :** {stats['graph_edges']}")
        st.markdown(f"**Communautés :** {stats['communities']}")
        st.markdown(f"**Chunk size / overlap :** {stats.get('chunk_size', '?')} / {stats.get('chunk_overlap', '?')}")
        st.markdown("---")
        st.markdown("### Modèles")
        api_ok = stats.get("api_available", False)
        api_badge = "✅ connecté" if api_ok else "❌ clé manquante"
        st.markdown(f"**LLM ({stats.get('llm_provider','?')}) :** `{stats['llm_model']}` — {api_badge}")
        st.markdown(f"**Embeddings :** `{stats['embed_model']}`")
        st.markdown(f"**Reranker :** `{stats['reranker_model']}`")
        if not api_ok:
            st.warning(
                "Définir `GROQ_API_KEY` dans l'environnement avant de lancer l'API. "
                "Clé gratuite : https://console.groq.com"
            )

    if st.button("🔄 Ré-indexer les documents"):
        with st.spinner("Indexation en cours..."):
            result = api_post("/ingest", {})
            if result:
                st.success(f"{result.get('documents', 0)} documents indexés, {result.get('chunks', 0)} chunks")
                st.rerun()


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : Chat
# ═══════════════════════════════════════════════════════════════════════════

if page == "💬 Chat":
    st.markdown('<div class="main-header">Interface de chat RAG</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Posez une question, configurez les techniques Advanced RAG '
        'et observez chaque étape du pipeline.</div>',
        unsafe_allow_html=True,
    )

    col_chat, col_cfg = st.columns([2, 1])

    with col_cfg:
        st.markdown("### ⚙️ Configuration du pipeline")

        with st.expander("📥 Retrieval (étape 1)", expanded=True):
            retrieval_method = st.selectbox(
                "Méthode de retrieval",
                ["hybrid", "dense", "sparse"],
                help="**hybrid** = BM25 + dense fusionnés via RRF (recommandé). "
                     "**dense** = embeddings seuls. **sparse** = BM25 seul.",
            )
            top_k = st.slider("Top-K candidats récupérés", 3, 20, 8)

        with st.expander("🚀 Advanced RAG (étape 1bis)", expanded=True):
            advanced_technique = st.selectbox(
                "Technique avancée",
                ["Aucune", "Query Rewriting", "Multi-Query (RRF)", "HyDE"],
                help=(
                    "**Aucune** : retrieval simple. "
                    "**Query Rewriting** : LLM réécrit la requête. "
                    "**Multi-Query** : LLM génère N variantes, fusion RRF. "
                    "**HyDE** : LLM génère une réponse hypothétique → embeddée."
                ),
            )
            use_query_rewriting = (advanced_technique == "Query Rewriting")
            use_multi_query = (advanced_technique == "Multi-Query (RRF)")
            use_hyde = (advanced_technique == "HyDE")

        with st.expander("🎯 Reranking & ordonnancement (étape 2)", expanded=True):
            use_reranking = st.checkbox(
                "Cross-encoder reranking",
                value=True,
                help="Réordonne les candidats avec un cross-encoder (plus précis).",
            )
            rerank_top_k = st.slider("Top-K après rerank", 1, 8, 3)
            use_lim_reorder = st.checkbox(
                "Lost-in-the-middle reorder",
                value=False,
                help="Place les meilleurs chunks aux extrémités du contexte (anti LIM).",
            )

        with st.expander("Récap des techniques actives"):
            pills = []
            pills.append(f"<span class='technique-pill'>{retrieval_method}</span>")
            if advanced_technique != "Aucune":
                pills.append(f"<span class='technique-pill technique-pill-active'>{advanced_technique}</span>")
            if use_reranking:
                pills.append("<span class='technique-pill technique-pill-active'>Rerank</span>")
            if use_lim_reorder:
                pills.append("<span class='technique-pill technique-pill-active'>LIM reorder</span>")
            st.markdown(" ".join(pills), unsafe_allow_html=True)

        st.markdown("### 💡 Questions d'exemple")
        samples = [
            "Qu'est-ce que le self-attention dans les Transformers ?",
            "Quelles stratégies de chunking sont utilisées en RAG ?",
            "Comment fonctionne HNSW ?",
            "Qu'est-ce que le fine-tuning LoRA ?",
            "Quand utiliser RAG plutôt que le fine-tuning ?",
            "Quel est le lien entre le Transformer, BERT et GPT ?",
        ]
        for q in samples:
            if st.button(q, key=f"sample_{q[:30]}"):
                st.session_state["_prefill"] = q
                st.rerun()

    with col_chat:
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        prefill = st.session_state.pop("_prefill", "")
        question = st.chat_input("Posez une question...") or prefill

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner(f"Pipeline RAG en cours ({advanced_technique}, rerank={use_reranking})..."):
                    result = api_post("/query", {
                        "question": question,
                        "method": retrieval_method,
                        "top_k": top_k,
                        "rerank_top_k": rerank_top_k,
                        "use_reranking": use_reranking,
                        "use_query_rewriting": use_query_rewriting,
                        "use_multi_query": use_multi_query,
                        "use_hyde": use_hyde,
                        "use_lim_reorder": use_lim_reorder,
                    })

                if result and "answer" in result:
                    st.markdown(result["answer"])

                    # Détails du pipeline
                    with st.expander("🔬 Détails du pipeline (étapes intermédiaires)"):
                        adv = result.get("advanced", {})
                        steps = result.get("steps", {})

                        if result.get("effective_query") != result.get("query"):
                            st.markdown(
                                f"<div class='step-card'><b>Requête réécrite</b><br/>"
                                f"<i>{result.get('effective_query', '')}</i></div>",
                                unsafe_allow_html=True,
                            )

                        if "query_variants" in steps:
                            st.markdown("<div class='step-card'><b>Variantes Multi-Query</b></div>",
                                        unsafe_allow_html=True)
                            for v in steps["query_variants"]:
                                st.caption(f"• {v}")

                        if "hypothetical_doc" in steps:
                            st.markdown(
                                f"<div class='step-card'><b>Réponse hypothétique (HyDE)</b><br/>"
                                f"<i>{steps['hypothetical_doc']}</i></div>",
                                unsafe_allow_html=True,
                            )

                        st.markdown(f"**Méthode utilisée :** `{result.get('method_used','?')}`")
                        st.markdown(f"**Reranking :** {result.get('reranked', False)}")
                        st.markdown(f"**LIM reorder :** {steps.get('lim_reorder', False)}")
                        st.markdown(f"**Longueur du prompt final :** {result.get('prompt_length_words', 0)} mots")

                    sources = result.get("sources", [])
                    if sources:
                        with st.expander(f"📎 Sources utilisées ({len(sources)})"):
                            for i, s in enumerate(sources):
                                rerank = f", rerank={s['rerank_score']:.3f}" if s.get("rerank_score") is not None else ""
                                st.markdown(
                                    f"**[{i+1}] {s['source']}** — *{s.get('section', '')}* "
                                    f"(score={s['score']:.3f}{rerank})"
                                )
                                st.caption(s.get("text", ""))

                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "details": result,
                    })
                elif result:
                    st.error(result.get("error", "Erreur inconnue"))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : Comparateur de techniques
# ═══════════════════════════════════════════════════════════════════════════

elif page == "🧪 Comparateur de techniques":
    st.markdown('<div class="main-header">Comparateur de techniques Advanced RAG</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Lance la même question avec différentes configurations et '
        'compare les réponses, sources et étapes intermédiaires.</div>',
        unsafe_allow_html=True,
    )

    question = st.text_input(
        "Question à tester",
        value="Qu'est-ce que le self-attention dans les Transformers ?",
    )

    cfg_col1, cfg_col2 = st.columns(2)
    with cfg_col1:
        rerank = st.checkbox("Cross-encoder reranking (toutes configs)", value=True)
        lim = st.checkbox("Lost-in-the-middle reorder (toutes configs)", value=False)
    with cfg_col2:
        top_k = st.slider("Top-K candidats", 3, 15, 8, key="cmp_topk")
        rerank_top_k = st.slider("Top-K après rerank", 1, 5, 3, key="cmp_rerank")

    techniques_to_compare = st.multiselect(
        "Techniques à comparer côte à côte",
        ["Baseline (hybrid)", "Query Rewriting", "Multi-Query (RRF)", "HyDE"],
        default=["Baseline (hybrid)", "Multi-Query (RRF)", "HyDE"],
    )

    if st.button("🚀 Lancer la comparaison", type="primary") and techniques_to_compare:
        results_per_technique = {}

        with st.spinner(f"Exécution de {len(techniques_to_compare)} configurations..."):
            for tech in techniques_to_compare:
                payload = {
                    "question": question,
                    "method": "hybrid",
                    "top_k": top_k,
                    "rerank_top_k": rerank_top_k,
                    "use_reranking": rerank,
                    "use_query_rewriting": tech == "Query Rewriting",
                    "use_multi_query": tech == "Multi-Query (RRF)",
                    "use_hyde": tech == "HyDE",
                    "use_lim_reorder": lim,
                }
                results_per_technique[tech] = api_post("/query", payload)

        cols = st.columns(len(techniques_to_compare))
        for col, (tech, res) in zip(cols, results_per_technique.items()):
            with col:
                st.markdown(f"### {tech}")
                if not res or "answer" not in res:
                    st.error(res.get("error", "Erreur") if res else "Pas de réponse")
                    continue

                steps = res.get("steps", {})

                # Étapes intermédiaires
                if "query_variants" in steps:
                    with st.expander("🔁 Variantes générées"):
                        for v in steps["query_variants"]:
                            st.caption(f"• {v}")
                if "hypothetical_doc" in steps:
                    with st.expander("📝 Réponse hypothétique"):
                        st.caption(steps["hypothetical_doc"])
                if res.get("effective_query") != question:
                    with st.expander("✏️ Requête réécrite"):
                        st.caption(res["effective_query"])

                # Réponse
                st.markdown("**Réponse**")
                st.markdown(res["answer"])

                # Sources
                with st.expander(f"📎 {len(res.get('sources', []))} sources"):
                    for i, s in enumerate(res.get("sources", [])):
                        st.markdown(f"**[{i+1}] {s['source']}** — *{s.get('section','')}*")
                        st.caption(f"score={s['score']:.3f}")
                        st.caption(s.get("text", ""))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : Graph RAG
# ═══════════════════════════════════════════════════════════════════════════

elif page == "🕸️ Graph RAG":
    st.markdown('<div class="main-header">Mode Graph RAG (bonus)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Combine retrieval vectoriel et traversée du graphe de connaissances.</div>',
        unsafe_allow_html=True,
    )

    g_col1, g_col2 = st.columns([2, 1])
    with g_col2:
        st.markdown("### Paramètres")
        top_k_vector = st.slider("Chunks vectoriels", 1, 8, 3)

        st.markdown("### Questions d'exemple (relationnelles)")
        for q in [
            "Quel est le lien entre le Transformer, BERT et GPT ?",
            "Quelles méthodes améliorent le retrieval RAG ?",
            "Compare LoRA et QLoRA pour le fine-tuning.",
            "Quels vector stores utilisent HNSW ?",
        ]:
            if st.button(q, key=f"graphq_{q[:25]}"):
                st.session_state["_graph_prefill"] = q
                st.rerun()

    with g_col1:
        question = st.text_input(
            "Question",
            value=st.session_state.pop("_graph_prefill", ""),
            placeholder="Ex. Quel est le lien entre le Transformer, BERT et GPT ?",
        )
        if st.button("Interroger Graph RAG", type="primary") and question:
            with st.spinner("Graph RAG en cours..."):
                res = api_post("/query/graph", {"question": question, "top_k_vector": top_k_vector})

            if res and "answer" in res:
                st.markdown("### Réponse")
                st.markdown(res["answer"])

                if res.get("graph_entities"):
                    with st.expander(f"🕸️ {len(res['graph_entities'])} entités utilisées"):
                        st.write(res["graph_entities"])

                if res.get("graph_triples"):
                    with st.expander(f"🔗 {len(res['graph_triples'])} relations traversées"):
                        for t in res["graph_triples"]:
                            st.markdown(f"**{t['source']}** —[{t['relation']}]→ **{t['target']}**")

                if res.get("sources"):
                    with st.expander(f"📎 {len(res['sources'])} chunks vectoriels"):
                        for i, s in enumerate(res["sources"]):
                            st.markdown(f"**[{i+1}] {s['source']}** — *{s.get('section','')}*")
                            st.caption(s.get("text", ""))


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : Embeddings
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📊 Embeddings":
    st.markdown('<div class="main-header">Espace d\'embeddings</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Projection PCA des embeddings — explorez les clusters sémantiques.</div>',
        unsafe_allow_html=True,
    )

    tab2d, tab3d = st.tabs(["Projection 2D", "Projection 3D"])

    with tab2d:
        data_2d = api_get("/embeddings")
        if data_2d and "points" in data_2d:
            df = pd.DataFrame(data_2d["points"])

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total chunks", data_2d["n_chunks"])
            c2.metric("Dim. embeddings", data_2d["embedding_dim"])
            c3.metric("Variance PC1", f"{data_2d['explained_variance'][0]:.1%}")
            c4.metric("Variance PC2", f"{data_2d['explained_variance'][1]:.1%}")

            fig = px.scatter(
                df, x="x", y="y", color="source",
                hover_data=["section", "text_preview"],
                title="Embeddings des chunks — PCA 2D",
                labels={"x": "PC 1", "y": "PC 2", "source": "Document"},
                height=600,
            )
            fig.update_traces(marker=dict(size=10, line=dict(width=1, color="white")))
            fig.update_layout(plot_bgcolor="#fafafa")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Répartition des chunks par document")
            sc = df["source"].value_counts().reset_index()
            sc.columns = ["Source", "Nombre"]
            fig_bar = px.bar(sc, x="Source", y="Nombre", color="Source", height=300)
            fig_bar.update_layout(showlegend=False, plot_bgcolor="#fafafa")
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab3d:
        data_3d = api_get("/embeddings/3d")
        if data_3d and "points" in data_3d:
            df3 = pd.DataFrame(data_3d["points"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Variance PC1", f"{data_3d['explained_variance'][0]:.1%}")
            c2.metric("Variance PC2", f"{data_3d['explained_variance'][1]:.1%}")
            c3.metric("Variance PC3", f"{data_3d['explained_variance'][2]:.1%}")

            fig3d = px.scatter_3d(
                df3, x="x", y="y", z="z", color="source",
                hover_data=["section", "text_preview"],
                title="Embeddings des chunks — PCA 3D",
                height=700,
            )
            fig3d.update_traces(marker=dict(size=5, line=dict(width=0.5, color="white")))
            st.plotly_chart(fig3d, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : Knowledge Graph
# ═══════════════════════════════════════════════════════════════════════════

elif page == "🌐 Knowledge Graph":
    st.markdown('<div class="main-header">Knowledge Graph</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Graphe entités-relations extrait des documents.</div>',
        unsafe_allow_html=True,
    )

    graph_data = api_get("/graph")
    if graph_data and "nodes" in graph_data:
        nodes = graph_data["nodes"]
        edges = graph_data["edges"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Entités", graph_data["total_nodes"])
        c2.metric("Relations", graph_data["total_edges"])
        c3.metric("Communautés", len(graph_data.get("communities", [])))
        c4.metric("Types d'entités", len(graph_data.get("type_counts", {})))

        tab1, tab2, tab3 = st.tabs(["Graphe interactif", "Communautés", "Statistiques"])

        type_colors = {
            "TECHNOLOGY": "#4A90D9",
            "CONCEPT": "#E67E22",
            "METHOD": "#27AE60",
            "METRIC": "#E74C3C",
            "FRAMEWORK": "#9B59B6",
            "PERSON": "#F39C12",
            "UNKNOWN": "#95A5A6",
        }

        with tab1:
            G = nx.DiGraph()
            for n in nodes:
                G.add_node(n["id"], type=n["type"], degree=n["degree"])
            for e in edges:
                G.add_edge(e["source"], e["target"], relation=e["relation"])
            pos = nx.spring_layout(G, k=2.5, iterations=80, seed=42)

            edge_x, edge_y = [], []
            for e in edges:
                if e["source"] in pos and e["target"] in pos:
                    x0, y0 = pos[e["source"]]
                    x1, y1 = pos[e["target"]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=1.2, color="#BDC3C7"),
                hoverinfo="none", mode="lines", showlegend=False,
            )

            edge_lab_x, edge_lab_y, edge_lab_t = [], [], []
            for e in edges:
                if e["source"] in pos and e["target"] in pos:
                    x0, y0 = pos[e["source"]]
                    x1, y1 = pos[e["target"]]
                    edge_lab_x.append((x0 + x1) / 2)
                    edge_lab_y.append((y0 + y1) / 2)
                    edge_lab_t.append(e["relation"])

            edge_label_trace = go.Scatter(
                x=edge_lab_x, y=edge_lab_y,
                mode="text", text=edge_lab_t,
                textfont=dict(size=8, color="#7F8C8D"),
                hoverinfo="none", showlegend=False,
            )

            node_traces = []
            for etype, color in type_colors.items():
                tn = [n for n in nodes if n["type"] == etype]
                if not tn:
                    continue
                xs = [pos[n["id"]][0] for n in tn if n["id"] in pos]
                ys = [pos[n["id"]][1] for n in tn if n["id"] in pos]
                texts = [n["id"] for n in tn if n["id"] in pos]
                sizes = [15 + 4 * n["degree"] for n in tn if n["id"] in pos]
                hovers = [f"<b>{n['id']}</b><br>Type : {n['type']}<br>Degré : {n['degree']}"
                          for n in tn if n["id"] in pos]
                node_traces.append(go.Scatter(
                    x=xs, y=ys,
                    mode="markers+text",
                    marker=dict(size=sizes, color=color, line=dict(width=1.5, color="white")),
                    text=texts, textposition="top center",
                    textfont=dict(size=9, color="#2C3E50"),
                    hovertext=hovers, hoverinfo="text",
                    name=etype,
                ))

            fig = go.Figure(
                data=[edge_trace, edge_label_trace] + node_traces,
                layout=go.Layout(
                    title="Knowledge Graph — Entités et relations",
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode="closest",
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    plot_bgcolor="white",
                    height=650,
                    margin=dict(l=20, r=20, t=60, b=20),
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            communities = graph_data.get("communities", [])
            if communities:
                comm_df = pd.DataFrame([
                    {"Communauté": f"C{c['id']+1}", "Taille": c["size"],
                     "Entités": ", ".join(c["entities"][:8]) + ("..." if len(c["entities"]) > 8 else "")}
                    for c in communities
                ])
                fig_comm = px.bar(
                    comm_df, x="Communauté", y="Taille",
                    color="Taille", color_continuous_scale="Blues",
                    hover_data=["Entités"], height=350,
                )
                fig_comm.update_layout(plot_bgcolor="#fafafa")
                st.plotly_chart(fig_comm, use_container_width=True)

                for c in communities:
                    with st.expander(f"Communauté {c['id']+1} — {c['size']} entités"):
                        st.write(c["entities"])
            else:
                st.info("Aucune communauté détectée.")

        with tab3:
            cl, cr = st.columns(2)
            with cl:
                tc = graph_data.get("type_counts", {})
                if tc:
                    tc_df = pd.DataFrame([{"Type": k, "Nombre": v} for k, v in tc.items()])
                    fig_types = px.pie(
                        tc_df, names="Type", values="Nombre",
                        color="Type", color_discrete_map=type_colors,
                        title="Types d'entités", height=400,
                    )
                    st.plotly_chart(fig_types, use_container_width=True)

            with cr:
                top = sorted(nodes, key=lambda x: x["degree"], reverse=True)[:10]
                deg_df = pd.DataFrame(top)
                fig_deg = px.bar(
                    deg_df, x="id", y="degree", color="type",
                    color_discrete_map=type_colors,
                    title="Top 10 entités les plus connectées",
                    labels={"id": "Entité", "degree": "Degré"},
                    height=400,
                )
                fig_deg.update_layout(plot_bgcolor="#fafafa", xaxis_tickangle=-45)
                st.plotly_chart(fig_deg, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════
# PAGE : Évaluation
# ═══════════════════════════════════════════════════════════════════════════

elif page == "📈 Évaluation":
    st.markdown('<div class="main-header">Évaluation du retrieval</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Hit Rate / MRR sur le golden set, comparaison Dense / Sparse / Hybrid.</div>',
        unsafe_allow_html=True,
    )

    if st.button("Lancer l'évaluation", type="primary"):
        with st.spinner("Évaluation en cours..."):
            ev = api_get("/evaluate")
        if ev and "methods" in ev:
            st.success(f"Évaluation sur {ev['golden_set_size']} questions")
            methods = ev["methods"]

            cols = st.columns(len(methods))
            for col, (name, m) in zip(cols, methods.items()):
                with col:
                    st.markdown(f"### {name}")
                    st.metric("Hit Rate @5", f"{m['hit_rate']:.0%}")
                    st.metric("MRR @5", f"{m['mrr']:.3f}")

            df = pd.DataFrame([
                {"Méthode": n, "Métrique": "Hit Rate @5", "Valeur": v["hit_rate"]}
                for n, v in methods.items()
            ] + [
                {"Méthode": n, "Métrique": "MRR @5", "Valeur": v["mrr"]}
                for n, v in methods.items()
            ])
            method_colors = {"Dense": "#4A90D9", "Sparse (BM25)": "#E74C3C", "Hybrid (RRF)": "#27AE60"}
            fig = px.bar(
                df, x="Méthode", y="Valeur", color="Méthode",
                color_discrete_map=method_colors,
                facet_col="Métrique", barmode="group", height=400,
            )
            fig.update_layout(plot_bgcolor="#fafafa", showlegend=False)
            fig.update_yaxes(range=[0, 1.05])
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("""
            **Métriques :**
            - **Hit Rate @5** : proportion de requêtes pour lesquelles le document attendu apparaît dans le top-5.
            - **MRR @5** : moyenne de 1 / rang du premier document pertinent.
            """)
    else:
        st.info("Cliquez sur **Lancer l'évaluation** pour comparer Dense / Sparse / Hybrid sur le golden set.")
        st.markdown("""
        ### Golden set utilisé

        | Question | Source attendue |
        |---|---|
        | Qu'est-ce que le self-attention dans les Transformers ? | transformers.md |
        | Quelles stratégies de chunking existent en RAG ? | rag_systems.md |
        | Qu'est-ce que le fine-tuning LoRA ? | finetuning.md |
        | Comment fonctionne l'indexation HNSW ? | vector_databases.md |
        | Quels sont les bénéfices du retrieval hybride ? | rag_systems.md |
        | Qu'est-ce que le DPO dans l'alignement des LLM ? | finetuning.md |
        """)
