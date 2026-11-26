# Application and experiment acceptance checklist

**Status reviewed:** 17 November 2026  
This checklist covers the DevMind application and its existing experiments. Academic report and presentation preparation are handled separately and are not release requirements here.

| Requirement | Status | Evidence and remaining limit |
|---|---|---|
| Understand the existing project and preserve its local workflow | Implemented and audited | See audit/FEATURE_IMPLEMENTATION_MATRIX.md, MANUAL.md, and docs/ARCHITECTURE.md. No Git metadata exists, so there is no source commit or feature branch. |
| Describe Text Analytics accurately | Implemented | The analyzer is deterministic and rule-based. No independent classification labels or classifier-performance metrics exist. |
| Emit traceable query variants | Implemented and unit-tested | Four deterministic variants retain original text and transformation traces. |
| Compare retrieval on real issue records | Exploratory pilot completed | Five SWE-bench Lite development instances, five repositories, four query variants, five methods in the dense run. Every label is an unreviewed changed-file proxy. No exact location ground truth or generalization claim. |
| Compare dense retrieval with TF-IDF on identical inputs | Completed for the five-case pilot | Same-run TF-IDF and dense records use the same issues, query variants, base snapshots, top-k, and separate labels. Dense did not improve proxy metrics and used substantially more CPU time. See reports/experiments/RESULTS.md. |
| Prevent fix-data leakage into retrieval | Verified for the pilot protocol | Runtime input schema contains no fixing PR or commit fields; base snapshots are pinned and content-hash verified; labels are applied after ranking for scoring. See the dense run metadata and comparison JSON. |
| Preserve raw experimental evidence and reproduction details | Completed for current pilot | Separate lexical and dense JSONL files and sidecars are in evaluation/raw_runs/. Inputs, labels, manifests, and summary JSON are in datasets/ and evaluation/results/. A clean independent-machine reproduction has not been performed. |
| Import a public GitHub URL reproducibly | Reproduced on two presentation repositories | `evaluation/live_github_import_smoke.py` and its two JSON records show identical commit SHAs, archive SHA-256 values, evidence spans, and scores across runs. This verifies static import/retrieval only; no target code or tests ran, and the current repositories do not contain the described demo bugs. |
| Establish reliable human ground truth | Pending; blind review packet prepared | `datasets/annotation_review_packet.csv` contains the five sanitized issue reports and blank reviewer fields, without fix metadata or current proxy labels. Two independent reviews and adjudication are still required; existing labels remain changed-file proxies. |
| Evaluate classification quality | Pending | No independently labelled text analytics dataset exists. |
| Compare LLM-only, RAG-only, and iterative repair outcomes | Pending | No matched model-backed runs or adjudicated outcomes. |
| Grade SWE-bench predictions | Pending | The adapter creates untested predictions only; the official grading harness has not run. |
| Verify Docker isolation and current repair integration | Non-root synthetic smoke completed; formal security review pending | Both images report UID/GID `10001:10001`; Python and Node baseline tests failed as expected, known candidates passed, and fixture hashes remained unchanged. See `reports/sandbox-nonroot-docker-smoke-20261117.json`. This is not a formal isolation proof. |
| Re-retrieve evidence after failed sandbox tests and preserve attempt audit fields | Implemented, unit-tested, and live-smoke-tested | The deterministic Docker retry proves failure parsing, TF-IDF retrieval of new test evidence, and per-attempt capture. The provider was a deterministic fixture; the separate Qwen attempt failed diff application and a follow-up timed out. |
| Bound sandbox subprocess output memory | Implemented and verified with unit and live Docker checks | Two reader threads drain stdout/stderr continuously and retain only 4,000 characters per stream; truncation and execution-marker state are tracked independently. A noisy Node container completed with `stdout_truncated=true`, a 3,999-character cleaned tail, and a passing test. See `reports/sandbox-bounded-output-docker-20261117.json`. |
| Run the complete current regression suite | Completed for current source | `.venv\Scripts\python.exe -m pytest --tb=short -rs` returned 179 passed, 3 skipped in 17.06 seconds on 17 November 2026. Three skips require Windows symlink permission. |
| Verify Docker sandbox execution for supported fixture languages | Non-root synthetic smoke completed | Python and Node baselines failed as expected; known candidates passed under UID/GID `10001:10001`; both fixture trees remained unchanged. Raw evidence is in `reports/sandbox-nonroot-docker-smoke-reproduction-20261117.json`. This is not a formal isolation audit or a model-repair success claim. |
| Verify the main app service | Endpoint and source-selector checks completed | Streamlit `/` and `/healthz` returned HTTP 200 on `127.0.0.1:8501`; `tests/test_streamlit_app.py` verifies the GitHub selector changes its input. Browser-based end-to-end repair was not verified. |
| Verify extension launch and repository prefill logic | Automated extension tests passed | `node --test browser-extension/tests/service-worker.test.mjs` returned 3 passed. Loading the unpacked extension and clicking it in Brave/Chrome was not interactively verified in this run. |
| Build a clean source-and-evidence archive | Completed | `dist/devmind-project.zip` passed ZIP integrity validation and contains the raw retrieval and Docker evidence. It excludes academic documents, caches, local environments, and model artifacts. |
| Academic report and presentation | Outside this application delivery | The user will prepare the final academic report separately. No report or presentation compilation is required for this project ZIP. |

## Current verification commands

Focused retrieval-evaluation regression command:

    .venv\Scripts\python.exe -m pytest tests/test_embeddings.py tests/test_retrieval_experiment.py tests/test_retrieval_evaluation_cli.py --tb=short -rs

Previously observed result after retrieval evaluator changes: 13 passed in 0.70 second. The latest full suite returned 179 passed and 3 Windows symlink skips in 17.06 seconds. The dense primary and replication files match on all non-timing record fields. All entries in the current project evidence and integration manifests verified successfully.

Dense run command, with the pinned model already present locally:

    .venv\Scripts\python.exe -m devmind.retrieval_evaluation --inputs datasets/evaluation_inputs.csv --labels datasets/retrieval_ground_truth.csv --output evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu.jsonl --top-k 5 --embedding-model .devmind/models/all-MiniLM-L6-v2

The raw run metadata records model revision, resource data, input/label hashes, source fingerprints, and process outcome. No fixing patch or post-fix source was passed to the indexer.
