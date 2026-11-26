# Query ablation

The query transformation implementation emits four reproducible conditions: raw issue text, normalized text, normalized text plus extracted keywords and identifiers, and a structured query that adds observed component/path hints and an observed non-default category when present. It preserves the original issue and records transformation details.

The SWE-bench Lite development pilot executes all four conditions for five selected tasks and three lexical methods. Results are in evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl and summarized in reports/experiments/RESULTS.md.

On these five unreviewed changed-file proxies, keyword/identifier enrichment moved one TF-IDF target from rank 4 to rank 3, increasing mean Recall@3 from 0.60 to 0.80. TF-IDF Recall@1 and Recall@5 did not change. BM25 and lexical RRF rankings were unchanged by that enrichment in this sample. These are descriptive observations only.

The proxy labels were created from fixing-patch changed paths, not independent fault-location annotations. Keep the four transformations paired on identical base snapshots and labels; do not put patch or fix metadata into the query. Extend the sample and independently review labels before drawing broader conclusions.
