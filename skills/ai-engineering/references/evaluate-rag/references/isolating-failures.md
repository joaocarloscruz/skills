# Isolate RAG failures

Use for a reproducible comparison, not as a demand to add every metric. Record the corpus snapshot, document permissions and versions, chunking/index parameters, retriever/reranker, prompt, generator, and judge configuration. Avoid tuning on the held-out cases.

## Choose metrics with known denominators

| Measurement | Required evidence | What it does not establish |
| --- | --- | --- |
| Document/chunk recall at k | Labeled relevant IDs and a defined relevance unit | Answer quality, or recall of documents never labeled |
| Ranking quality | Relevance labels and an agreed cutoff | Whether the final prompt kept the useful evidence |
| Context support for reference claims | Reference claims and retrieved text | Exact document-ID recall; a judge-based proxy has different semantics |
| Answer groundedness/faithfulness | Answer claims and supplied context | Factual truth when the source itself is wrong or stale |
| Answer correctness | Independent accepted answer or task oracle | Whether a correct answer was supported by the cited source |
| Citation support | Each material claim mapped to its actual cited span | That merely having a citation makes the claim true |

Keep no-answer cases separate when a recall denominator is empty. Deduplicate relevant IDs before counting and specify whether alternate valid sources receive credit. A string match for a document title is not evidence that its contents support the claim.

## Run a small diagnostic comparison

For the same failed question, compare these conditions while holding the generator and prompt policy fixed:

1. Actual retrieved context and the final context after truncation/deduplication.
2. A verified minimal context sufficient to answer, within the same usable context budget.
3. No supporting context, when the product is expected to abstain without evidence.

If verified evidence fixes the answer, inspect retrieval and context construction. If evidence was retrieved but omitted, repair assembly. If adequate evidence remains but the answer is wrong, investigate generation or conflicting instructions. Treat this as diagnostic evidence, not a proof that a single stage is solely responsible.

Include near-duplicate outdated documents, questions needing multiple sources, conflicting evidence, and another tenant's tempting but unauthorized answer. Test permission filtering before chunks enter the model context; redacting only the final answer does not undo an unauthorized retrieval.

## Compare without fooling the evaluator

- Pair old/new runs on the same cases. Repeat stochastic cases and report changes by meaningful slice plus uncertainty; do not promote a change from one favorable answer.
- Calibrate automated judges against a small human-reviewed set, including clearly unsupported and partially supported answers. Preserve judge failures separately from product failures.
- Separate quoted source text from judge instructions. Adversarial retrieved content must remain data for both the answering model and the evaluator.
- Report p50/p95 latency and token/index costs for comparable workloads where those measurements are available. An improved average can hide unacceptable permission failures or degraded no-answer behavior.

## Primary references

- [Ragas: faithfulness measures support in context](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)
- [Ragas: context recall variants and reference requirements](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/)
- [OWASP: RAG security](https://cheatsheetseries.owasp.org/cheatsheets/RAG_Security_Cheat_Sheet.html)

Ragas names and APIs vary by version; use its installed-version documentation if implementing those metrics. The diagnostic comparisons above are original, framework-independent evaluation guidance.
