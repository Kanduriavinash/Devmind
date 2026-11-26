# Retrieval pilot dataset

## Source and selection

This exploratory sample uses the development split of SWE-bench Lite, downloaded from the dataset repository at revision b0dde1093fe417d83b7184254edf8199c1f0dff5. The source development Parquet contains 23 rows and has SHA-256 b90bcbfaca1b5f65155500124a977876c264a4003ab384aca4dfc39a54bef89f.

Before inspecting retrieval scores, the first source-order record for each of five distinct repositories was selected. Five base-commit archives were imported and hashed. A further PyVista candidate was excluded before indexing because its pinned archive exceeded DevMind's 100 MiB ZIP-import limit. No target repository code was executed.

The included benchmark task IDs are marshmallow-code__marshmallow-1343, pvlib__pvlib-python-1072, pydicom__pydicom-1139, astroid__astroid-1196, and sqlfluff__sqlfluff-1517. They map to opaque evaluation IDs pilot-01 through pilot-05 in the runtime input and raw records. Exact repository, base-commit, source title/body, fixing-PR provenance, and snapshot hashes are retained in issue_manifest.csv.

The source task identifiers refer to pull-request records rather than separate issue URLs, so issue_url is blank. The fixing PR URLs were verified through the GitHub API and remain in the provenance manifest only. The runtime input contains the benchmark problem statement and base snapshot identity; it does not contain fixing PR URLs, fix commits, patch contents, or post-fix source.

## Files and separation

- issue_manifest.csv is the provenance record and includes source task identifiers, repository, base commit, benchmark issue text, fixing-PR metadata, language, snapshot location, digest, source revision, and exclusion notes.
- evaluation_inputs.csv is the sanitized runtime input. It contains five issue records using opaque IDs and local base-snapshot paths.
- retrieval_ground_truth.csv contains one changed-file proxy label per issue. These labels were extracted from the benchmark fixing-patch changed paths. They are not independent human judgments or exact fault locations; reviewer and confidence fields remain blank.
- annotation_review_packet.csv is the sanitized five-issue worksheet for independent review. It contains only issue text, repository/base snapshot identity, and blank reviewer fields; fixing provenance and current proxy labels are excluded. Its `base_snapshot_path` values are local to the evaluation workspace. For reviewers on another machine, the packet's repository and full base commit identify the exact source to check out; `annotation_guidelines.md` gives safe retrieval and static-review steps. Give each annotator a separate blank copy and join completed labels only after retrieval rankings are frozen.
- annotation_template.csv is a legacy provenance-oriented template that includes fix metadata; do not use it for blind independent annotation. Use annotation_guidelines.md for the review procedure.

## Pilot run

The lexical run is evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl. The separate CPU dense comparison is evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu.jsonl. It repeats TF-IDF, BM25, and lexical RRF and adds Sentence Transformers cosine and lexical-semantic RRF over the exact same five issues, four query variants, top-k, inputs, labels, and base snapshots. It contains 100 completed rows. All supplied snapshot digests matched before indexing, and all 20 TF-IDF rankings and metrics match the primary lexical run.

The dense model is sentence-transformers/all-MiniLM-L6-v2 at pinned revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41. Model/runtime details, content hashes, timing, memory, and command are in the adjacent dense runmeta JSON. The derived comparison is evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json.

This is an exploratory, five-case file-proxy pilot. The dense-model result is specific to one general-purpose model and CPU configuration. It must not be described as a reviewed benchmark, exact bug-localization ground truth, or repair-accuracy result. Results are descriptive; no significance test or generalization claim is justified. No label has an independent reviewer or exact function-level fault-location annotation.

See reports/experiments/RESULTS.md and reports/experiments/REPRODUCIBILITY.md for metrics and protocol details.
