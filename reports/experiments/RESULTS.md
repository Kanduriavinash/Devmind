# Retrieval pilot results

**Run:** 17 November 2026  
**Evidence:** evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl and its adjacent runmeta JSON  
**Interpretation:** exploratory, five-case, changed-file-proxy pilot; no human-reviewed localization labels

## Design

Five SWE-bench Lite development instances from five distinct repositories were selected before scoring. Each instance had one relevant-file proxy extracted from its fixing-patch changed paths. Four deterministic query conditions were compared with TF-IDF cosine, Okapi BM25, and equal-weight lexical reciprocal-rank fusion (RRF). The same pinned base snapshot, ordered chunks, top-k=5, and proxy label were used across methods for each issue.

The sample has five records and one binary file-level proxy per record. Scores indicate agreement with these proxy paths, not verified bug localization. The estimates are descriptive only; no confidence interval or significance test is reported.

## Aggregate metrics

All metric values are means over five issues. Precision at k uses the metric implementation's number-of-proxy-files divided by k; each issue has one proxy label.

| Query condition | Method | P@1 | P@3 | P@5 | R@5 | MRR | nDCG@5 |
|---|---|---:|---:|---:|---:|---:|---:|
| Raw | TF-IDF cosine | 0.400 | 0.200 | 0.160 | 0.800 | 0.550 | 0.612 |
| Raw | BM25 | 0.400 | 0.200 | 0.160 | 0.800 | 0.517 | 0.586 |
| Raw | Lexical RRF | 0.600 | 0.267 | 0.160 | 0.800 | 0.667 | 0.700 |
| Normalized | TF-IDF cosine | 0.400 | 0.200 | 0.160 | 0.800 | 0.550 | 0.612 |
| Normalized | BM25 | 0.400 | 0.200 | 0.160 | 0.800 | 0.517 | 0.586 |
| Normalized | Lexical RRF | 0.600 | 0.267 | 0.160 | 0.800 | 0.667 | 0.700 |
| Keywords and identifiers | TF-IDF cosine | 0.400 | 0.267 | 0.160 | 0.800 | 0.567 | 0.626 |
| Keywords and identifiers | BM25 | 0.400 | 0.200 | 0.160 | 0.800 | 0.517 | 0.586 |
| Keywords and identifiers | Lexical RRF | 0.600 | 0.267 | 0.160 | 0.800 | 0.667 | 0.700 |
| Structured | TF-IDF cosine | 0.400 | 0.267 | 0.160 | 0.800 | 0.567 | 0.626 |
| Structured | BM25 | 0.400 | 0.200 | 0.160 | 0.800 | 0.507 | 0.577 |
| Structured | Lexical RRF | 0.600 | 0.267 | 0.160 | 0.800 | 0.667 | 0.700 |

## Paired per-issue ranks

The values below are the rank of the one proxy file in the top-five unique-file list; “>5” means it was not retrieved in the top five.

| Evaluation ID | Proxy path | TF-IDF raw | TF-IDF keywords | BM25 raw | BM25 keywords | Lexical RRF raw |
|---|---|---:|---:|---:|---:|---:|
| pilot-01 | src/marshmallow/schema.py | 1 | 1 | 1 | 1 | 1 |
| pilot-02 | pvlib/temperature.py | 2 | 2 | 1 | 1 | 1 |
| pilot-03 | pydicom/valuerep.py | >5 | >5 | >5 | >5 | >5 |
| pilot-04 | astroid/nodes/node_classes.py | 1 | 1 | 4 | 4 | 3 |
| pilot-05 | src/sqlfluff/core/parser/helpers.py | 4 | 3 | 3 | 3 | 1 |

## Observations

- Lexical RRF had the highest mean top-rank metrics in this sample: P@1=0.60, MRR=0.667, and nDCG@5=0.700. Its Recall@5 was 0.80, the same as both standalone lexical methods.
- Adding keywords and identifiers moved the SQLFluff proxy from TF-IDF rank 4 to rank 3. Mean TF-IDF Recall@3 changed from 0.60 to 0.80; Recall@1 and Recall@5 stayed at 0.40 and 0.80.
- Normalization alone produced the same ranking metrics as raw text in all three lexical methods for this sample.
- The structured query did not improve the lexical RRF ranking. BM25's mean MRR and nDCG@5 were slightly lower for structured queries than for raw queries.
- Every method missed the pydicom proxy file in its top five. This is the one miss behind Recall@5=0.80.

These are observations on five selected cases. They do not show that RRF or query enrichment will perform better on a larger or independently reviewed sample.

## Dense comparison against the paired TF-IDF baseline

The dense run uses the same five issues, base snapshots, four query variants, top-k=5, and separate proxy labels. It also recomputes TF-IDF in the same process and corpus; its twenty TF-IDF rankings and metrics exactly match the primary lexical run.

An independent full CPU rerun produced a separate 100-record JSONL. Direct comparison showed exact equality for all 100 ranked-file lists, metric dictionaries, query traces, base-snapshot digests, and hash-verification flags. This confirms repeatability of the ranking and metric results under the pinned inputs and model. Timings varied between processes, and the replication process did not have a process-level memory sampler; use the primary run for the recorded 670.2919-second total and 932.89 MiB sampled peak RSS.

| Query condition | Method | P@1 | P@5 | R@5 | MRR | nDCG@5 |
|---|---|---:|---:|---:|---:|---:|
| Raw | TF-IDF cosine | 0.400 | 0.160 | 0.800 | 0.550 | 0.612 |
| Raw | Sentence Transformer cosine | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Raw | Lexical-semantic RRF | 0.400 | 0.120 | 0.600 | 0.440 | 0.477 |
| Normalized | TF-IDF cosine | 0.400 | 0.160 | 0.800 | 0.550 | 0.612 |
| Normalized | Sentence Transformer cosine | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Normalized | Lexical-semantic RRF | 0.400 | 0.120 | 0.600 | 0.440 | 0.477 |
| Keywords and identifiers | TF-IDF cosine | 0.400 | 0.160 | 0.800 | 0.567 | 0.626 |
| Keywords and identifiers | Sentence Transformer cosine | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Keywords and identifiers | Lexical-semantic RRF | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Structured | TF-IDF cosine | 0.400 | 0.160 | 0.800 | 0.567 | 0.626 |
| Structured | Sentence Transformer cosine | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Structured | Lexical-semantic RRF | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |

| Evaluation ID | Proxy path | TF-IDF raw | Dense raw | Lexical-semantic RRF raw | TF-IDF keywords | Dense keywords | Lexical-semantic RRF keywords |
|---|---|---:|---:|---:|---:|---:|---:|
| pilot-01 | src/marshmallow/schema.py | 1 | 1 | 1 | 1 | 1 | 1 |
| pilot-02 | pvlib/temperature.py | 2 | >5 | >5 | 2 | >5 | >5 |
| pilot-03 | pydicom/valuerep.py | >5 | >5 | 5 | >5 | >5 | >5 |
| pilot-04 | astroid/nodes/node_classes.py | 1 | 1 | 1 | 1 | 1 | 1 |
| pilot-05 | src/sqlfluff/core/parser/helpers.py | 4 | >5 | >5 | 3 | >5 | >5 |

On these five proxies, dense cosine matched TF-IDF at P@1 and retrieved two rather than four proxy files in the top five. Its mean R@5 was 0.40 versus 0.80 for raw TF-IDF; MRR was 0.400 versus 0.550, and nDCG@5 was 0.400 versus 0.612. The lexical-semantic RRF retrieved three proxy paths at top five for raw queries and two for the enriched queries; it did not reach the raw TF-IDF result. Dense rankings were unchanged across the four query variants.

### Model and compute record

The local CPU model was sentence-transformers/all-MiniLM-L6-v2 at repository revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 (Sentence Transformers 5.7.0, Transformers 4.57.6, PyTorch 2.13.0+cpu; 384 dimensions). The run used exact NumPy cosine because FAISS was unavailable. The model directory SHA-256 is 3c9da5348bc316aa84664e33ac0590590c7fdfe12f2386a0dd513179b8b2393f.

Model initialization took 14.3290 seconds. Dense document embedding and vector-index construction took 594.7371 seconds across the five repositories (mean 118.9474 seconds; median 41.7316 seconds). The TF-IDF index builds in the same run took 1.1988 seconds total, so the dense index build took about 496 times as long on this CPU and these snapshots. Dense query retrieval averaged 0.0622 seconds per call (median 0.0543; max 0.1079), compared with 0.0362 seconds for TF-IDF. Lexical-semantic RRF averaged 0.1738 seconds per call because it combines rankings.

The complete five-method dense run took 670.2919 seconds and sampled peak Windows process-tree RSS of 932.89 MiB at 25 ms intervals. The sample may miss brief peaks. Pure model.encode time was not separately instrumented: dense index-build time includes document encoding and vector preparation, and retrieval latency includes query embedding, search, ranking, and file deduplication. These are the measured inference-related timings; no separate model-only inference value is claimed.

### Interpretation

For this five-case, unreviewed changed-file-proxy sample, dense cosine did not improve localization agreement and required substantially more CPU time and memory than the lexical baseline. Dense-plus-lexical fusion also scored below TF-IDF. Keep the model path optional and TF-IDF as the application default. This result is specific to this general-purpose model, CPU environment, repository set, and weak labels; it does not establish that dense retrieval is universally inferior.

## Cost and resource observations

The lexical run completed 60 rows in 7.8416 seconds. Mean per-row retrieval latency was 0.0268 seconds (median 0.0247; maximum 0.0786). Average lexical index construction time across the five unique snapshots was about 0.260 seconds. The index contained 1,233 to 3,162 chunks per repository.

The run's sampled peak Windows process-tree RSS was 192.35 MiB, sampled every 25 ms; short peaks can be missed. The mean retrieved-source size was 4,624.5 whitespace-separated words (median 3,431; maximum 11,320). This is an approximate source-size measure, not an LLM tokenizer count or a controlled equal-token context budget. No model calls or provider costs occurred.

## Limits

The five labels are unreviewed changed-file proxies derived from fixing-patch metadata, not exact fault locations. The source is the SWE-bench Lite development split, not the official test split. One additional PyVista candidate was excluded before indexing because its pinned archive exceeded the project's 100 MiB import limit. Repository selection and exclusion can affect representativeness.

No classifier accuracy, repair outcome, official SWE-bench score, statistical significance, or generalization claim follows from this pilot. The run does not compare semantic embeddings. See reports/experiments/REPRODUCIBILITY.md and research/THREATS_TO_VALIDITY.md.
