# Superseded pilot protocol checks

These append-only exploratory outputs are retained for audit but are not included in the reported metrics. The primary result is the later hash-gated, anonymized run at evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl.

- pre_url_correction_uninstrumented.jsonl and pre_url_correction_resource.jsonl were produced before GitHub API verification showed that the benchmark task IDs mapped to pull-request URLs, not issue URLs. The latter has process resource metadata.
- url_corrected_confidence_field_unreviewed.jsonl corrected the PR provenance but preceded final label cleanup. No human review occurred; the confidence field must not be interpreted as adjudication.
- corrected_labels_pre_hash_gate.jsonl used corrected label paths but was recorded before the evaluator enforced snapshot digest verification.
- pre_anonymization_hash_verified.jsonl verified snapshot hashes, but retained identifiable task IDs and paths in raw input records. It was superseded by the opaque-ID run.
- Run metadata is retained beside outputs where it was captured. The uninstrumented first check has no runmeta file.

These rows are evidence of protocol refinement, not additional independent samples. Do not pool them with the authoritative pilot or use them as a validation set.
