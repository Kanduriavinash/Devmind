# Retrieval pilot reproducibility record

**Run date:** 17 November 2026  
**Scope:** Five-repository SWE-bench Lite development-split retrieval pilot  
**Source limitation:** Workspace has no Git metadata; source-tree content fingerprints are recorded instead of a Git commit.

## Dataset and selection

Source: SWE-bench/SWE-bench_Lite at revision b0dde1093fe417d83b7184254edf8199c1f0dff5. The development Parquet used for selection has SHA-256 b90bcbfaca1b5f65155500124a977876c264a4003ab384aca4dfc39a54bef89f. One first-source-order record per repository was selected before inspecting retrieval scores. Five instances were included; one additional PyVista archive was excluded before indexing because it exceeded the 100 MiB import limit.

| Evaluation ID | Repository | Base commit | Snapshot SHA-256 | Proxy path |
|---|---|---|---|---|
| pilot-01 | marshmallow-code/marshmallow | 2be2d83a1a9a6d3d9b85804f3ab545cecc409bb0 | ef3246f5237d09b497dcea471a8c3ac2b82e627e6cd3fa1446c12ae291d648c0 | src/marshmallow/schema.py |
| pilot-02 | pvlib/pvlib-python | 04a523fafbd61bc2e49420963b84ed8e2bd1b3cf | 68c9951af9c69d037abcdc6ec2800ffdee735f4ae21e19a1bc51272de5173a5b | pvlib/temperature.py |
| pilot-03 | pydicom/pydicom | b9fb05c177b685bf683f7f57b2d57374eb7d882d | 55065620aed3f0c18b5d26612b8ad9de262a04ac7a213508d839cab3048efb0f | pydicom/valuerep.py |
| pilot-04 | pylint-dev/astroid | 39c2a9805970ca57093d32bbaf0e6a63e05041d8 | af81367b2d99162b04fcb7659bf583aeb86d589487565a8730161f43ce7a7c86 | astroid/nodes/node_classes.py |
| pilot-05 | sqlfluff/sqlfluff | 304a197829f98e7425a46d872ada73176137e5ae | 78cc37316dd845fe1171e9ff2a8c35127f89b621f9c69aec5efe3a309bc3bf13 | src/sqlfluff/core/parser/helpers.py |

The proxy paths were extracted from fixing-patch changed paths. There is one proxy per issue, no independently reviewed labels, no reviewer/confidence values, and no function-level ground truth. The issue bodies are taken from the benchmark problem statements. The task records map to pull-request pages; issue_url is blank.

## Leakage and snapshot checks

- The sanitized runtime input has exactly the allowed issue/repository/base-commit/text/snapshot fields. It contains no fixing PR URL, fixing commit, patch, test patch, or post-fix source field.
- Included fixing-commit fields in the provenance manifest are blank. Fixing PR URLs are retained only in that manifest; none appears in the runtime input or raw run records.
- The retrieval runner receives the base snapshot and generated issue query. It creates rankings before passing the separate relevant-path set to the metric scorer.
- Each supplied base snapshot digest was checked by the evaluator before indexing. All 60 lexical records and all 100 dense records have snapshot_hash_verified=true, and each actual digest matches the expected digest.
- Each snapshot is the bounded public archive imported at the task's base_commit; symlinks_skipped=0 for the five included snapshots. No repository source was imported as a Python module or executed.
- The same-run dense JSONL recomputes the TF-IDF baseline. All 20 issue/variant TF-IDF rankings and metric objects exactly match the separately preserved lexical run.

The code path can be inspected in src/devmind/retrieval_evaluation.py and src/devmind/retrieval_experiment.py. The label is used by score_file_ranking only after each index.search call has produced its ranking.

## Model and environment

- Model: sentence-transformers/all-MiniLM-L6-v2, pinned revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41; Apache-2.0; 384-dimensional output.
- Model directory SHA-256: 3c9da5348bc316aa84664e33ac0590590c7fdfe12f2386a0dd513179b8b2393f.
- Sentence Transformers 5.7.0; Transformers 4.57.6; PyTorch 2.13.0+cpu; NumPy 2.2.2; Python 3.12.5; Windows 11 build 26300.
- CPU only, ten PyTorch threads, CUDA unavailable, FAISS unavailable. Exact NumPy cosine was used.
- Dense evaluation reused one loaded model object across all five snapshots.
- The editable extras install reported conflicts with unrelated packages visible via system-site-packages. Use a clean isolated environment for reproduction.

## Input and label digests

- datasets/evaluation_inputs.csv: SHA-256 12ee4a2b50ed25851ddf26eb9db8ad9b5f0c2d70cfb4acb470385b5149724df7
- datasets/retrieval_ground_truth.csv: SHA-256 56d01974dfa148ec47c6896ceb6904d46874ea86281ed320a450e0d23fbfc04a

## Installation and model download

Use Python 3.12 in a clean virtual environment. Install the optional embedding dependencies, then download the model at the exact revision into a local ignored cache:

    python -m pip install -e ".[embeddings]"
    python -c "from huggingface_hub import snapshot_download; print(snapshot_download(repo_id='sentence-transformers/all-MiniLM-L6-v2', revision='1110a243fdf4706b3f48f1d95db1a4f5529b4d41', local_dir='.devmind/models/all-MiniLM-L6-v2'))"

The evaluator itself never downloads model files. Do not add the model cache to a release archive.

## Commands

Primary lexical run:

    .venv\Scripts\python.exe -m devmind.retrieval_evaluation --inputs datasets/evaluation_inputs.csv --labels datasets/retrieval_ground_truth.csv --output evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl --top-k 5

Paired dense comparison:

    .venv\Scripts\python.exe -m devmind.retrieval_evaluation --inputs datasets/evaluation_inputs.csv --labels datasets/retrieval_ground_truth.csv --output evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu.jsonl --top-k 5 --embedding-model .devmind/models/all-MiniLM-L6-v2

The evaluator refuses to overwrite existing output files. The dense run metadata stores the command, exit code, input/label hashes, model identity, model-directory digest, source fingerprints, and resource observations.

Independent dense-ranking replication (separate raw output):

    .venv\Scripts\python.exe -m devmind.retrieval_evaluation --inputs datasets/evaluation_inputs.csv --labels datasets/retrieval_ground_truth.csv --output evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu_replication.jsonl --top-k 5 --embedding-model .devmind/models/all-MiniLM-L6-v2

The second process completed with exit code 0. A key-by-key comparison found exact equality for all 100 ranked-file lists, metrics, query traces, and snapshot hashes/verification flags. The independent output and its sidecar are separate from the primary run. Its sidecar records model-load and per-record retrieval/index-build timings but explicitly leaves process-level elapsed time and peak memory unavailable; use the primary sidecar for the sampled resource measurements.

## Timings and memory

For the dense run:

- Model initialization, including the lazy Sentence Transformers import and model load: 14.329032 seconds.
- Dense document embedding and vector-index construction: 594.737142 seconds total. Per repository: marshmallow 22.611218 s; pvlib 32.374030 s; pydicom 55.550675 s; astroid 442.469654 s; sqlfluff 41.731565 s.
- TF-IDF index construction in the same process: 1.198795 seconds total.
- Mean per-query retrieval call: TF-IDF 0.0362 s; dense cosine 0.0622 s; lexical-semantic RRF 0.1738 s.
- Total CLI evaluation time: 670.2919 seconds.
- Peak Windows process-tree RSS: 932.89 MiB, sampled every 25 ms over 7,901 samples. Brief peaks can be missed.

The runner does not isolate raw model.encode duration. Dense index-build timing includes document encoding, vector validation, normalization, and index preparation; query retrieval timing includes query embedding, vector scoring, ranking, and file deduplication. These are the exact measured inference-related intervals. A separate model-only inference duration is unavailable and is not fabricated.

## Raw and derived artifacts

- Lexical raw records: evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl
- Lexical run metadata: evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_runmeta.json
- Dense raw records: evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu.jsonl
- Dense run metadata: evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu_runmeta.json
- Independent replication raw records and metadata: evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu_replication.jsonl and evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu_replication_runmeta.json
- Machine-readable comparison: evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json
- SHA-256 integrity manifest: evaluation/results/SHA256SUMS.txt
- Human-readable metrics and interpretation: reports/experiments/RESULTS.md

The raw records are separate and append-only. No significance test or generalization claim is supported by five unreviewed proxy labels.

## Regression verification

After the evaluator/model-reuse changes, the focused command `.venv\Scripts\python.exe -m pytest tests/test_embeddings.py tests/test_retrieval_experiment.py tests/test_retrieval_evaluation_cli.py --tb=short -rs` returned **13 passed in 0.70 s**. The latest full project suite, after failure-informed retry and bounded streaming output changes, returned **178 passed, 3 skipped in 5.75 s** with `.venv\Scripts\python.exe -m pytest --tb=short -rs`; all three skips require Windows symlink-creation permission. A second CPU process independently reproduced the 100 dense-run ranking/metric rows exactly, but no clean independent-machine reproduction has been performed. Later Docker and local-model repair checks are separate controlled-fixture records in `reports/` and do not alter the retrieval metrics.
