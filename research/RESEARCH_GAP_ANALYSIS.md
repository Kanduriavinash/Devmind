# Research gap and feasible DevMind study

**Status:** Scoping synthesis of the reviewed literature through 16 November 2026, updated with the five-case pilot completed on 17 November 2026. The literature review identifies established prior work; the pilot is preliminary evidence, not a field-level research gap claim.

## What prior work already establishes

- Bug-report classification has established machine-learning baselines including TF-IDF, logistic regression, and linear SVM.
- Bug localization includes classical IR, query reformulation, relevance feedback, learned bi-encoders, dense and hybrid retrieval, graph expansion, and LLM reranking.
- Repository-level patch generation and test-based grading are studied by SWE-bench and software-engineering agent systems.
- Prior work has directly examined how localization affects repair outcomes. DevMind does not claim that this relationship has not been studied.
- Passing tests are not sufficient to establish patch correctness; published work has manually examined test-accepted patches for overfitting and ambiguity.

See research/LITERATURE_REVIEW.md and research/RELATED_WORK_COMPARISON.csv for the reviewed sources and task distinctions.

## What the DevMind pilot observed

Five SWE-bench Lite development records from five repositories were selected before scoring. Each had a changed-file proxy derived from fixing-patch metadata. On this sample, keyword/identifier enrichment moved one TF-IDF target from rank 4 to rank 3, changing mean Recall@3 from 0.60 to 0.80; Recall@1 and Recall@5 were unchanged. Lexical RRF had a higher mean MRR and nDCG@5 than standalone lexical methods. Dense cosine with all-MiniLM-L6-v2 had Recall@5 0.40, MRR 0.400, and nDCG@5 0.400, compared with raw TF-IDF Recall@5 0.80, MRR 0.550, and nDCG@5 0.612. Dense-plus-lexical RRF reached Recall@5 0.60 for raw queries and 0.40 for enriched queries. Dense document embedding and vector-index construction took 594.737 seconds on the CPU; TF-IDF index construction took 1.199 seconds in the same run.

These observations are based on five unreviewed proxy labels. They do not demonstrate exact localization, causal improvement, or general performance. The full scores and resource measurements are in reports/experiments/RESULTS.md. The dense result is tied to its pinned general-purpose model and CPU execution.

## Remaining DevMind questions

1. Whether the observed query-enrichment and lexical-ranking patterns persist on a larger, independently reviewed sample.
2. Whether file-level proxy labels can be replaced or supplemented with reviewed file/function relevance judgments and clear agreement policy.
3. Whether the observed dense-versus-lexical difference persists after human label review and on a larger sample; the current run records CPU latency, peak memory, and context estimates for only five instances.
4. Whether retrieval quality changes patch quality under identical model, prompt, evidence budget, test, timeout, and grading conditions. No matched repair comparison or independent resolution labels exist.
5. Classification quality, severity extraction quality, inter-annotator agreement, and generalization. These remain unavailable without independent labels.

## Feasible follow-up study

Use a predeclared set of public issue records with pinned base commits and a documented sample-selection procedure. Keep source issue text separate from all fixing-patch metadata. Review multiple changed files and likely relevant functions with at least two annotators where feasible; record disagreements rather than silently resolving them. Keep failed retrievals and exclusions.

Compare raw, normalized, keywords/identifiers, and structured query variants against identical chunks and cutoffs. Compare TF-IDF, BM25, lexical RRF, dense cosine, and lexical-semantic RRF only when the same model and resource controls are recorded. Report Precision@1/3/5, Recall@5, MRR, nDCG@5, per-issue rankings, latency, index-build time, process memory, and a tokenizer-specific context count when a model is involved.

Repair evaluation should wait until a model provider, model/version, prompt, context and candidate budget, test environment, timeout, and issue-resolution adjudication can be held constant across arms. Official SWE-bench resolution claims require its official grading harness.

## Research questions and current answerability

- **RQ1:** How does deterministic query enrichment change file-proxy localization? A first descriptive five-case result exists; broader answer is pending reviewed labels and a larger sample.
- **RQ2:** How do lexical, semantic, and hybrid methods compare? A five-case comparison exists. On these proxy labels, dense cosine and lexical-semantic RRF scored below TF-IDF; general comparison remains open.
- **RQ3:** Does retrieval evidence improve repair outcomes? Not answerable from current runs.
- **RQ4:** What resource and traceability trade-offs occur? The lexical and pinned-model runs recorded runtime, index-build timing, retrieval latency, context estimates, and sampled RSS. These measurements describe this Windows CPU only.

## Claims to avoid

- Do not claim “first,” “novel,” or that no related system exists.
- Do not call deterministic category rules a trained classifier.
- Do not describe the default application as semantic retrieval; it defaults to TF-IDF.
- Do not treat changed-file proxy paths as exact bug locations.
- Do not claim SWE-bench training, resolution performance, or official grading from generated predictions.
- Do not call a selected test pass a confirmed fix or a synthetic fixture a real-repository repair.
- Do not interpret five-case point estimates as statistical significance or generalization.
