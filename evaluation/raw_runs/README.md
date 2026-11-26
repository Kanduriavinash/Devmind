# Raw run records

Keep one immutable JSONL row per run condition. Retain failures, empty rankings, blockers, and exclusions. Do not overwrite a prior run to correct provenance or protocol; preserve it and explain the correction.

## Primary lexical pilot

The current authoritative retrieval file is swebench_lite_dev_pilot_20261117_anonymized.jsonl. Its run metadata is swebench_lite_dev_pilot_20261117_anonymized_runmeta.json. The run contains 60 completed records for five opaque issue IDs, four query variants, and three lexical methods. Snapshot hashes were verified before indexing.

## Dense-model comparison

The separate run swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu.jsonl contains 100 completed records for the same five issues, four query variants, and five methods: TF-IDF, BM25, lexical RRF, Sentence Transformers cosine, and lexical-semantic RRF. It recomputes TF-IDF on the same snapshots and labels; all 20 query/TF-IDF rankings and metrics match the primary lexical run. Every snapshot digest was verified.

Its sidecar swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu_runmeta.json records the exact command, exit status, elapsed time, sampled peak RSS, model revision and directory digest, model load time, source fingerprints, and runtime versions. The derived aggregate is evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json. The detailed interpretation is in reports/experiments/RESULTS.md.

A separate independent CPU rerun is preserved as swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu_replication.jsonl with sidecar swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu_replication_runmeta.json. All 100 issue/variant/method keys, ranked-file lists, metric objects, query traces, and snapshot verification flags exactly match the primary dense run. Process-level elapsed time and memory were not sampled on this repeat; its sidecar marks these values unavailable.

Earlier protocol iterations are kept in superseded_provenance_checks/ with a README explaining why they are excluded from primary metrics.

## Required run metadata

Record dataset revision and issue IDs, base commits and snapshot hashes, query transformation version, retrieval/model configuration, top-k and context budget, exact command, input and label file hashes, completed/blocked status, latency, resource measurement method, output path, and limitations. Use null where a value was not measured. Keep test output, provider usage, token counts, and cost only when observed.

The checked-in run metadata records exact commands and CSV digests, elapsed time, process-tree RSS sampled every 25 ms, exit code, stderr, and verification notes. It reports approximate whitespace-token counts, not tokenizer counts. The dense timing records dense index construction and query retrieval; pure model.encode time was not isolated.

No target repository source or model output may be executed on the host.
