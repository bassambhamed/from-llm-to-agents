# Vector Databases and Indexing

## Why Vector Databases
Vector databases store high-dimensional embeddings and enable fast approximate
nearest neighbor (ANN) search. Exact search has O(n) complexity, which is too
slow for millions of vectors. ANN algorithms trade a small amount of accuracy
for orders-of-magnitude speedup.

## HNSW Algorithm
Hierarchical Navigable Small World (HNSW) is the most popular ANN algorithm.
It builds a multi-layer graph where each layer is a navigable small-world network.
Search starts at the top layer (sparse, long-range connections) and progressively
refines through lower layers (dense, short-range connections).

HNSW provides excellent recall (>95%) with millisecond-level latency for
collections of millions of vectors. Key parameters are M (number of connections)
and efConstruction (build-time quality vs speed tradeoff).

## Popular Solutions
- Chroma: embedded/server mode, simple API, good for prototyping
- FAISS (Meta): library-level, extremely fast, GPU support, no native persistence
- Pinecone: managed cloud, serverless scaling, metadata filtering
- Weaviate: open-source, native hybrid search, GraphQL API
- Qdrant: open-source, advanced filtering, gRPC, production-ready
- Milvus: open-source, highly scalable, multi-index support

## Similarity Metrics
The three main metrics for vector similarity are:
- Cosine similarity: measures angle between vectors, insensitive to magnitude
- Dot product: cosine × norms, useful when magnitude encodes importance
- Euclidean distance: geometric distance, less common in RAG

Important: the similarity metric must match what the embedding model was trained
with. If the model uses cosine similarity during training, index with cosine.
