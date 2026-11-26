# DevMind implementation and evidence status

**Last reviewed:** 19 November 2026  
This file separates implementation from behavior verified in recorded runs. Implemented code does not imply broad reliability.

## Implemented

- Deterministic, rule-based bug-report analysis, query normalization, identifier extraction, component hints, and four traceable query variants. No trained issue classifier is present.
- Static repository indexing with Python AST and lexical JavaScript/TypeScript extraction, including inline scripts in HTML and HTM. Target repository code is not executed during host indexing.
- Default TF-IDF retrieval with traceable file, symbol, and line evidence.
- Retrieval comparison infrastructure for TF-IDF, BM25, lexical RRF, optional local Sentence Transformers cosine, and lexical-semantic RRF.
- File-level precision, recall, MRR, and nDCG metrics; separate sanitized issue inputs and labels; rejection of unknown input columns; deterministic snapshot-directory hashing and pre-index hash verification.
- Optional model-backed investigation and candidate patch generation, structural patch validation, bounded repair attempts, and Docker-only disposable-copy tests when Docker is available.
- Failure-informed retries: bounded failure parsing, TF-IDF retrieval against the unchanged repository, run-local evidence IDs, per-attempt patch/test/evidence audit fields, and structured feedback that excludes raw stdout/stderr from the next provider prompt.
- Interactive Human Review Gate in Streamlit: candidate diffs require explicit operator confirmation (`[ ✅ Yes, Update Code in Files ]`) before applying changes to host disk, preserving host repository safety. Includes a live `[ 🔄 Reset Website to Buggy State ]` toggle for evaluator demonstrations.
- Bounded Self-Healing Stopping Limit: demonstrable preset (`Boundary limit test · Max 3 attempts limit demo`) showing deterministic halt after 3 failed container attempts with status `repair_attempt_limit_reached` and visible iteration trace.
- Local Streamlit interface, CLI, optional loopback-only API, JSON reports, history dashboard, and unpacked Manifest V3 Brave/Chrome launcher. Demo presets (QuickCart cart reload bug, Cricket Scorer, Safe Divide, Boundary Limit Test) auto-populate sample repositories, built-in bug reports, and matching test runners. Reference documentation includes `DEVMIND_MASTER_EXPLAINER.md` and `PROJECT_FILES_CHEATSHEET.md`.
- Public GitHub URL imports resolve the default branch to a full commit SHA, download the archive by that immutable SHA, and include the commit, archive SHA-256, branch, pushed timestamp, and skipped-symlink count in the saved analysis report. A live static import was completed for both presentation repositories; see `reports/github_repository_import_smoke_20261117.json`.
- SWE-bench Lite prediction adapter that writes untested proposals; it does not grade the official benchmark.

The repository-source selector regression was rechecked on 17 November 2026: the Streamlit UI tests returned 4 passed, including the immediate switch from local-folder input to the public GitHub URL field. The active local app on port 8501 returned HTTP 200 for the health and home routes, and all four JavaScript module URLs shown in the earlier error screenshots returned HTTP 200. This confirms current server/asset availability, not a full browser visual or GitHub-download end-to-end test; the reported client-side error was not reproduced.

The GitHub importer was exercised twice against `Kanduriavinash/QuickCart` and `Kanduriavinash/cricket-scorer-pro`. Both runs resolved the same full commit SHAs and archive hashes and returned identical evidence spans and scores, with eight traceable evidence chunks per repository. No source or tests were executed. At those revisions QuickCart restores cart state from localStorage and Cricket Scorer increments `matchState.balls` by one for ordinary deliveries. The described demo bugs are absent; use separate controlled buggy fixtures for a repair demonstration. This smoke does not demonstrate an upstream fix.

## Current retrieval evaluation

The development-split pilot contains five instances from five repositories, four query variants, and three lexical methods. Its hash-gated raw lexical run contains 60 completed rows. A separate CPU dense run contains 100 completed rows for five methods, including the paired TF-IDF baseline, dense cosine, and lexical-semantic RRF. The two TF-IDF runs have identical rankings and metrics for all 20 issue/variant pairs.
The independently rerun dense JSONL also matches all 100 primary dense ranked-file lists, metric dictionaries, query traces, and snapshot verification flags exactly. Its raw records and run sidecar are preserved separately.

All five labels are unreviewed changed-file proxies derived from fixing-patch paths. They are not function-level or exact fault-location annotations. No reviewer or confidence value is recorded. One additional PyVista candidate was excluded before indexing because its pinned archive exceeded the 100 MiB importer limit.

Dense all-MiniLM-L6-v2 at revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 scored Recall@5 0.40, MRR 0.400, and nDCG@5 0.400 against same-run raw TF-IDF at 0.80, 0.550, and 0.612. Dense document embedding and vector-index construction took 594.737 seconds; model initialization took 14.329 seconds; sampled peak process-tree RSS was 932.89 MiB. These are descriptive results on five proxy labels, not evidence of general semantic-retrieval quality.

Raw records, input/label hashes, model revision and directory hash, source fingerprints, resource measurements, per-issue ranks, and derived metrics are linked in reports/experiments/RESULTS.md and evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json.
The exact independent reproduction command and its deliberately unmeasured process-level resource fields are documented in reports/experiments/REPRODUCIBILITY.md.

## Verification

- Final full suite after the non-root sandbox implementation on 17 November 2026: `.venv\Scripts\python.exe -m pytest --tb=short -rs` — **179 passed, 3 skipped in 17.06 seconds**. All skips require Windows symlink-creation permission.
- Reproducible Docker smoke: `evaluation/sandbox_nonroot_smoke.py` reran the Python and Node known-patch fixtures. Both expected baseline failures changed to candidate passes under UID/GID `10001:10001`; both source fixture hashes remained unchanged. Raw records are `reports/sandbox-nonroot-docker-smoke-20261117.json` and `reports/sandbox-nonroot-docker-smoke-reproduction-20261117.json`.
- The local Streamlit application returned HTTP 200 for `/` and `/healthz` on `127.0.0.1:8501`. This is endpoint availability, not browser visual QA or a live model-backed end-to-end repair.
- `node --test browser-extension/tests/service-worker.test.mjs` returned 3 passed for GitHub URL prefill, non-GitHub launch, and unsafe URL fallback. The unpacked extension was not interactively loaded in Brave/Chrome.
- Built and inspected `dist/devmind-project.zip`; ZIP integrity check passed. It contains the raw retrieval runs and Docker integration evidence while excluding academic document files and local caches/environments.
- Pre-change baseline on 17 November 2026: 142 passed, 2 skipped. The skips required Windows symlink permission. See audit/BASELINE_TEST_RESULTS.md.
- Focused snapshot/model/evaluator regression tests after the hash gate and one-model reuse change: 13 passed in 0.70 second.
- Docker Desktop 29.9.1 responded after a restart. The QuickCart-like synthetic fixture failed its Node baseline test (expected), and a known repair patch passed 1/1 tests. A deterministic two-attempt `run_repair` test failed on attempt 1, parsed the failing test, retrieved `test/cart-reload.test.cjs` as new evidence, passed on attempt 2, and left the fixture tree hash unchanged. Raw run: `reports/quickcart-retry-docker-integration-20261117_v3.json`.
- A real Docker high-output smoke passed with `stdout_truncated=true`; the returned cleaned stdout tail was 3,999 characters after removing the internal marker. See `reports/sandbox-bounded-output-docker-20261117.json`.
- Local Qwen3 1.7B generated a structurally valid patch, but the exact diff did not apply in Docker (`git apply` failed at `index.html:27`), so no test executed. A follow-up Qwen request with focused evidence timed out after 180 seconds. These outcomes are separately recorded; no model-generated fix is claimed.
- The lexical pilot exited 0 with 60/60 completed records and all five snapshot hashes verified.
- The dense pilot exited 0 with 100/100 completed records and every supplied snapshot hash verified. It used CPU, PyTorch 2.13.0+cpu, ten Torch threads, no CUDA, and NumPy exact cosine because FAISS was unavailable.
- The dense run emitted a non-fatal SyntaxWarning while statically parsing the pvlib versioneer.py file. No target repository code was run.

## Known blockers and limitations

- Changed-file labels are weak proxies; no independently reviewed file/function relevance labels exist.
- The sample is only five development instances. No significance test, generalization claim, classifier score, repair accuracy, or official SWE-bench score is established.
- The dense model is general-purpose and was evaluated on one Windows CPU environment. Pure model.encode time was not isolated; dense index-build time includes document encoding and vector preparation, and retrieval latency includes query embedding and ranking.
- The Docker smoke verifies non-root container startup, patch application for known patches, test execution, and a deterministic failure-informed retry. Both language fixtures passed their known candidates under UID/GID `10001:10001` and retained unchanged source hashes. This does not prove isolation against malicious repositories or show that the local model can repair this bug. Streaming capture keeps retained stdout/stderr bounded, but test output is limited to its final 4,000 characters and may omit earlier diagnostics.
- The first live Qwen call was blocked because `DEVMIND_NODE_DOCKER_IMAGE` was not set in that process; its saved diff was then checked directly with the Node image and failed to apply. The correctly configured follow-up request timed out at 180 seconds.
- Public GitHub imports require unauthenticated API requests to GitHub; private repositories are unsupported. The new live smoke verifies exact snapshot provenance and static retrieval only. It did not exercise browser form submission, candidate generation, or sandbox repair against the presentation repositories.
- No matched model-backed repair comparison or independently adjudicated issue-resolution outcome exists.
- The workspace has no Git metadata, so no commit or feature branch is available. Source and test tree fingerprints are stored with the dense run metadata.
- The project virtual environment includes system site packages. Installing the optional embedding extra reported conflicts with unrelated base-environment packages; use a clean isolated environment for an independent reproduction.
- The workspace contains separately maintained academic report and presentation files. Their preparation and compilation are outside the current application delivery; the project archive excludes them.

## Next work

1. Have two team members independently annotate `datasets/annotation_review_packet.csv` using the base snapshots and annotation guidelines, without showing them the existing proxy labels. Reconcile disagreements only after both initial sheets are saved.
2. Expand the sample using a predeclared selection procedure and preserve all exclusions.
3. Run a matched model-backed comparison of LLM-only, one-shot retrieval-augmented, and iterative repair using the same issues, candidate budgets, and Docker tests; no adjudicated repair outcome currently exists.
4. Expand the retrieval sample using a predeclared selection rule and repeat the paired comparison; preserve exclusions and label provenance.
5. Complete two independent blind annotations and adjudicate disagreements before treating retrieval scores as localization quality. A formal sandbox security review and official SWE-bench grading also remain outstanding.

These items are pending; they must not be described as implemented or complete.
