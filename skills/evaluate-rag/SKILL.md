---
name: evaluate-rag
description: Evaluate RAG across retrieval, context, answer grounding, citation support, latency, and cost.
---

# Evaluate RAG

1. Define the decisions the evaluation must support and the failure costs for missing, wrong, stale, unauthorized, or unsupported information.
2. Build a versioned dataset from real questions, difficult boundaries, ambiguous terminology, multi-document reasoning, no-answer cases, and known failures. Keep a held-out set.
3. Record authoritative answers, acceptable evidence, access constraints, and relevant document versions.
4. Evaluate retrieval independently using measures such as recall at k, ranking quality, source diversity, and authorization correctness.
5. Evaluate supplied context for relevance, duplication, truncation, ordering, freshness, and contamination.
6. Evaluate answers for correctness, completeness, groundedness, citation entailment, calibration, refusal, and unsupported claims.
7. Compare chunking, query transformation, filters, hybrid search, reranking, and generation changes one variable at a time.
8. Report results by meaningful slices, not only one average. Include latency, token use, index cost, and failure examples.
9. Trace representative failures from query through retrieved chunks to final answer and assign them to retrieval, context construction, or generation.

Prevent evaluation leakage and unstable live-web answers. Recommend changes only when improvements hold on relevant slices without weakening authorization or groundedness.
