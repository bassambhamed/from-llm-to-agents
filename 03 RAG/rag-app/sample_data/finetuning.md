# LLM Fine-Tuning

## When to Fine-Tune vs RAG
Fine-tuning modifies model weights to adapt behavior (tone, format, domain
language). RAG provides dynamic knowledge access. They are complementary:
- Need fresh knowledge → RAG
- Need specific behavior/style → Fine-tuning
- Need both → Hybrid (fine-tune for behavior + RAG for knowledge)

## LoRA and QLoRA
Low-Rank Adaptation (LoRA) freezes the pre-trained model and injects trainable
rank decomposition matrices into each Transformer layer. Instead of updating the
full weight matrix W, LoRA learns two small matrices A and B such that the update
is W + BA, where B has shape (d, r) and A has shape (r, d) with r << d.

QLoRA combines LoRA with 4-bit quantization of the base model, enabling
fine-tuning of 65B parameter models on a single 48GB GPU. This dramatically
reduces the hardware requirements for fine-tuning.

## RLHF and DPO
Reinforcement Learning from Human Feedback (RLHF) trains a reward model from
human preferences, then optimizes the LLM policy via PPO. Direct Preference
Optimization (DPO) simplifies this by directly optimizing preferences without
a separate reward model, using a classification loss on preference pairs.

## Evaluation of Fine-Tuned Models
Fine-tuned models should be evaluated on:
- Task-specific benchmarks (accuracy, F1, BLEU, ROUGE)
- Safety and alignment checks (TruthfulQA, toxicity)
- Catastrophic forgetting tests (performance on original capabilities)
- Human evaluation for subjective quality (fluency, helpfulness)
