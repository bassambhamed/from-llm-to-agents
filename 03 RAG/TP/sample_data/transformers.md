# Transformer Architecture

## Overview
The Transformer architecture was introduced by Vaswani et al. in the 2017 paper
"Attention Is All You Need". It replaced recurrent neural networks (RNNs) with
self-attention mechanisms, enabling parallel processing of sequences.

The key innovation is scaled dot-product attention, which computes attention
weights between all pairs of tokens simultaneously. This allows capturing
long-range dependencies without the vanishing gradient problem.

## Self-Attention Mechanism
Self-attention computes three matrices from the input: Query (Q), Key (K), and
Value (V). The attention output is computed as softmax(QK^T / sqrt(d_k)) * V.

Multi-head attention runs multiple attention operations in parallel, each with
different learned projections. This allows the model to attend to information
from different representation subspaces at different positions.

## Encoder-Decoder Structure
The original Transformer has an encoder-decoder structure. The encoder processes
the input sequence bidirectionally. The decoder generates the output sequence
autoregressively, attending to both its own previous outputs and the encoder's
representations via cross-attention.

Modern variants include encoder-only models (BERT), decoder-only models (GPT),
and encoder-decoder models (T5, BART).

## Positional Encoding
Since self-attention is permutation-invariant, positional information must be
injected explicitly. The original paper uses sinusoidal positional encodings.
Modern models often use learned positional embeddings or relative position
encodings like RoPE (Rotary Position Embedding) and ALiBi.
