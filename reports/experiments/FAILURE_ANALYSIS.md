# Retrieval pilot failure analysis

## Observed retrieval miss

In the primary five-case run, all three lexical methods missed the pydicom proxy path pydicom/valuerep.py in their top five. This occurred for all four query variants. The run records the complete rankings in evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl. With one proxy label per issue, this single miss accounts for the observed Recall@5 of 0.80.

No cause is assigned to the pydicom miss because this pilot did not perform a manual relevance review of the retrieved alternatives. A follow-up should inspect the issue wording, indexed chunk text, target file representation, and plausible neighboring files, then record the reviewer and rationale separately from the original proxy metric.

The other four proxy paths appeared within the top five for each lexical method and query condition. A changed-file match is still only agreement with the weak label; it is not proof that the retrieved function contains the true defect.

## Dataset exclusion

One additional candidate from PyVista was excluded before indexing because its base-commit ZIP exceeded the importer's 100 MiB archive limit. The exclusion is recorded in datasets/issue_manifest.csv. It was not excluded based on retrieval outcome and contributes no result row.

## Execution notes

The authoritative run completed all 60 issue/variant/method rows with matching snapshot hashes. The pvlib snapshot emitted a non-fatal Python SyntaxWarning from versioneer.py while DevMind statically parsed source. No repository source was imported or executed.

Several preliminary raw files are preserved under evaluation/raw_runs/superseded_provenance_checks/. They exposed provenance, anonymization, or hash-gating issues in the protocol and are excluded from primary metrics. The folder README describes each correction.

## Unobserved failure classes

This pilot only evaluated lexical rankings. It did not generate or test patches and therefore provides no counts for model timeouts, invalid diffs, patch application, test failures, or issue resolution. The existing SWE-bench smoke and synthetic fixture records remain separate evidence and are not pooled into these retrieval results.
