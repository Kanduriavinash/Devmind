# Evaluation result index

The current measured result is an exploratory retrieval pilot on five SWE-bench Lite development instances. Lexical results and the paired CPU dense comparison are reported in reports/experiments/RESULTS.md and preserved as separate raw JSONL runs in evaluation/raw_runs/. The machine-readable derived aggregate, including metrics, per-issue ranks, commits, hashes, resource data, and leakage audit, is swebench_lite_dev_pilot_20261117_dense_comparison.json.
The independent dense rerun is recorded as a separate JSONL and sidecar; all 100 ranked-file lists and metric objects exactly match the primary dense run.
File integrity digests for the inputs, raw runs, sidecars, summary, and experiment reports are listed in SHA256SUMS.txt.

Every relevance label is a changed-file proxy derived from a fixing patch. The five labels have not been independently reviewed, and they are not exact fault locations. The pilot does not establish classification quality, semantic-retrieval quality, repair accuracy, or official SWE-bench performance.

The two controlled QuickCart and Cricket Scorer fixtures remain separate historical demonstrations. Their selected tests passed in recorded Docker runs, but the changes do not confirm a bug in either current public repository and do not count toward the retrieval pilot.

No matched model-backed repair comparison, independently adjudicated resolution outcome, or official SWE-bench grade is available. Keep those outcomes pending in future reports. The complete reproduction protocol and limits are in reports/experiments/REPRODUCIBILITY.md.
