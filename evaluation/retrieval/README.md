# Retrieval evaluation

The evaluator applies the same four deterministic query variants to the same ordered repository chunks. It compares TF-IDF cosine, Okapi BM25 (k1=1.5, b=0.75), and equal-weight lexical reciprocal-rank fusion (RRF constant 60). Optional Sentence Transformers cosine and lexical-semantic RRF require an explicitly supplied local model; no model is downloaded by the CLI.

The runner records Precision@1/3/5, Recall@1/3/5, MRR, nDCG@1/3/5, retrieval latency, per-method index-build timing, ranked evidence, approximate retrieved-source whitespace-token counts, and snapshot hash evidence. Duplicate chunks from the same file are collapsed to the first-ranked file before file-level metrics are scored. RRF values are rank-fusion scores and cannot be compared numerically with cosine or BM25 scores.

## Current evidence

The five-instance SWE-bench Lite development pilot is stored in datasets/ and evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl. It covers five repositories, four query variants, and three lexical methods, for 60 completed records. All five base-snapshot content hashes were checked before indexing.

Each instance has one changed-file proxy derived from the fixing patch. No label was independently adjudicated. Scores measure agreement with this weak proxy, not confirmed fault localization. Results are descriptive for this selected five-case sample; no statistical significance or generalization claim is warranted.

See reports/experiments/RESULTS.md for the complete lexical table and per-issue analysis. The optional dense model comparison is reported only after the pinned model has actually been loaded and run; package installation alone is not a semantic retrieval result.

## Reproduction and controls

The exact command, CSV SHA-256 digests, Python environment, runtime, sampled process-tree RSS, stderr, and exit status are stored in the runmeta JSON adjacent to the raw JSONL. Run the same command from the project root:

    .venv\Scripts\python.exe -m devmind.retrieval_evaluation --inputs datasets/evaluation_inputs.csv --labels datasets/retrieval_ground_truth.csv --output evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl --top-k 5

The evaluator rejects unexpected input columns, keeping fix metadata out of ranking inputs. Snapshot content hashes are verified before indexing; mismatches and malformed digests are blocked. Empty digests are allowed only with an explicit unverified record.

Preserve raw records and exclusions. Keep changed-file proxies separate from human-reviewed file/function relevance labels. Report every failed or blocked condition. Do not infer causal improvement from point estimates on this five-case sample.
