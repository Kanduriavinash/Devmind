# Threats to validity

## Current evidence

The lexical retrieval pilot contains five SWE-bench Lite development instances from five repositories. It has one changed-file proxy label per instance and no independent fault-location review. It supports only descriptive statements about agreement with those five proxy paths.

## Construct validity

- A fixing-patch changed file may contain tests, refactoring, or supporting changes and does not identify the exact defective function. The score measures agreement with this file-level proxy, not whether DevMind found the true cause.
- Each issue has one included proxy file. Precision and recall therefore reflect a single target and top-k cutoff, not the complete set of relevant repository locations.
- A category produced by the deterministic Task Analyzer is not ground-truth issue classification. There are no independent classification labels.
- A passing selected test does not prove semantic correctness or complete issue resolution. The synthetic demonstrations are narrow controlled fixtures.
- The whitespace-separated context count is not a model-token count or an equal-token-budget comparison.

## Internal validity

- All lexical methods and query variants were paired on the same ordered chunks, top-k, issue text, and labels for each task. The recorded snapshot content hash was verified before indexing.
- Fixing PR URLs, fix commits, patch bodies, and post-fix code are kept outside the runtime query input. The changed-file proxy itself is held in a separate scoring file.
- The five-case run used benchmark problem statements and base-commit snapshots. One additional PyVista archive was excluded before indexing because it exceeded the configured 100 MiB archive limit.
- Query normalization, AST chunk extraction, lexical scoring, and deterministic file ordering can affect ranking. The raw run preserves transformation traces, file rankings, evidence spans, and the exact run metadata.
- The query variants are not statistically independent. Point-estimate differences on five paired cases do not establish a reliable effect.
- The source benchmark split is development. The results are not official SWE-bench task-resolution scores and were not produced by the official harness.

## External validity

- Five selected repositories and a Python-heavy historical benchmark sample cannot represent all languages, repository sizes, issue types, or development workflows.
- Results may change on issues with different wording, code organization, tests, or target-file multiplicity.
- The lexical resource measurement is from one Windows CPU environment. It cannot establish costs on other hardware.
- Sentence Transformers all-MiniLM-L6-v2 is a general sentence-embedding model, not a code-specific retriever. Its results and CPU costs must be reported as model-specific.
- Historical public benchmark issues may overlap language-model or embedding-model pretraining data. This pilot cannot rule out contamination.

## Conclusion validity

- No significance test is reported for the five-case sample. The observed Recall@3 change is descriptive and driven by a single rank movement.
- Method comparisons must remain paired and preserve all misses and exclusions. Do not infer that lexical RRF is better in general from its higher point estimates in this sample.
- A semantic-method result cannot be interpreted as a general semantic retrieval claim; it is tied to one model, snapshot, CPU configuration, and proxy label set.
- Retrieval ranking does not establish downstream patch quality. No matched repair-arm result or independently adjudicated resolution outcome exists.

## Reliability and security

- Docker Desktop could not start during the current audit. Historical synthetic runs do not prove current container isolation.
- Unit tests verify code contracts but not full security against malicious repositories, model outputs, or compromised dependencies.
- The workspace has no Git metadata, so the exact source commit and a rollback branch cannot be recorded.
- The optional dependency installation uses a virtual environment configured with system site packages. Pip reported conflicts with unrelated packages in the base installation; this is recorded in the current run documentation.
