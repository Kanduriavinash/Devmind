# Research contribution status

**Assessment date:** 17 November 2026  
**This is an evidence-status table, not a claim that DevMind is novel.**

| ID | Candidate contribution | Implementation | Empirical support | Safe manuscript wording |
|---|---|---|---|---|
| C1 | Traceable deterministic issue-query variants. | Four transformations preserve the original issue and record their extracted features and generated text. | Unit tests plus raw transformation traces in the pilot. Similar query reformulation is established prior work. | “We implemented four deterministic query conditions for a controlled ablation.” |
| C2 | Measure the effect of query enrichment on file localization. | The evaluator pairs each query with the same snapshot, retriever, cutoff, and proxy label. | Five-case development-split pilot: TF-IDF Recall@3 was 0.60 for raw text and 0.80 for keywords/identifiers; Recall@1 and Recall@5 remained 0.40 and 0.80. One target path was missed by all lexical methods. Labels are unreviewed changed-file proxies. | “In a five-instance exploratory pilot using changed-file proxies, keyword/identifier enrichment moved one target into the top three; the sample is too small and weakly labelled for a general effectiveness claim.” |
| C3 | Compare lexical, semantic, and hybrid retrieval. | TF-IDF, BM25, lexical RRF, Sentence Transformers cosine, and lexical-semantic RRF were run on matched inputs. | On five unreviewed proxy labels, dense cosine Recall@5 was 0.40 versus TF-IDF 0.80; lexical-semantic RRF was 0.60 for raw queries. Dense document embedding and index construction took 594.737 seconds. | “In a five-instance exploratory CPU pilot, the tested general-purpose embedding model did not improve agreement with changed-file proxies and had substantially higher index-build cost.” |
| C4 | Link proposed changes to evidence and bounded verification. | Candidate diffs are validated and tested in Docker-only disposable copies; a passing status still requires human review. | Historical controlled fixtures passed their selected tests. Current Docker integration was unavailable during the audit. | “The prototype records proposed patches and selected test outcomes in controlled fixtures; general repair quality has not been established.” |
| C5 | Measure whether retrieval improves patch outcomes. | The comparison runner has common test and reporting paths for baseline, LLM-only, RAG, and iterative arms. | No matched model-backed runs or independently adjudicated resolution labels exist. | “The downstream repair comparison is not yet evaluated.” |

## Novelty positioning

The project does not claim to introduce query reformulation, lexical or dense retrieval, RRF, evidence-guided repair, autonomous agents, or test-based patch evaluation. Its current defensible output is an implementation and a traceable five-case pilot with lexical and model-specific dense measurements. Any broader contribution claim depends on reviewed labels, larger paired experiments, and downstream repair evaluation.
