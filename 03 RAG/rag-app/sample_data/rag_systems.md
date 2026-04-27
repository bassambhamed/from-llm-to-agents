# Retrieval-Augmented Generation

## Definition
Retrieval-Augmented Generation (RAG) combines an information retrieval layer with
a language model so that responses are generated from retrieved evidence instead
of relying only on parametric memory. The canonical paper by Lewis et al. (2020)
introduced this paradigm for knowledge-intensive NLP tasks.

RAG systems split knowledge into parametric memory (model weights, frozen at
training time) and non-parametric memory (document index, updatable at any time).

## Why RAG Matters
Pure LLMs suffer from knowledge cutoff, hallucinations under uncertainty, and
inability to access private enterprise data. RAG addresses these by grounding
generation in retrieved evidence, enabling source attribution and freshness.

In production, RAG reduces hallucination rates by 40-60% compared to vanilla
LLM prompting, according to industry benchmarks.

## Chunking Strategies
Chunking is the most underestimated quality lever in RAG. Strategies include:
- Fixed-size (token-based): window of 256-512 tokens with 10-20% overlap
- Recursive splitting: split by hierarchical separators (paragraphs, sentences)
- Semantic chunking: segment by embedding similarity between adjacent passages
- Document-aware: respect document structure (headings, sections, code blocks)

The optimal chunk size depends on the use case: smaller chunks (256 tokens) favor
precision, while larger chunks (1024 tokens) preserve more context.

## Hybrid Retrieval
Hybrid retrieval combines sparse methods (BM25/TF-IDF for exact keyword matching)
with dense methods (embedding similarity for semantic matching). Results are fused
using Reciprocal Rank Fusion (RRF). This is the recommended approach for
production systems as it balances recall and robustness.

## Evaluation
RAG evaluation requires both component-level and end-to-end metrics:
- Retrieval: Recall@k, Hit Rate, MRR, nDCG
- Generation: Faithfulness, Answer Relevancy (via Ragas framework)
- Context: Context Precision, Context Recall
- Operations: latency p50/p95, cost per query, fallback rate
