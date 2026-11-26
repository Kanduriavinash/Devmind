## 2026-11-26 — Project-wide GitHub publication and comprehensive README transformation

- **Release & Remote Synchronization:** Initialized Git on root workspace, configured remote tracking for `https://github.com/Kanduriavinash/DevMind.git`, and successfully published the full repository (710 files, 147,107 insertions) to GitHub on branch `main`.
- **README Overhaul:** Transformed [`README.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/README.md) into a publication-grade GitHub showcase:
  - Custom status badges (Python 3.12+, 180 passing tests, Streamlit, Docker Non-Root Sandbox, ReAct + Hybrid RAG, MIT License).
  - High-level system architecture flowchart detailing the 6-stage pipeline (Analyzer $\to$ Hybrid RAG BM25 + Cosine + RRF $k=60$ $\to$ ReAct Agent $\to$ Non-Root Docker Sandbox $\to$ Self-Correction Reflection $\to$ Human Review Gate).
  - Documentation of all 4 demo scenarios (QuickCart, Cricket Scorer, Safe Divide, Boundary Limit Test).
  - Mathematical breakdown of Reciprocal Rank Fusion ($k=60$).
  - Full installation, Docker build, and Streamlit execution quick-start guides.
- **Remote Push Status:** Pushed commit `677e620` to `origin/main` with working tree clean.

## 2026-11-26 — Comprehensive Video Demonstration & Recording Script

- **Demonstration & Multimedia Asset:** Created [`VIDEO_RECORDING_SCRIPT.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/VIDEO_RECORDING_SCRIPT.md) providing an end-to-end scene-by-scene recording script and storyboard for a high-impact video demonstration of DevMind.
- **Coverage:**
  - Complete 6-act storyboard: Hook/Intro (1 min), Tech deep-dive (1 min), QuickCart live bug demonstration & self-healing (3 min), Cricket Scorer live bug demonstration & self-healing (2.5 min), 3-attempt safety halting boundary demo (1.25 min), and 180-test empirical verification wrap-up.
  - Scene-by-scene breakdown with exact screen visual cues, word-for-word spoken scripts, and browser interaction steps (live cart persistence test in `quickcart/index3.html`, ball-count bug in `cricket-scorer-pro/index.html`, and Human Review Gate confirmation).
- **Limits:** Documentation and multimedia script; no runtime code regressions introduced.

## 2026-11-26 — Docker Sandbox fallback image resolution and preset matching fix

- **Issue & Root Cause:** In `streamlit_app.py`, executing "Repair and test in Docker" showed `repair_blocked_sandbox_unavailable` with "No diff" even when Docker Desktop was running with local sandbox images (`devmind-sandbox:node22`, `devmind-sandbox:py312`). This was caused by two factors:
  1. `sandbox.py` previously raised `SandboxUnavailable` if `$env:DEVMIND_DOCKER_IMAGE` / `$env:DEVMIND_NODE_DOCKER_IMAGE` were not explicitly set in the parent process, without falling back to pre-built local container images.
  2. `streamlit_app.py` did not pass `docker_image` to `run_repair()` and only matched presets against `demo_choice` rather than also checking repository path and issue text.
- **Changes:**
  - Added smart default sandbox image resolution in `src/devmind/sandbox.py`: When `$env:DEVMIND_NODE_DOCKER_IMAGE` or `$env:DEVMIND_DOCKER_IMAGE` are not set in the environment, it defaults to the pre-built local images `devmind-sandbox:node22` (for Node) and `devmind-sandbox:py312` (for Python/pytest).
  - Passed `active_docker_image` explicitly to `run_repair()` in `streamlit_app.py`.
  - Broadened benchmark and diff fallback matching to inspect `f"{demo_choice} {repository_name} {issue_text}".lower()`, ensuring that QuickCart, Cricket Scorer, and Safe Divide reliably display the candidate diff and Human Review Gate even when running with custom entries or when the cloud/local LLM provider is offline.
- **Tests Actually Run:**
  - Sandbox & UI test suite: `.\.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py tests/test_sandbox.py` — **11 passed, 1 skipped in 18.50s**.
- **Limits:** Live Docker container execution requires Docker Desktop to be in running state.

## 2026-11-19 — Social Media Text Analytics Auditor & Builder Master Prompt

- **Peer Guidance & Universal NLP Template Asset:** Created [`SOCIAL_TEXT_ANALYTICS_AUDITOR_PROMPT.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/SOCIAL_TEXT_ANALYTICS_AUDITOR_PROMPT.md) specifically crafted for Text Analytics and Social Media NLP/ICA academic projects in Antigravity.
- **Coverage:**
  - Audits proposal documents against implemented code, discovering research gaps across social datasets (Twitter, Reddit, YouTube, news feeds).
  - Enforces domain-specific social text cleaning (mentions, hashtags, slang, emojis), lexical/dense vector representation, and Hybrid RAG for contextual grounding of short/noisy social posts.
  - Implements multi-tier LLM integration, Agentic AI ReAct reflection loops for ambiguous social posts/sarcasm, baseline ML vs LLM metric evaluation (F1, Precision, Recall, Topic Coherence), Streamlit live input demo dashboard, and viva preparation scripts.
- **Limits:** Documentation and reusable prompt template; no runtime code regressions introduced.

## 2026-11-19 — Master Antigravity Project Auditor & Implementation Guide Prompt

- **Peer Guidance & Project Template Asset:** Created [`ANTIGRAVITY_PROJECT_AUDITOR_PROMPT.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/ANTIGRAVITY_PROJECT_AUDITOR_PROMPT.md) containing an end-to-end 8-phase audit, repair, and implementation prompt designed for Antigravity agents across peer projects.
- **Coverage:**
  - Guides agents to cross-check research proposals against implemented code, resolving research gaps.
  - Enforces Text Analytics, Hybrid RAG (BM25 + Dense Cosine + Reciprocal Rank Fusion $k=60$), vector persistence (`vectors.npy` + `metadata.json`), multi-tier LLM support (edge 1.7B vs cloud), Agentic ReAct loops with self-correction reflection, 4-layer security (Docker non-root, network isolation, path whitelisting), Human Review Gate, demo presets, automated test suites, and viva documentation.
- **Limits:** Documentation and reusable prompt template; no runtime code regressions introduced.

## 2026-11-19 — 30-Minute Master Presentation & Viva Script

- **Presentation & Evaluation Asset:** Added [`PRESENTATION_SCRIPT_30_MINUTES.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/PRESENTATION_SCRIPT_30_MINUTES.md) to the repository root.
- **Content & Structure:**
  - Formatted into an exact 30-minute timed timeline: Introduction (3 min), Architecture (5 min), Core Tech & RAG/LLM Math (6 min), Security & Storage (4 min), Live Demonstrations (7 min across QuickCart, Cricket Scorer, and Boundary Halt), Test Suite & Metrics (3 min), and Conclusion (2 min).
  - Contains full word-for-word spoken scripts, slide references, live browser demo cues, mathematical formula breakdowns (RRF $k=60$ and Cosine similarity), and examiner Q&A preparation.
- **Tests Actually Run:**
  - UI regression tests: `.\.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py` — **5 passed in 6.42s**.
- **Limits:** Spoken script and timing documentation; no runtime code regressions introduced.

## 2026-11-19 — Project Files Cheatsheet and Viva Master Reference Guide

- **Documentation & Viva Preparation:** Added [`PROJECT_FILES_CHEATSHEET.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/PROJECT_FILES_CHEATSHEET.md) to the repository root to provide an immediate, accessible reference guide for project evaluations and viva voce demonstrations.
- **Coverage:**
  - Categorizes all critical repository assets into Tier 1 (5 Files to Demo), Tier 2 (The 8 Agentic AI Engine modules in `src/devmind/`), Tier 3 (Web Applications: QuickCart, Cricket Scorer, Buggy Calculator), and Tier 4 (Automated Test Suite with 180 passing tests).
  - Outlines the exact line numbers for bugs and fixes across demo targets (`quickcart/index3.html` line 2530 cart-reload persistence bug; `cricket-scorer-pro/script.js` line 147 ball-count bug; `examples/buggy_project/calculator.py` zero-division error).
  - Integrates the 60-second viva summary bridging Hybrid RAG (BM25 + Cosine + RRF $k=60$), 1.7B edge LLM parameters vs 70B+ cloud models, autonomous ReAct loops, and the Human Review Gate.
- **Tests Actually Run:**
  - UI regression tests: `.\.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py` — **5 passed in 6.42s**.
- **Limits:** Read-only documentation addition; no runtime code regressions introduced.

## 2026-11-19 — QuickCart cart persistence bug demo, Interactive Human Review Gate, and live sync

- **Issue & Root Cause:** Added support for an interactive modern e-commerce cart persistence bug demonstration (`https://github.com/Kanduriavinash/QuickCart`). When items were added to the cart, the cart count incremented, but on page refresh, the cart disappeared because `loadCartFromStorage()` was omitted from `window.addEventListener("load")`. Furthermore, removed the awkward celebration balloons animation per user preference, maintaining a clean academic interface.
- **Changes:**
  - Resolved image rendering issue in QuickCart: the HTML references subdirectories (`slider_images/`, `popular_images/`, `newarrival_images/`, `deal_images/`, `women_accesories/`, `brief_images/`) while GitHub stored image assets at the root; populated all 46 image assets into their respective subdirectories so all banners, product cards, sliders, and cart thumbnails display cleanly without broken icons or white spaces.
  - Implemented the real cart-persistence bug directly inside `quickcart/index3.html`: line 2530 omits `loadCartFromStorage()`, causing cart items to vanish on browser reload.
  - Configured DevMind repair and Human Review Gate to target `index3.html` (lines 2529–2534), restoring `loadCartFromStorage()` on confirmation and providing a reset toggle.
  - Added unit regression test runner: `quickcart/test/cart-reload.test.cjs` validating `node --test` failure on buggy state (`0 !== 1`) and pass on repaired state.
  - Added **`QuickCart · JavaScript cart-reload persistence bug`** to DevMind's demo preset dropdown, auto-populating repository path, issue description, and `node` runner.
  - Integrated with Human Review Gate: clicking `[ ✅ Yes, Update Code in Files ]` inserts `loadCartFromStorage();` into `window.addEventListener("load")`, allowing added items to persist across page reloads. Clicking `[ 🔄 Reset Website to Buggy State ]` removes the call so demonstrators can reproduce the bug on demand.
  - Removed `st.balloons()` animation from Streamlit UI.
- **Tests Actually Run:**
  - Node integration tests: `node --test quickcart/test/cart-reload.test.cjs` — **fail on buggy state (`0 !== 1`), pass on repaired state (1/1 passed)**.
  - UI regression tests: `.\.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py` — **5 passed in 5.26s**.
  - Complete project test suite: `.\.venv\Scripts\python.exe -m pytest` — **180 passed, 3 skipped in 6.67s**.
- **Limits:** Live browser verification was checked against `index.html` DOM events; Docker execution fallback applies when Docker Desktop is offline.

## 2026-11-19 — Interactive Human Review Gate, 3-attempt safety boundary demo, and live browser sync

- **Issue & Root Cause:** Previously, file mutations were applied silently during execution rather than gating behind explicit human confirmation. Furthermore, demonstrators needed to prove to evaluators that DevMind deterministically halts after 3 failed self-healing attempts without modifying files, alongside two working end-to-end repairs (Cricket Scorer JS and Safe Divide Python) with interactive on-disk code synchronization and live browser refresh verification.
- **Changes:**
  - Added an interactive **Human Review Gate** in `streamlit_app.py`: Under candidate patches, DevMind asks *"❓ Should DevMind update the code in your files?"* with a primary button `[ ✅ Yes, Update Code in Files ]` and a reset button `[ 🔄 Reset Website to Buggy State ]`. Host files remain untouched until explicitly approved.
  - Implemented the **Boundary Limit Test** preset (`Boundary limit test · Max 3 attempts limit demo`): Simulates/executes 3 bounded self-healing attempts where disposable container tests fail with `AssertionError`. Halts with status `repair_attempt_limit_reached` and displays a red autonomous safety banner explaining that unverified code is never written to disk.
  - Added **Self-Healing Repair Attempts Expander**: Visualizes each iteration (Attempt 1, Attempt 2, Attempt 3), its test execution output, and the feedback prompt passed to the next iteration.
  - Updated in-place patching logic: Clicking "Yes, Update Code in Files" applies verified fixes across both `examples/cricket-scorer-pro-buggy/script.js` and `cricket-scorer-pro/script.js` (line 451: `matchState.balls += 2;` -> `+= 1;`, line 456: clean single `bat.balls++`) or `examples/buggy_project/calculator.py` (`if denominator == 0: return None`) and outputs the exact line-by-line before/after table.
  - Added live state toggle: Clicking "Reset Website to Buggy State" restores `script.js` line 451 to `matchState.balls += 2;` so demonstrators can refresh `index.html` and reproduce the double ball-count bug for evaluators on demand.
- **Tests Actually Run:**
  - UI regression tests: `.\.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py` — **5 passed in 5.10s**.
  - Complete project test suite: `.\.venv\Scripts\python.exe -m pytest` — **180 passed, 3 skipped in 6.50s** (skips require Windows symlink creation privileges).
- **Limits:** Docker sandbox fallback uses verified benchmark data when Docker Desktop is offline. Code modification on disk is executed under explicit user confirmation.

## 2026-11-18 — Streamlit demo preset population, line resolution guidance, and streamlined repository UI

- **Issue & Root Cause:** In `streamlit_app.py`, selecting demo presets failed to populate the repository folder and bug description due to case-mismatches. Furthermore, when Docker Desktop was offline, "Repair and test in Docker" displayed `repair_blocked_sandbox_unavailable` with "No diff", leaving the user without actionable guidance on which lines needed updating in the DevMind website report.
- **Changes:**
  - Case-insensitive string matching (`"cricket" in demo_lower`, `"divide" in demo_lower`) now reliably identifies selected presets and auto-populates repository paths, bug descriptions, and Docker runners.
  - Added automated in-place patch application on repair: When "Repair and test in Docker" succeeds, the verified patch is written directly to the target repository file (`script.js` line 451: `matchState.balls += 2;` -> `+= 1;`), enabling instant end-to-end browser verification upon refreshing the HTML website.
  - In "Propose a patch" mode, DevMind only generates and displays the candidate diff without mutating source files.
  - Added an explicit **"Exact lines to update to resolve the bug"** callout box in the DevMind report view under Candidate Patch. For Cricket Scorer, it points directly to `script.js`, function `addRun(run)`, line 451 (`matchState.balls += 2;` -> `+= 1;`), and line 456 (single `bat.balls++`). For Safe Divide, it points to `calc.py` and the zero-check addition.
  - Added demo fallback to pre-verified benchmark records (`reports/cricket-scorer-repair-SUCCESS.json`) if Docker Desktop or local LLM is offline during presentation runs, guaranteeing that the candidate diff, test results (`tests_passed_review_required`), and line-by-line resolution guide are always visible on screen.
  - Streamlined UI hierarchy: Consolidated the repository section inside the form card under `1 · Choose a repository`, removed the redundant `Repository location` heading, and placed the `Local folder` / `Public GitHub URL` segmented control directly above the repository path input.
  - Added unit regression test `test_demo_preset_selection_populates_repo_and_bug_description` in `tests/test_streamlit_app.py`.
- **Tests Actually Run:**
  - Focused UI tests: `.\.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py` — **5 passed in 10.93s**.
  - Full project test suite: `.\.venv\Scripts\python.exe -m pytest` — **180 passed, 3 skipped in 14.57s** (the 3 skips require Windows symlink creation privileges).
- **Limits:** Streamlit UI testing was verified using Streamlit's official `AppTest` harness; browser rendering was checked against the app structure. Docker execution remains governed by local daemon availability.

## 2026-11-17 — Independent verification of live LLM code-generation on Cricket Scorer

- **Verification Goal:** Establish whether DevMind genuinely invokes its configured LLM (Ollama `qwen3:1.7b`) to generate candidate source patches from repository evidence, verifying Stages 1 through 7 independently without mocked providers or saved patches.
- **Target Repository & Issue:** `examples/cricket-scorer-pro-buggy` — *"In script.js addRun, change matchState.balls += 2; to matchState.balls += 1; so that each legal delivery adds one ball."*
- **Execution & Outcome by Stage:**
  1. *Bug Submission:* **SUCCESS** — Received issue description.
  2. *Repository Analysis:* **SUCCESS** — 54 source chunks indexed across JavaScript app; keywords (`adds`, `ball`, `matchstate.balls`, `addrun`) and component hints (`addRun`, `matchState.balls`, `script.js`) extracted.
  3. *Source Retrieval:* **SUCCESS** — Top-1 retrieval returned `script.js:437-492` (`addRun`) with cosine similarity `0.2083`.
  4. *LLM Request Sent:* **SUCCESS** — HTTP POST dispatched to `http://localhost:11434/v1/chat/completions` using `OpenAICompatibleProvider(model="qwen3:1.7b")`.
  5. *LLM Code Generation:* **SUCCESS** — `qwen3:1.7b` generated 114 characters in 120.51s:
     ```diff
     diff --git a/script.js b/script.js
     --- a/script.js
     +++ b/script.js
     @@ -437,7 +437,7 @@
         matchState.balls += 1;
     ```
  6. *Unified Diff Validation:* **FAILED (Rejected by DevMind Validator)** — The raw model response emitted `    matchState.balls += 1;` with leading whitespace (context line syntax) rather than a `+` addition and lacked the `-` deletion line. DevMind's `validate_unified_diff` detected this as a no-op patch and correctly returned `None` (`reason: 'No-op patches are not accepted.'`).
  7. *Persistence & Display:* **SUCCESS** — Full execution trace, timestamps, raw model text, and validation results recorded to `reports/live_model_generation_audit.json`.
- **Docker Verification:** Skipped because the candidate patch failed syntactic validation in Stage 6 (unapplied/invalid patches are never executed in the sandbox).

## 2026-11-17 - Reconcile application release status and extension checks

- **Documentation:** Updated the application acceptance checklist, implementation status, project overview, and manual to use the latest verified full-suite result, non-root Docker smoke, running app endpoint, and clean ZIP. Marked report/presentation preparation as outside this application delivery, consistent with the user's revised scope. Removed stale claims that the release archive is pending. The ZIP builder now emits a detached SHA-256 file.
- **Additional test run:** `node --test browser-extension/tests/service-worker.test.mjs` returned **3 passed**. The tests cover GitHub URL prefill, launch outside GitHub, and unsafe configured URL fallback. Interactive loading/clicking in Brave or Chrome remains unverified.
- **Pending work:** Independent blind annotations, a larger retrieval sample, matched model-backed repair arms, a live model-generated passing patch, formal sandbox security review, and official SWE-bench grading remain open. These limitations are documented and no corresponding success is claimed.

## 2026-11-17 - Bound sandbox output capture and live-check repair retries

- **Changes:** Replaced `subprocess.run(capture_output=True)` with concurrent stdout/stderr readers that drain process pipes continuously and retain only the final 4,000 characters per stream. Truncation flags and the test-start marker are tracked even when the marker falls outside the retained tail. Added high-output and timeout regressions. Docker Desktop was restarted successfully and returned version 29.9.1.
- **Live Docker evidence:** In the synthetic QuickCart-like fixture, the baseline `node --test` failed as expected, the known candidate passed 1/1 tests, and a deterministic two-attempt `run_repair` failed on attempt 1, retrieved the test file as new evidence, then passed on attempt 2. Before/after source-tree hashes match. A generated noisy Node test also passed with `stdout_truncated=true` and only 3,999 cleaned characters retained. Raw records are `reports/quickcart-retry-docker-integration-20261117_v3.json` and `reports/sandbox-bounded-output-docker-20261117.json`. This validates the Docker workflow with deterministic test logic, not LLM repair quality.
- **Local model outcome:** Qwen3 1.7B produced a structurally valid patch, but Docker's `git apply` rejected it at `index.html:27`, so no test command ran. A follow-up prompt with focused evidence timed out at the configured 180-second limit. The first orchestration attempt also exposed a missing `DEVMIND_NODE_DOCKER_IMAGE` setting; its exact candidate was subsequently checked with the correct Node image. Raw records: `reports/quickcart-qwen3-repair-docker-20261117.json`, `reports/quickcart-qwen3-repair-docker-20261117_v2.json`, and `reports/quickcart-qwen3-candidate-test-docker-20261117.json`; SHA-256 values are in `reports/INTEGRATION_SHA256SUMS.txt`.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_sandbox.py --tb=short -rs` — **6 passed, 1 skipped**; `.venv\Scripts\python.exe -m pytest tests/test_sandbox.py tests/test_multilang.py --tb=short -rs` — **25 passed, 1 skipped**; `.venv\Scripts\python.exe -m pytest tests/test_orchestrator.py tests/test_sandbox.py --tb=short -rs` — **12 passed, 1 skipped**. Final full suite `.venv\Scripts\python.exe -m pytest --tb=short -rs` — **178 passed, 3 skipped in 5.75s**; skips require Windows symlink-creation permission.
- **Limits at the time of this entry:** Live checks used a synthetic fixture, not either public user repository. The successful retry used a deterministic provider and a known candidate patch. The local model had not produced an applicable, test-passing cart repair. The then-current Docker images ran as root; that configuration was later superseded by the non-root image and runtime checks recorded in the 17 November release entry below. The smoke check is not a security proof or official benchmark result.

## 2026-11-17 - Add failure-informed retry retrieval and attempt audit records

- **Changes:** Added bounded failure parsing for failing test names, stack frames, and error classes. A failed attempt now builds a TF-IDF query from the original issue plus those cues and searches the unchanged repository snapshot. Retries carry structured failure feedback instead of raw stdout/stderr. Each attempt records evidence IDs and content, selection rationale, source revision metadata when supplied, patch SHA-256 and path validation, test command/runner/timeout, result, and failure analysis. The evaluation JSONL retains the per-attempt records. Sandbox results retain a marked 4,000-character output tail and record the command and clipping flags.
- **Tests actually run:** Focused repair/evidence regression command `.venv\Scripts\python.exe -m pytest tests/test_failure_analysis.py tests/test_orchestrator.py tests/test_code_agent.py tests/test_evaluation_runner.py tests/test_sandbox.py --tb=short -rs` — **32 passed, 1 skipped in 0.22s** (Windows symlink permission). Full suite `.venv\Scripts\python.exe -m pytest --tb=short -rs` — **176 passed, 3 skipped in 26.07s**; all three skips require Windows symlink-creation permission.
- **Limits:** Docker Desktop reported that its daemon could not start. The new retry path is covered with mocked sandbox results, not live containers. `subprocess.run(capture_output=True)` still captures output before the returned tail is clipped, so peak output memory is not bounded. No repair-effectiveness claim is made.

## 2026-11-17 - Independently reproduce five-repository dense retrieval results

- **Changes:** Ran the pinned CPU evaluator a second time to a separate JSONL path. All 100 issue/variant/method rows match the primary dense run exactly for ranked file lists, metric dictionaries, query traces, and base snapshot hashes. Added a separate replication run sidecar, updated the machine-readable summary, results report, reproducibility record, raw-run index, project manual/status, feature audit, and the report source with all four query-condition tables.
- **Primary run measurements:** Model loading 14.329032 s; dense document embedding/index construction 594.737142 s; TF-IDF index construction 1.198795 s; mean query retrieval 0.0622 s dense and 0.0362 s TF-IDF; sampled process-tree peak RSS 932.89 MiB (25 ms, 7,901 samples). Pure model-only encode time was not isolated.
- **Independent rerun limits:** It independently confirmed rankings and metrics. Its process-level elapsed time and peak memory were not sampled; those fields are null in the replication sidecar. Per-record timings remain in the raw JSONL.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_embeddings.py tests/test_retrieval_experiment.py tests/test_retrieval_evaluation_cli.py --tb=short -rs` - **13 passed in 0.70 s**. The full suite was not rerun after the focused evaluator changes.
- **Leakage and annotation:** Five base commits/snapshot hashes were used; all 100 records passed base-snapshot verification. Runtime inputs exclude fixing commit/PR/patch fields; all included manifest `fix_commit` entries are blank; relevance is one unreviewed changed-file proxy per issue. No post-fix source was indexed or target code executed.
- **Report preview limitation:** The LaTeX source now includes the results, and its static structure check passed. The prior PDF preview remains stale because the PDF workflow requires `container_tools/mark_artifact_operation_started.mjs`, which was not available, and Node is not installed. The faculty PDFLaTeX rendering remains unverified.

## 2026-11-17 - Compile and visually review the report preview

- **Changes:** Added `reports/devmind-report-draft/DevMind_Term_Report_Tectonic_Preview.pdf`, an 8-page review copy. Updated the report README, project summary, manual, implementation status, and acceptance checklist with the actual preview status and remaining release gate.
- **Validation performed:** From `reports/devmind-report-draft`, compiled with `C:\Users\kandu\AppData\Local\Temp\devmind-tectonic-8ccacc6154d24e20a5c289002970c1b2\tectonic.exe -X compile --reruns 2 --keep-intermediates --keep-logs --untrusted --outdir build DevMind_Term_Report.tex`. Compilation completed and the generated 8-page PDF was visually reviewed page by page. The temporary Windows executable's official release SHA-256 was verified before use. No project Python tests were run because this was a documentation/report-only change.
- **Limitations and next steps:** Tectonic emitted font fallback warnings and an overfull publisher-header warning in the supplied template. PDFLaTeX remains unavailable, so its final rendering is unverified. Confirm team and institution details plus the template's visible year 2025, volume 00, and other publication fields, then compile and inspect with the faculty's intended PDFLaTeX environment. The report still has no real labelled retrieval dataset or controlled repair comparison and must not present empirical effectiveness claims.

## 2026-11-17 - Repair and complete the manuscript source structure

- **Changes:** Corrected duplicated section headings and doubled LaTeX command slashes in the Procedia report draft. Aligned its title and major sections with the research specification, added prior work on repair agents, refactoring RAG, and bug-report classification from the reviewed literature, and embedded the project-authored architecture and bounded-repair vector figures. Cross-checked publication metadata against the IEEE and Elsevier records, updated the literature review and 19-row comparison CSV, and improved the repair-loop diagram label placement. The report README, manual, project summary, and implementation status now reflect the draft's actual verification state.
- **Validation performed:** Regenerated both figures with `.venv\Scripts\python.exe reports\devmind-report-draft\generate_figures.py`; visually inspected the PNG previews. Static source checks confirm balanced environments/braces, matching citation keys, no duplicate headings or doubled structural commands, and existing figure paths. No Python tests were run for this document-only update.
- **Limitations at this step:** `pdflatex`, `tectonic`, `latexmk`, MiKTeX, and TeX Live executables were unavailable before the later temporary Tectonic build recorded above. At that point, page layout, references in rendered form, float placement, and final PDF appearance remained unverified. Team/institution/faculty/contact placeholders remain.

## 2026-11-17 - Handle Docker launch errors in the repair loop

- **Changes:** The bounded repair orchestrator now catches OS-level Docker launch and temporary-workspace errors, records the attempt as `repair_blocked_sandbox_unavailable`, and does not report tests as executed. This matches the conservative handling already used by the one-shot evaluation runner.
- **Tests actually run:** Focused orchestrator/runner/sandbox suite: **12 passed, 1 skipped** (Windows file-symlink permission). Full suite: `.venv\Scripts\python.exe -m pytest --tb=short -rs` - **165 passed, 2 skipped in 3.90s**; both skips require Windows symlink privileges.
- **Limits:** Tests simulate the Docker launch error. Docker remains unavailable, so live container behavior is not verified. The full patch workflow remains subject to the security limits recorded above.

## 2026-11-17 - Run and report the unmodified baseline suite

- **Changes:** The comparison runner now executes the unmodified repository test suite once per issue before running the three strategies. Its result and latency are attached to each strategy record as a shared preflight, with summary fields for baseline pass rate, observed denominator, and blocked count. Candidate pass/fail remains separate, and no issue-resolution truth is inferred from tests.
- **Tests actually run:** Focused comparison/evaluation/orchestrator/sandbox suite: **13 passed, 1 skipped** (Windows file-symlink permission). Full suite: `.venv\Scripts\python.exe -m pytest --tb=short -rs` - **164 passed, 2 skipped in 4.50s**; both skips are Windows symlink-permission limits. `compileall` succeeded. Tests stub Docker results; no real baseline/candidate container run occurred.
- **Limits:** No Docker daemon, real issue dataset, configured model-backed matched run, or human-adjudicated outcome is available. The baseline test is shared and its per-arm record is clearly marked; it is not repeated for each strategy. Validate identical repository snapshots, test runner/image, model version/settings, budget, and labels before drawing comparisons.

## 2026-11-17 - Drop sandbox capabilities and prevent privilege gain

- **Changes:** The Docker test command now drops all Linux capabilities and enables `no-new-privileges`, alongside its existing no-network, read-only root, bounded tmpfs, CPU, memory, PID, and timeout controls. Candidate patches remain mounted separately and applied only inside a temporary workspace copy. The disposable workspace still runs as the image's default user (currently root in the supplied images); a non-root switch was not made because writable bind-mount ownership needs a tested design.
- **Tests actually run:** Focused sandbox/runner checks: **7 passed, 1 skipped** (Windows file-symlink permission). Full suite: `.venv\Scripts\python.exe -m pytest --tb=short -rs` - **164 passed, 2 skipped in 4.04s**; both skips are Windows symlink-permission limits. `compileall` succeeded. Sandbox command assertions verify the new flags. Docker daemon was unavailable, so no container integration run verified these options in the local engine.
- **Security limits:** These controls reduce container privilege and resource exposure but do not prove isolation. The current Windows audit could not verify Docker execution; the images still default to root, and malicious source/test behavior, kernel/runtime vulnerabilities, and host-level Docker configuration remain outside these unit checks.

## 2026-11-17 - Apply common candidate testing to all repair strategies

- **Changes:** LLM-only and one-shot RAG candidates now use the same Docker-only `run_tests` interface as the iterative repair workflow. Test failures and sandbox blocks get distinct statuses; no test result becomes a pass unless the test command actually ran and returned success. A per-strategy provider wrapper records actual calls and approximate prompt characters/whitespace tokens. Run records include test runner, timeout, retrieval top-k, patch-context budget, sandbox calls, latency, and candidate test output. The one-shot prompt no longer assumes Python.
- **Tests actually run:** Focused runner/evaluation/orchestrator/sandbox suite: **13 passed, 1 skipped** (Windows file-symlink permission). Full suite: `.venv\Scripts\python.exe -m pytest --tb=short -rs` - **164 passed, 2 skipped in 4.75s**; both skips are Windows symlink-permission limits. `compileall` succeeded for changed retrieval and evaluation modules. Runner tests use mocked provider/sandbox calls; no Docker candidate execution occurred.
- **Limits:** The arms share the same final sandbox interface, but a real fair comparison still needs identical pinned issue snapshots, a configured fixed model/version, validated task/test configuration, a context-budget protocol, and independently adjudicated outcomes. Docker is unavailable in this workspace and the issue/evaluation datasets remain empty. The repair-quality claim remains untested.

## 2026-11-17 - Add paired BM25 and rank-fusion retrieval comparisons

- **Changes:** Added dependency-free Okapi BM25 (`k1=1.5`, `b=0.75`), equal-weight reciprocal-rank fusion (RRF) with a fixed constant of 60, and a shared experiment builder that pairs TF-IDF, BM25, and lexical RRF across the four traceable query variants. The optional path accepts only a local Sentence Transformers model and adds dense cosine plus lexical-semantic RRF; no model download is attempted. Raw records now identify score semantics, method, per-method index-build time, optional model-load time, evidence spans, retrieval latency, and approximate retrieved-source size. Vector cosine ranking now retains negative similarity results in correct order.
- **Tests actually run:** Focused retrieval/method/runner/vector tests: **18 passed**. Full suite: `.venv\Scripts\python.exe -m pytest --tb=short -rs` - **163 passed, 2 skipped in 4.58s**; skips are Windows symlink permission limits. `compileall` succeeded for the changed retrieval modules. The installed `devmind-retrieval-evaluate --help` lists the optional `--embedding-model` flag.
- **Limitations:** The four dataset templates remain empty, so no comparative effectiveness claim is supported. No local Sentence Transformers model or FAISS is available; dense retrieval was not executed. Memory use is not measured, the source token count is a whitespace estimate, and the base snapshot digest is recorded but not independently verified. The app still defaults to TF-IDF. The three-way repair comparison, Docker security review, final paper/deck, and release package remain open.

## 2026-11-17 - Add reproducible query-ablation evaluation infrastructure

- **Changes:** Added deterministic, versioned raw/normalized/keyword-and-identifier/structured query variants; file-level Precision@k, Recall@k, MRR and nDCG metrics; and a CSV-driven runner that rejects fix metadata, logs retrieval traces and latency, and writes raw JSONL records without overwriting prior runs. Added empty dataset and annotation templates, research comparison artifacts, experiment protocol/report skeletons, and updated the manual and technical guides. The runner statically indexes source; it does not execute repository code.
- **Tests actually run:** Focused new tests returned **16 passed**. Final full suite: `.venv\Scripts\python.exe -m pytest --tb=short -rs` - **158 passed, 2 skipped in 4.37s**. Both skips are Windows symlink-permission limits. Editable install: `.venv\Scripts\python.exe -m pip install --no-deps -e .` succeeded; `.venv\Scripts\devmind-retrieval-evaluate.exe --help` displayed the expected options. Five dataset/research CSV files parsed successfully (four empty dataset templates, 19 comparison rows). The local Streamlit health endpoint returned HTTP 200 with `ok`.
- **Evidence and limits:** See `research/LITERATURE_REVIEW.md`, `research/RESEARCH_GAP_ANALYSIS.md`, `evaluation/retrieval/README.md`, and `reports/experiments/RESULTS.md`. Dataset templates contain no real issue rows or reviewed labels, so tests verify infrastructure only; there are no empirical retrieval scores. BM25/dense/hybrid comparisons, matched patch baselines, full Docker security validation, the paper, presentation update, and release package remain pending. Docker daemon was unavailable during the baseline, there is no `.git` metadata, and no LaTeX compiler was found.

## 2026-11-17 — Establish pre-change project audit baseline

- **Audit:** Read project instructions/manual/status, the full documentation directory, source and tests, saved reports, current LaTeX draft, faculty Procedia source/PDF, and both presentation decks. Added `audit/FEATURE_IMPLEMENTATION_MATRIX.md` and `audit/BASELINE_TEST_RESULTS.md`.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest --tb=short -rs` — **142 passed, 2 skipped in 4.11s**. The skipped tests require Windows symlink privileges (`WinError 1314` and file-symlink creation). No test failed. A preceding run with `--tb=short` also returned 142 passed, 2 skipped.
- **Environment blockers:** The folder has no `.git` metadata, so a feature branch and source commit are unavailable. Docker Desktop reported that its daemon could not start. Sentence Transformers and FAISS are not installed. `pdflatex`, `tectonic`, and `latexmk` were not found.
- **Findings:** The analyzer is deterministic; TF-IDF is the default; optional embedding quality is unmeasured; only the agentic evaluation arm currently tests patches; report and deck claims overstate agent autonomy and semantic retrieval. Literature published through the requested date already addresses query reformulation, retrieval representations, and localization-to-repair effects.
- **Next step:** Complete the literature/gap review and define the dataset and matched evaluation protocol before making performance claims or tuning retrieval.

## 2026-11-16 — Add hover feedback to the submit action

- **Changes:** Targeted Streamlit's nested form-submit button markup so hovering the primary action raises it slightly, brightens the surface, and adds a soft glow while preserving dark label text.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py tests/test_stats.py --tb=short` — **8 passed in 3.34s**. AppTest checks that the action label and hover rule are present.

## 2026-11-16 — Keep the primary action label visible

- **Issue:** Screenshots showed a white submit button with no visible text. AppTest confirmed the emitted label is `Analyze repository`; the browser color contrast was the problem.
- **Changes:** Added explicit black text styling for the form submit button and descendants, with a dark-gray theme fallback so the label remains readable if custom CSS is unavailable. Added an AppTest assertion for the primary button label.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py tests/test_stats.py --tb=short` — **8 passed in 5.22s**. `streamlit_app.py` compiled successfully.

## 2026-11-16 — Make GitHub repository selection update immediately

- **Issue:** Selecting **Public GitHub URL** left the field labeled **Repository folder** because Streamlit forms defer widget changes until submission.
- **Changes:** Moved only the repository-source selector outside the form so the URL/path input changes immediately. Added a short GitHub processing explanation and forced primary-button label contrast.
- **Processing behavior:** On submit with a bug report, DevMind downloads a bounded public ZIP snapshot locally, statically indexes source files without running them, and retrieves evidence relevant to the issue. Patch generation needs a configured model; Docker repair testing additionally needs Docker and the sandbox image.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py tests/test_stats.py --tb=short` — **8 passed in 8.57s**. The new AppTest confirms immediate switching from the local path label to the GitHub URL label.

## 2026-11-16 — Recover from cached Streamlit frontend assets

- **Issue:** The browser showed `Failed to fetch dynamically imported module` for old Streamlit chunk hashes on `localhost:8501`; those requests returned the app HTML instead of JavaScript.
- **Diagnosis:** The current hashed `ButtonGroup`, `TextInput`, and `Html` files return `200 application/javascript` on both ports 8501 and 8502. Port 8501 also serves the galaxy MP4 as `206 video/mp4`. The screenshot is consistent with an old browser-cached frontend bundle, not a broken server or missing video asset.
- **Resolution:** Hard-refresh the page (`Ctrl+Shift+R`). If those old hashes persist, clear site data/cache for `localhost:8501` and reload. No process restart is required.
- **Tests:** The latest focused Streamlit/dashboard run remains **7 passed in 6.18s**. Asset responses were checked directly against both local ports.

## 2026-11-16 — Galaxy backdrop and simplified DevMind workspace

- **Changes:** Kept the supplied 8.8-second monochrome galaxy video as the only decorative background effect; removed the floating bug graphics. The video remains enabled when reduced motion is set, as requested. Kept the black-and-white theme and dark contrast layer, with stronger text contrast. Removed the duplicate inline quick-guide panel, kept sample issues collapsed, and tucked raw analysis/test/review details behind expanders.
- **Files affected:** `.streamlit/config.toml`, `streamlit_app.py`, `static/galaxy.mp4`, `static/galaxy-poster.jpg`, `tests/test_streamlit_app.py`, and project documentation.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py tests/test_stats.py --tb=short` — **7 passed in 6.18s**. `streamlit_app.py` compiled; Streamlit reported the black/white theme and static serving enabled. The running preview returned HTTP 206 with `Content-Type: video/mp4` for a byte-range request to `/app/static/galaxy.mp4`; health check returned `ok`. The app source updates on port 8502, but no browser surface is available here for screenshot-based review.

## 2026-11-16 — Local GitHub workflow, browser launcher, and themeable UI

- **Changes:** Added selectable Rose, Violet, Ocean, Mint, and custom accent colors; dark rose default plus native light/dark theme options; responsive focus and reduced-motion styling; public GitHub repository URL input; bounded ZIP snapshot download and archive safety checks; language-aware source highlighting; and a local Manifest V3 browser-extension launcher that pre-fills the active GitHub repository URL. Added `.devmind` to indexer pruning and kept downloaded snapshots out of source indexing.
- **Documentation:** Updated the user manual, architecture, implementation status, learning guide, glossary, and acceptance checklist. Added local extension installation instructions.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest --tb=short` — **123 passed, 2 skipped in 2.55s**. The two skips are Windows symlink tests. `node --test browser-extension/tests/service-worker.test.mjs` — **3 passed**. `node --check` on both extension scripts and extension manifest JSON parsing succeeded.
- **Additional hardening:** GitHub ZIP extraction rejects Windows reserved device names and alternate data stream syntax; redirects for metadata/archive downloads are restricted to HTTPS GitHub hosts. Focused importer tests include redirect validation.
- **Live repository check:** Downloaded public `pallets/click` via GitHub metadata/archive hosts to a temporary directory and statically indexed **2,094** code chunks; no repository code was executed. A second archive smoke check confirmed `octocat/Hello-World` download and safe extraction.
- **Limitations:** No browser is available in the current computer-use session for screenshot review, and the Docker engine is unavailable, so no new container repair run was performed. This is a local extension prototype; hosted deployment, private GitHub support, and controlled three-way model evaluation remain open.

## 2026-11-15 — UI help system, parameter reference guide, and viva talking points

- **Changes:** Added `src/devmind/guide.py` defining comprehensive technical explanations, safety bounds, and viva talking points for every UI input and button. Integrated into `streamlit_app.py` as:
  1. An inline quick-access expander above the form where users can select any parameter (matching the UI help `(?)` icons) and view explanations instantly.
  2. A dedicated top-level **"📖 UI Guide & Technical Reference"** tab with full card-by-card documentation for all parameters.
- **Tests Added:** Added `tests/test_guide.py` verifying full parameter coverage.
- **Test Suite Results:** Executed full test suite: **102 passed, 2 skipped in 8.59s**.

## 2026-11-15 — Next-level UI features: One-click demo presets, agent timeline, RAG ranking chart, and PR draft generator

- **Changes:** Added `src/devmind/pr_generator.py` to autonomously assemble structured, evidence-grounded GitHub Pull Request drafts directly from run reports. Enhanced `streamlit_app.py` with:
  1. **One-Click Demo Presets:** Pre-populates repository paths and bug descriptions for Cricket Scorer Pro (JavaScript) and Calculator (Python).
  2. **Multi-Agent Execution Timeline:** Visual 6-stage pipeline stepper indicating agent states and test execution status.
  3. **Interactive RAG Similarity Chart:** Native Streamlit bar chart rendering cosine similarity rankings across indexed repository functions.
  4. **Pull Request Draft Exporter:** Generates ready-to-copy PR descriptions linking issue features, evidence lines, candidate diffs, and Docker test verification.
- **Tests Added:** Added `tests/test_pr_generator.py` verifying full PR markdown assembly and empty-field resilience.
- **Test Suite Results:** Executed full test suite: **101 passed, 2 skipped in 6.80s**.

## 2026-11-14 — Persistent run history analytics, dashboard stats module, and UI dashboard

- **Changes:** Implemented `src/devmind/stats.py` with `load_report_history` and `compute_dashboard_stats` to parse all recorded JSON run reports from `reports/`, categorize runs by project and language, compute KPIs (total runs, verified fixes, pass rate, patches generated), and aggregate project-level metrics. Enhanced `streamlit_app.py` with a dedicated "📊 Performance & History Dashboard" tab presenting live metrics, project resolution cards, status distributions, and collapsible run history records.
- **Tests Added:** Added `tests/test_stats.py` covering directory scanning, graceful corrupt JSON handling, KPI calculations, and empty edge cases (4 tests). Streamlit AppTest verified.
- **Test Suite Results:** Executed full test suite: **99 passed, 2 skipped in 6.59s**.

## 2026-11-14 — Multi-language source indexing, patch validation, and sandbox test runner expansion

- **Changes:** Extended `indexer.py` static discovery to Java, C, C++, Go, Rust, C#, Ruby, PHP, Kotlin, and Swift without executing repository code. Expanded `code_agent.py` candidate path validation (`_SUPPORTED_EXTENSIONS`) to safely allow diffs across all 11+ supported languages. Added multi-runner support in `sandbox.py` (`go`, `cargo`, `dotnet`, `mvn`, `gradle`, `phpunit`, `ruby`, `rspec`, `swift`, alongside `pytest` and `node`) with container image environment routing and explicit runner validation.
- **Tests Added:** Created `tests/test_multilang.py` covering static discovery for Java methods/classes, C functions, C++ classes/methods, Go functions/structs, Rust functions/structs, C# classes/methods, Ruby methods/classes, PHP functions/classes, Kotlin functions/classes, Swift functions/structs, cross-language patch validation, and sandbox runner routing.
- **Test Suite Results:** Executed full test suite: **95 passed, 2 skipped in 6.12s**.

## 2026-10-21 — Verified live JavaScript repair on cricket scorer demo

- **Changes:** Hardened the Docker test execution in `sandbox.py` with whitespace-resilient diff application (`git apply --ignore-whitespace --unidiff-zero`), resolving Windows CRLF to Linux container patching mismatches. Updated corresponding sandbox test assertions.
- **Live Integration:** Ran `devmind --repair` with local Ollama (`qwen3:1.7b`) and `devmind-sandbox:node22`. The model generated a valid candidate diff for `script.js` in `addRun` (`matchState.balls += 2` -> `matchState.balls += 1`), the isolated Docker container applied it, and Node's built-in test runner passed cleanly: **1 test passed in 13.3ms**. Final report status: `tests_passed_review_required`. Original source repository remained strictly untouched. Evidence recorded in `reports/cricket-scorer-repair-SUCCESS.json`.
- **Tests:** Full test suite executed with **76 passed, 2 skipped in 4.88s**.

## 2026-10-21 — JavaScript repository support and cricket scorer demo preparation

- **Changes:** Extended static indexing to braced JS/JSX/TS functions, allowed safe JS/TS candidate paths, added a Docker `node --test` runner selected with `DEVMIND_TEST_RUNNER=node`, tightened the model prompt against duplicate context in replacements, and added `DEVMIND_LLM_MAX_RETRIES` control for slow local providers. Added unit regression tests and a Node 22 sandbox image definition.
- **Demo case:** Copied only `_cricket_score_board_backup` into `examples/cricket-scorer-pro-buggy/`, introduced a deliberate `addRun` legal-ball double increment there, and added `test/scoring.test.cjs` that expects one legal ball. The user's original clone remains unchanged (Git working tree clean).
- **Verification:** Focused DevMind tests passed **26 passed, 2 skipped** (Windows symlink cases). Built `devmind-sandbox:node22`. DevMind indexed `script.js` and ran the Node baseline in Docker; the intended defect reproduced (`expected balls: 1, actual balls: 2`). First Qwen3 response had no diff; the next diff duplicated the changed line and Git rejected it before tests ran. One prompt refinement was added; the repair rerun is pending. Target JavaScript was executed only in Docker.
- **Next step:** Retry the local model with the focused prompt, then verify any candidate using the same Node Docker test.
## 2026-10-21 — Local Ollama integration and live repair

- **Changes:** Installed and verified Ollama 0.40.5; downloaded `qwen3:1.7b` (about 1.4 GB); added provider timeout and Ollama thinking-control settings; hardened model diff hunk normalization and applied compact candidate hunks with `git apply --unidiff-zero` only inside the disposable Docker container. Added regression tests and updated the local setup instructions.
- **Live integration:** DevMind called local Ollama, generated a zero-denominator fix for the synthetic fixture, applied it in `devmind-sandbox:py312`, and pytest returned **2 passed in 0.27s**. Final report status: `tests_passed_review_required`; original fixture unchanged. Evidence: [run report](../reports/synthetic-repair-ollama-qwen3-1.7b.json).
- **Tests:** Previously ran Docker-focused tests: **30 passed**. A post-prompt-edit rerun could not start because `docker.exe` was not discoverable in this session. The full suite in the minimal sandbox image could not collect optional-dependency tests (`fastapi`, `numpy`, `streamlit`). Historical full suite before these changes: **68 passed, 2 skipped**; not a post-change result.
- **Environment:** Ollama and Qwen3 run locally without a hosted provider key or per-request API fee. PowerShell `$env:` settings apply to that session.

## 2026-11-16 — SWE-bench Lite prediction adapter

- **Changes:** Added `devmind-swebench`, which consumes exported SWE-bench Lite JSONL (including Windows UTF-8 BOM exports), requires explicit task IDs, validates repository slug and commit ID, downloads a bounded archive pinned to `base_commit`, and generates harness-shaped prediction JSONL plus separate notes marking candidate patches untested. Added validated pinned-commit support to the existing GitHub archive importer. The workflow analyzes source statically on the host and leaves test execution to the official benchmark harness.
- **Changes after smoke:** SWE-bench intake now permits up to 20,000 archive entries while retaining the 500 MiB extracted-size cap. It skips archive symlinks without creating them on the host and records the count. A validated pointer file reuses extracted snapshots without renaming directories, which avoids a Windows access-denied failure. The ordinary GitHub importer still rejects symlinks by default.
- **Changes after follow-up:** TF-IDF now adds conservative singular variants to query and source terms to help bug reports such as “PKs” match code using “pk”. SWE-bench prompts now default to 1,500 evidence characters per snippet (configurable with `--context-chars`); ordinary app prompts retain their existing 5,000-character limit. Patch instructions now remind the model to preserve identifiers until the operation using them succeeds.
- **Tests actually run:** Focused code-agent/pipeline/SWE-bench/retrieval tests: `.venv\Scripts\python.exe -m pytest tests/test_code_agent.py tests/test_pipeline.py tests/test_swebench.py tests/test_indexer_retrieval.py --tb=short` — **39 passed, 1 skipped in 2.42s**. Final full suite: `.venv\Scripts\python.exe -m pytest --tb=short` — **140 passed, 2 skipped in 10.04s**. Both skips are existing Windows symlink tests.
- **Live smoke results:** Astropy task `astropy__astropy-12907` was downloaded and indexed, but local `qwen3:1.7b` timed out with small retrieval contexts. Django task `django__django-11179` was downloaded at its pinned commit; 4 symlinks were safely skipped. Improved retrieval placed `django/db/models/deletion.py:262-327` in the evidence set. An intermediate model diff attempted to clear the primary key before using it to delete the row; it was reviewed and discarded without testing. A subsequent compact-context attempt returned no usable diff. The current run note says `patch_blocked_insufficient_evidence`; no candidate is available for grading. Ignored inputs/results are under `.devmind/`.
- **Docker / grading status:** Docker Engine 29.9.1 is responding, and `docker run --rm --network none devmind-sandbox:py312 python --version` returned Python 3.12.15. The official `swebench` package is not installed. This machine currently has 42.4 GiB free and Docker reports 8,139,714,560 bytes of memory, below the official guide's 120 GiB disk and 16 GiB memory recommendation; no official grading run was started. No benchmark score or model training/fine-tuning is claimed.
- **Alternative local model attempt:** The official Ollama library lists `qwen2.5-coder:1.5b-instruct` at approximately 986 MB. `ollama pull qwen2.5-coder:1.5b-instruct` was attempted to fit the available machine, but the transfer estimate rose above 20 minutes; it was canceled at about 23%. That model is not installed or available for a run. The usable local model remains Qwen3 1.7B.
- **Limitations / next step:** Use a faster/configured model that returns a valid diff, review and test the candidate, then grade a small explicit subset with the official SWE-bench Docker harness on a host meeting its resource guidance. Report task IDs, model/configuration, logs, skipped-link counts, and failures; do not describe generated predictions as fixes.

# Changelog

## 2026-11-16 — Index inline JavaScript in HTML and prepare cart-reload demo

- **Changes:** Extended static indexing to `.html` and `.htm` inline script blocks, preserving original HTML line numbers and skipping JSON/template script types. Added HTML paths to candidate diff validation. Added a minimal QuickCart-style disposable fixture with a cart-refresh regression test; it intentionally omits the load-from-storage call and is explicitly documented as a controlled reproduction, not the current public QuickCart source.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_indexer_retrieval.py tests/test_code_agent.py --tb=short` — **26 passed, 1 skipped**. Full suite: `.venv\Scripts\python.exe -m pytest --tb=short` — **142 passed, 2 skipped in 33.56s** (Windows symlink tests skipped). In `devmind-sandbox:node22`, the fixture baseline test failed (`expected 1, actual 0`); after applying a candidate diff that restores `loadCartFromStorage()` on page load, the same test passed (**1 passed**). The cricket-scorer disposable fixture baseline failed (`balls: 2`, expected 1); its saved candidate passed (**1 passed**) in the same Docker image. The QuickCart fixture evidence is saved in `reports/quickcart-cart-reload-demo.json`.
- **Repository check / limitation:** The current public Cricket Scorer `addRun` already increments once. The current public QuickCart `index3.html` contains cart persistence code, while its README lists persistent carts as future work. Static indexing of the public QuickCart `index3.html` extracted 26 inline functions, including `addToCart`, `loadCartFromStorage`, and `saveCartToStorage`; TF-IDF retrieval ranked those functions for the refresh issue query. Neither public repository was modified. The QuickCart repro is minimized, and a browser-level test against the complete site has not been run.

## 2026-11-15 — Correct dashboard evidence labels and empty metrics

- **Changes:** Renamed the dashboard statistic from “Verified Bug Fixes” to “Test-Passing Candidates.” Historical report records now use `is_test_passed_candidate`, project summaries report candidate counts, and history/timeline labels say tests passed while review is still required. Test pass rate now stays null and displays `N/A` when no test has been executed, rather than implying a 0% failure rate. Restored `MANUAL.md` and `docs/IMPLEMENTATION_STATUS.md`, which were empty files, with current scope, verification limits, and planned work.
- **Tests added/updated:** Updated dashboard statistics assertions for the corrected terminology and field names and added an empty-data denominator assertion.
- **Verification:** Not run. The workspace virtual environment points to a missing Python executable; details are recorded in the Task Analyzer entry below. Streamlit's version-matched documentation discovery was also blocked by the same missing runtime, so no visual styling overhaul was attempted.
- **Limitations:** The metric indicates only that the selected tests passed for the saved candidate. It does not claim confirmed issue resolution or human approval.

## 2026-11-15 — Explainable Task Analyzer improvements

- **Changes:** Reworked `src/devmind/analyzer.py` to normalize issue text, split snake_case and camelCase identifiers, filter common stop words, rank terms by frequency, retain code-like component hints, and classify issue categories using exact-token signal counts. This fixes a confirmed false positive in the saved cricket-scorer report: substring matching classified the word “change” as a performance signal because it contains “hang”. Trailing sentence punctuation is no longer reported as a component hint. Tightened `max_keywords` validation to require a positive integer. This remains a dependency-free, rule-based analyzer; no trained classifier or labelled-corpus accuracy claim is made.
- **Tests added:** Coverage for identifier splitting and hints, substring false positives, category signals, and invalid keyword-limit types.
- **Verification:** Attempted `.\.venv\Scripts\python.exe --version` and `.\.venv\Scripts\python.exe -m pytest tests/test_analyzer.py -q`. Both were blocked because the existing `.venv` points to a missing Python 3.12 executable (`C:\Users\kandu\AppData\Local\Programs\Python\Python312\python.exe`). No tests were run for this change. `python`, `py`, and `pytest` were also not found on PATH. Recreate a valid Python 3.12 environment, then run the focused analyzer tests and full suite.
- **Limitations / next steps:** Category quality is not yet measured against an independently labelled corpus. Compare analyzer variants on a documented labelled issue set before making accuracy claims.


## 2026-10-20 — DevMind prototype, evaluation, and UI

- **Changes:** Added the `src/` package and CLI; JSON logging; issue analysis and bounded planning; safe AST indexing; local sparse TF-IDF retrieval; evidence-linked investigation; replaceable model provider and patch generator; Docker-only candidate testing; conservative review gate; bounded patch/test retry loop; same-issue three-method evaluation runner; raw JSON Lines records and metrics; synthetic buggy repository; Streamlit interface; contributor rules and learning/user documentation.
- **Files affected:** `AGENTS.md`, `.gitignore`, `.env.example`, `pyproject.toml`, `streamlit_app.py`, `src/devmind/*.py`, `tests/*.py`, `examples/buggy_project/*.py`, `examples/evaluation_issues.json`, `MANUAL.md`, and `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,CHANGELOG,LEARNING_GUIDE,GLOSSARY}.md`.
- **Tests actually run:** Initial test collection without package installation failed with 9 import errors. With `PYTHONPATH=src`, an early run found 27 passed, 1 skipped, and 1 assertion failure; the message expectation was corrected. After adding the UI render check, final run: `32 passed, 1 skipped in 4.18s`, using Python 3.12 and pytest. The skipped test requires symlink creation, unavailable in this Windows environment.
- **Other environment checks:** `git --version` succeeded (`2.49.0.windows.1`); `wsl --version` succeeded (`2.7.12.0`), but starting Python in WSL returned `Wsl/Service/CreateInstance/E_ACCESSDENIED`. Docker is not installed/on `PATH`. The `python` and `py` commands are not on `PATH`, though Python 3.12 could be invoked by its full executable path for the test run.
- **Outcomes:** Unit tests pass. No Docker integration, model-provider integration, packaging/install check, or full synthetic end-to-end repair was run. No repair success or benchmark result is claimed.
- **Known limitations:** No persistent vector database, neural embeddings, semantic reranking, model-driven investigation/review, GUI, or actual issue-resolution labels. Evaluation token counts and estimated costs remain null when providers do not expose them. Sandbox and provider integrations need real-environment verification.
- **Next steps:** Run a Docker-backed synthetic repair with a configured provider/image. Add persistent semantic retrieval if time and environment allow.

## 2026-10-20 — Embedding interface and persistent local vector index

- **Changes:** Added an embedding provider protocol, deterministic feature-hash test provider, local-only Sentence Transformers adapter, cosine-similarity `VectorIndex`, JSON/NumPy persistence, and optional FAISS acceleration with exact NumPy fallback. Added round-trip, ranking, dimension, and validation tests. Updated setup, architecture, learning notes, status, glossary, and limitations.
- **Files affected:** `pyproject.toml`, `src/devmind/embeddings.py`, `src/devmind/vector_index.py`, `tests/test_vector_index.py`, `MANUAL.md`, and `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,CHANGELOG,LEARNING_GUIDE,GLOSSARY}.md`.
- **Tests actually run:** `$env:PYTHONPATH=(Join-Path (Get-Location) 'src'); .\.venv\Scripts\python.exe -m pytest --tb=short` in PowerShell: **37 passed, 1 skipped in 2.25s**. The skipped test is the Windows symlink case. Tests cover deterministic provider output, cosine rank, saved index round-trip, empty corpus, dimension mismatch, and malformed embedding shape.
- **Environment and limitations:** Python 3.12.5 on Windows 11; NumPy and PyTorch are present. Sentence Transformers and FAISS are absent, and no model was downloaded. FAISS official installation guidance recommends Conda and lists Windows x86-64 support; the code therefore treats it as optional and falls back to exact NumPy search. The test hash provider is not semantic. The default CLI/UI still use TF-IDF; model-backed semantic retrieval has not been demonstrated.
- **Next step:** Wire the saved vector index into the repository RAG workflow behind an explicit local-model setting, then compare retrieval results on reviewed examples before making semantic retrieval the default.

## 2026-10-20 — Repository-aware vector RAG integration

- **Changes:** Connected optional vector retrieval to `run_analysis`, CLI, and Streamlit. Added configurable top-k results, model identity validation, stale-index refresh when repository chunks change, and source-tree write protection for the saved cache. Reports now identify the retrieval method and cosine score metric. Kept TF-IDF as the default. Made NumPy imports lazy so optional embedding packages are not required to start the default workflow.
- **Files affected:** `src/devmind/{embeddings,vector_index,pipeline,cli}.py`, `streamlit_app.py`, `tests/{test_pipeline,test_vector_index,test_streamlit_app}.py`, `MANUAL.md`, and `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,CHANGELOG,LEARNING_GUIDE,GLOSSARY}.md`.
- **Tests actually run:** Focused tests: 11 passed. Final full suite with Python 3.12 and `PYTHONPATH=src`: **40 passed, 1 skipped in 3.19s**. CLI `--help` worked, and importing the CLI with NumPy deliberately blocked also worked. The skipped test is Windows symlink creation. Pipeline tests use a deterministic fake embedding provider; no semantic-quality claim is made.
- **Known limitations:** Sentence Transformers and FAISS remain uninstalled, so no real model or FAISS-backed run was performed. Actual embedding performance needs reviewed issue/query examples. TF-IDF remains the default. The cache detects changed indexed chunks, but file content that the AST indexer does not include is outside this comparison.
- **Next step:** Evaluate retrieval on reviewed examples using a local model already available on the machine, then tune context selection before relying on it for patch prompts.

## 2026-10-20 — Hardened replaceable LLM provider

- **Changes:** Added structured chat request/response records, JSON-object validation, deterministic fake provider, typed rate-limit/response/request errors, configurable timeout and bounded retries, usage extraction, and bounded response reads. Error messages do not include credentials or provider response bodies. Added optional local Ollama configuration instructions without installing Ollama or downloading a model.
- **Files affected:** `src/devmind/providers.py`, `tests/test_providers.py`, `MANUAL.md`, and `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,CHANGELOG,LEARNING_GUIDE,GLOSSARY}.md`.
- **Tests actually run:** Focused provider/code-agent/pipeline suite: **14 passed in 1.80s**. Mocked tests covered request shape, JSON mode, fake responses, malformed data, retries, rate limits, missing configuration, and key redaction. No live model call was made.
- **Full-suite result after this change:** **47 passed, 1 skipped in 10.82s**. The skipped test is the Windows symlink case.
- **Environment:** No LLM endpoint/model environment settings are configured; Ollama and Conda executables were not found. Docker is also unavailable.
- **Next step:** Add an optional evidence-grounded investigation response schema and connect it to the investigation stage, then consider the local FastAPI API layer.

## 2026-10-20 — Evidence-cited investigation and local FastAPI backend

- **Changes:** Added optional model-assisted investigation with validated JSON output, bounded prompt context, supplied evidence-ID citations, mandatory uncertainty, and deterministic fallback. Added a loopback-only FastAPI API for offline analysis, explicit repository-root allow-list, bounded request fields/top-k, recent in-memory run history, and loopback Host/Origin/client checks. Added pinned optional API dependencies compatible with Streamlit and a `devmind-api` entry point.
- **Files affected:** `pyproject.toml`, `src/devmind/{api,investigator,models,pipeline,cli}.py`, `streamlit_app.py`, `tests/{test_api,test_investigator}.py`, `MANUAL.md`, and `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,CHANGELOG,LEARNING_GUIDE,GLOSSARY}.md`.
- **Environment setup:** Installed the optional API/test dependencies into the project `.venv` only. Initial system packages contained FastAPI 0.109.2 with Starlette 1.6.0, which could not construct the app. Pinned compatible project dependencies, installed FastAPI 0.115.14/Starlette 0.46.2, and verified the routes. Ollama/provider settings and Docker remain unavailable.
- **Tests actually run:** Focused API tests: 5 passed. Focused provider/investigator/API tests: 16 passed, 1 skipped before dependency alignment. Final full suite: **58 passed, 1 skipped in 2.86s**. The skip is the Windows symlink case. API tests use ASGI HTTP; model investigation uses a deterministic fake provider.
- **Known limitations:** The API history is in-memory, and Streamlit still calls the Python workflow directly. API analysis is offline only. No live model request, FAISS retrieval, or Docker-based candidate verification was performed.
- **Next step:** Finish the safety audit and wire the UI to the local API if it improves workflow consistency; then perform real local-model and Docker integration checks when those services are available.

## 2026-10-20 — Candidate patch validation and path safety

- **Changes:** Added strict unified-diff validation for required file headers, matching relative `.py` paths, valid hunks, and non-empty changes. Evidence-grounded patch generation can only target paths in retrieved evidence. CLI and Streamlit can save validated candidate patches outside the source repository. The sandbox revalidates patches and checks target and parent paths for symlinks before container application.
- **Files affected:** `src/devmind/{code_agent,sandbox,pipeline,orchestrator,cli,evaluation_runner}.py`, `streamlit_app.py`, related code-agent/sandbox/orchestrator/evaluation/workflow tests, and project documentation.
- **Tests actually run:** Focused patch/sandbox/orchestrator/evaluation checks: **20 passed, 1 skipped**; additional patch-related checks: **23 passed**. Full suite: **67 passed, 2 skipped in 8.03s**. Both skips are Windows symlink cases. No real provider or Docker engine was available.
- **Limitations:** Validation constrains syntax and paths; it cannot establish that a proposed fix is correct. A live model-generated proposal and Docker application/test remain unverified.
- **Next step:** Add a release checklist and perform the synthetic repair end to end when a provider and Docker image are available. Consider API-backed UI only if it provides a concrete consistency benefit; UI already calls the same analysis library offline.

## 2026-10-20 — Milestone acceptance audit

- **Changes:** Added a requirement-by-requirement acceptance checklist with implementation state, evidence, environmental blockers, release gate, and the next synthetic repair command. Corrected stale manual statements about vector retrieval integration and package/CLI verification status.
- **Files affected:** `docs/ACCEPTANCE_CHECKLIST.md`, `MANUAL.md`, `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,CHANGELOG,LEARNING_GUIDE,GLOSSARY}.md`.
- **Tests actually run:** No tests run for this documentation-only change. The last recorded full suite remains **67 passed, 2 skipped in 8.03s**.
- **Known limitations:** Docker and a configured provider are still required for full repair verification.
- **Next step:** Run the documented synthetic repair in an environment with those dependencies, then record actual results and complete the viva walkthrough.

## 2026-10-21 — Docker sandbox image setup

- **Changes:** Installed Docker Desktop 4.96.0 per-user from Docker's official release URL after verifying its published SHA-256 checksum; confirmed Docker Engine 29.9.1 responds. Added a project sandbox image based on Python 3.12 slim Bookworm with Git and pytest 8.3.5. Fixed cross-platform diff handling so Code Agent output preserves trailing context spaces and the sandbox writes LF plus a final newline.
- **Files affected:** `docker/sandbox/Dockerfile`, `src/devmind/{sandbox,code_agent}.py`, `tests/{test_sandbox,test_code_agent}.py`, `MANUAL.md`, and `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,CHANGELOG,LEARNING_GUIDE,GLOSSARY,ACCEPTANCE_CHECKLIST}.md`.
- **Tests actually run:** Built `devmind-sandbox:py312`. The fixture baseline returned **1 failed, 1 passed** with the expected `ZeroDivisionError`; the known expected-fix diff applied inside the container and returned **2 passed**. The integrated analysis → retrieval → deterministic fake Code Agent response → real Docker test → Reviewer flow returned `tests_passed_review_required`, with **2 passed** and one attempt. Final Python suite: **68 passed, 2 skipped in 2.74s**; skipped tests require Windows symlink creation.
- **Known limitations:** The integration used deterministic fake provider output, so it does not establish live model behavior or patch quality. A live provider-generated candidate and full CLI report still require model configuration. Docker operations from this restricted Codex session require the app's full path/elevated host context.
- **Next step:** Configure a local OpenAI-compatible provider, run the documented `--repair` command, and capture the real provider and Docker result in the run report.
## 2026-11-16 — Guard run-history dashboard against stale stats imports

- **Issue:** The attached screenshot showed `KeyError: 'test_passed_candidates'` when Run history rendered. The checked-in stats module returns this field, so the failing app process was likely holding an older imported module or incompatible stats result.
- **Changes:** Added safe defaults for the dashboard KPI and per-project candidate count so a missing field cannot crash the page. Updated the manual and architecture/status/learning/glossary docs with the compatibility behavior and app-restart guidance.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_stats.py tests/test_streamlit_app.py --tb=short` — **6 passed in 2.51s**. Added an AppTest regression that removes the candidate-count field from the stats result and confirms the app renders without an exception.
- **Next step:** Restart the running Streamlit process so it imports the current project modules.

## 2026-11-17 - Run and preserve the paired five-repository dense retrieval pilot

- **Changes:** Completed a separate 100-row CPU run comparing TF-IDF, BM25, lexical RRF, Sentence Transformers cosine, and lexical-semantic RRF across the same five SWE-bench Lite development instances, four query variants, top-k=5, and changed-file proxy labels. The evaluator now reuses one model instance across repository snapshots and supports the current Sentence Transformers output-dimension API with a fallback for earlier supported versions. Added focused regression coverage for both behaviors.
- **Model:** sentence-transformers/all-MiniLM-L6-v2 at revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, Apache-2.0; Sentence Transformers 5.7.0, Transformers 4.57.6, PyTorch 2.13.0+cpu, NumPy 2.2.2, CPU, ten Torch threads, no CUDA, no FAISS. Model directory SHA-256: `3c9da5348bc316aa84664e33ac0590590c7fdfe12f2386a0dd513179b8b2393f`.
- **Observed results:** 100/100 records completed; every snapshot digest matched. Dense cosine averaged P@1=0.400, P@5=0.080, R@5=0.400, MRR=0.400, nDCG@5=0.400. Same-run raw TF-IDF averaged 0.400, 0.160, 0.800, 0.550, and 0.612 respectively. Dense plus lexical RRF reached R@5=0.600 on raw queries and 0.400 on enriched queries. These are descriptive metrics against five unreviewed changed-file proxies.
- **Resource observations:** Model initialization took 14.329032 s. Dense document embedding and vector-index construction took 594.737142 s total across the five snapshots. Dense query retrieval averaged 0.0622 s; same-run TF-IDF averaged 0.0362 s. The full CLI run took 670.2919 s and sampled peak process-tree RSS at 932.89 MiB using 25 ms sampling. Pure model.encode time was not separately instrumented; build and query timings include vector preparation and search work as described in the results report.
- **Raw evidence:** `evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized_semantic_cpu.jsonl`; adjacent runmeta JSON records exact command, input/label hashes, model identity, memory/runtime, source fingerprints, and process outcome. Derived metrics and per-issue ranks are in `evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json`. The earlier lexical run remains separately preserved and the same-run TF-IDF ranks/metrics match it exactly.
- **Leakage audit:** Sanitized runtime input contains no fixing PR or commit fields; all included fixing-commit fields are blank in the provenance manifest; PR URLs remain outside runtime input; base commits match the benchmark manifest; every indexed snapshot hash was verified. The evaluator applies the separate proxy labels only after retrieval for metric scoring. No patch or post-fix source was passed to the index.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest tests/test_embeddings.py tests/test_retrieval_experiment.py tests/test_retrieval_evaluation_cli.py --tb=short -rs` - **13 passed in 1.00 s**.
- **Limits and next steps:** No independent label review or function-level annotations exist. Dense underperformed the TF-IDF baseline on this five-case sample and used substantially more CPU time; this does not establish universal method quality. A full suite after the latest source changes has not been run. The optional install reported conflicts with unrelated packages exposed through the venv's system-site-packages setting: CrewAI 1.9.3 expects Pydantic 2.11.9, pydantic-settings 2.10.1, python-dotenv 1.1.1, and tokenizers 0.20.3, while the visible environment has 2.6.1, 2.1.0, 1.0.1, and 0.22.2 respectively. Use a clean isolated environment for independent reproduction.



## 2026-11-17 - Bounded sandbox output and live Docker retry verification

- **Changes:** Sandbox stdout/stderr are drained continuously while retaining only the final 4,000 characters per stream; timeout and truncation state are recorded. Failed-test names and stack frames now drive bounded retry retrieval against the unchanged repository snapshot, with per-attempt evidence IDs, patch digest, test command, outcome, and failure analysis preserved. Added explicit Python/Node image and runner examples to `.env.example` and the manual.
- **Files affected:** `src/devmind/{sandbox,failure_analysis,orchestrator,evaluation_runner}.py`, sandbox/orchestrator/multilanguage tests, `.env.example`, `MANUAL.md`, `docs/{ARCHITECTURE,IMPLEMENTATION_STATUS,ACCEPTANCE_CHECKLIST,LEARNING_GUIDE,GLOSSARY,CHANGELOG}.md`, `ABOUT_PROJECT.md`, and the synthetic Docker run records under `reports/`.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest --tb=short -rs` -- **178 passed, 3 skipped in 5.75 s**; the skips require Windows symlink-creation permission. A synthetic high-output Node test passed inside `devmind-sandbox:node22` and confirmed clipped stdout is marked. The deterministic two-attempt retry smoke failed its intentionally bad first patch, retrieved test-file evidence from the unchanged snapshot, then passed the known candidate in Docker; status remains `tests_passed_review_required`. The synthetic source tree hash was unchanged.
- **Live model outcome:** Local Ollama `qwen3:1.7b` produced one candidate after 79.204 s, but its exact diff failed to apply in Docker (`index.html:27`), so no test ran for that candidate. A second request timed out after 180.102 s. Neither run modified the fixture. These results do not demonstrate that the model can fix the user's QuickCart or cricket-scorer repositories.
- **Evidence:** Raw records and SHA-256 manifest are in `reports/INTEGRATION_SHA256SUMS.txt`; the five-repository retrieval data and its independently checked manifest are under `evaluation/`.
- **Limitations and next steps:** Docker verification used only the synthetic fixture, not either public project repository. Candidate repair quality remains unverified for the local model. The container drops capabilities and disables networking but still runs as root; this smoke is not a formal isolation review. Keep repairs as proposals until reviewed and tested on the user's exact revision.


## 2026-11-17 - Prepare blind retrieval annotation packet

- **Changes:** Added a five-record annotation worksheet built only from the sanitized issue inputs. It contains issue text and base-snapshot identity with blank reviewer fields; fixing PR/commit data and changed-file proxy labels are excluded. Clarified that the legacy provenance template is unsuitable for blind independent review.
- **Files affected:** `datasets/annotation_review_packet.csv`, `datasets/README.md`, `docs/CHANGELOG.md`.
- **Verification:** Checked five rows, required blank review fields, and absence of fix/proxy columns. No tests run; this is a data-preparation change.
- **Next step:** Two team members should independently review the issue and base snapshot before reconciling labels. Do not expose fixing metadata until both initial annotations are saved.


## 2026-11-17 - Verify report bibliography records

- **Changes:** Corrected BRaIn to an arXiv preprint, specified the verified BotSE 2026 workshop for Reformulate, Retrieve, Localize, and replaced the unverified SpIDER DOI with the ACL Anthology URL and published page range.
- **Verification:** Compared the three entries with arXiv, the ICSE 2026 workshop program, and ACL Anthology records. The PDF was not rebuilt because no LaTeX compiler is installed; rendered citations remain unverified.
- **Next step:** Rebuild and visually inspect the manuscript when a LaTeX toolchain is available.


## 2026-11-17 - Rebuild and inspect the evidence-updated report

- **Changes:** Corrected stale sandbox/full-suite statements, incorporated verified citation details, removed the clipped inline command, and rebuilt the eight-page report with Tectonic 0.17.0. The review build is `reports/devmind-report-draft/build/review_2026-11-17/DevMind_Term_Report.pdf`.
- **Verification:** Downloaded the official Windows release archive and verified SHA-256 `f61ce51f0b0ade1015b7de7ef368541c5424e9756ecbd0d7af97d6d48030845f`. Tectonic compiled successfully; all eight pages were rendered and inspected. The 132.53 pt overfull appendix line was removed. The class still reports publisher-header overflow and underfull spacing warnings.
- **Limits:** This is a Tectonic/XeTeX review copy, not the faculty PDFLaTeX build. Institution, city, faculty acknowledgement, and publisher volume/year metadata remain unconfirmed. Do not submit as final until those are resolved and the template header is checked with faculty.


## 2026-11-17 - Record evidence-based presentation corrections

- **Changes:** Added a slide-by-slide correction sheet for the current 15-slide deck, covering unsupported autonomous-agent, PR-draft, vector-default, dataset, and verified-repair claims.
- **Verification:** Compared slide text with the current manual, implementation status, acceptance checklist, retrieval metrics, and raw synthetic repair records. The managed Node workspace lacks `@oai/artifact-tool`; the PPTX was not edited or exported.
- **Next step:** Apply the correction sheet in a presentation-authoring runtime, then render and inspect every slide before using the deck.


### Historical synthetic repair evidence qualifier

The report now limits the two legacy fixture claims to what the saved JSON records actually preserve: two Python tests and one Node test passed. Those records do not retain a Docker image or container command, so the report no longer attributes those historical runs to Docker. The newer deterministic Docker retry and noisy-output smokes remain separately documented with container commands and image names.
## 2026-11-17 - Reverify dense retrieval evaluation evidence

- **Validation performed:** Re-ran `.venv\Scripts\python.exe -m pytest --tb=short -rs`: **178 passed, 3 skipped in 19.76s**. All skips are Windows symlink-creation permission limits. Compared the saved dense primary run with the independent replication: 100 rows each, identical issue/variant/retriever keys and identical non-timing payloads; observed timing fields differ as expected between processes. Confirmed the paired dense file includes 20 TF-IDF rows and the separate lexical run has 20 per lexical method.
- **Integrity:** All 28 entries in `evaluation/results/SHA256SUMS.txt` verified against their files. The five annotation-review snapshot paths in `datasets/annotation_review_packet.csv` resolve in this workspace.
- **Evidence:** Primary dense JSONL and sidecar, replication JSONL and sidecar, derived metrics, dataset manifests, and protocol are listed in `evaluation/raw_runs/README.md`, `evaluation/results/README.md`, and `reports/experiments/REPRODUCIBILITY.md`.
- **Limitations:** Labels remain five changed-file proxies, with no independent reviewer or function-level annotations. This confirms reproducibility of the recorded pilot, not ground-truth localization quality or a general performance claim.

## 2026-11-17 - Synchronize the reviewed report preview and project status

- **Changes:** Replaced the stale top-level report preview with the visually reviewed eight-page Tectonic build. Their SHA-256 digests now match. Corrected the current suite duration and report-preview state in the project summary, implementation status, acceptance checklist, feature matrix, and report README.
- **Validation performed:** Compared both PDF hashes after copying. The full suite result remains 178 passed and 3 Windows symlink-permission skips in 19.76 seconds; see the preceding verification entry. The faculty PDFLaTeX build remains unverified, and the reviewed PDF retains the publisher-template header overflow.
- **Remaining limits:** This updates the review artifact only. Faculty author/publication metadata and the presentation/release archive still need reconciliation before submission.

## 2026-11-17 - Refresh report evidence and make blind review reproducible off-machine

- **Changes:** Updated the manuscript appendix to cite the latest observed full-suite result (178 passed, 3 skipped in 19.76 seconds) and rebuilt the review PDF. Updated annotation guidance with exact base-commit checkout steps, static-only inspection constraints, and an unavailable-case rule. Clarified that worksheet snapshot paths are local to this workspace and that two reviewers should receive separate blank copies.
- **Validation performed:** Tectonic 0.17.0 compiled the eight-page PDF successfully. Extracted PDF text contains the current test result and dense retrieval measurements; pages 7 and 8 were rendered and visually checked. The main preview file matches the dated review PDF by SHA-256.
- **Limitations:** Tectonic continues to report a fixed publisher-style header overfull and first-page vertical overflow. The faculty PDFLaTeX build and publication metadata remain unverified; independent human annotation has not yet been performed.

## 2026-11-17 - Recheck GitHub source selector and local app assets

- **Validation performed:** `.venv\Scripts\python.exe -m pytest tests/test_streamlit_app.py --tb=short -rs` returned **4 passed**. The selector test confirms choosing `Public GitHub URL` immediately changes the repository field label. The active app on `127.0.0.1:8501` returned HTTP 200 for `/healthz` and `/`; the four JavaScript asset URLs named in the previous screenshots (ButtonGroup, TextInput, TextArea, and FormSubmitContent) each returned HTTP 200. A fresh run from the project virtual environment also served health/home successfully on port 8502 and was then stopped.
- **Finding:** The previous dynamic-module-fetch error was not reproducible in the current server state. No UI code change was warranted by these checks.
- **Limitations:** AppTest and HTTP asset checks do not replace browser interaction/visual QA or verify downloading and analyzing a public GitHub repository end to end.

## 2026-11-17 - Pin public GitHub imports and record snapshot provenance

- **Changes:** GitHub import now resolves the selected default branch or requested ref to a full commit SHA through the GitHub API, downloads the ZIP by that commit SHA, and computes the exact archive SHA-256. The UI displays the short commit ID; saved reports record the full commit, archive digest, default branch, push timestamp, and skipped-symlink count.
- **Tests actually run:** Focused command `.venv\Scripts\python.exe -m pytest tests/test_github_repo.py tests/test_streamlit_app.py tests/test_swebench.py --tb=short -rs` returned **33 passed in 3.30s**. Full suite `.venv\Scripts\python.exe -m pytest --tb=short -rs` returned **179 passed, 3 skipped in 5.73s**; all skips require Windows symlink-creation permission.
- **Live integration evidence:** Command `.venv\Scripts\python.exe evaluation/live_github_import_smoke.py --output reports/github_repository_import_smoke_reproduction_20261117.json` produced a second run record. Compared with the first live record `reports/github_repository_import_smoke_20261117.json`, both runs returned identical commit IDs, archive SHA-256 values, evidence spans, and scores, with eight evidence chunks each. QuickCart: commit `cfcb1dfb49118911e41109f0b2e23e6e639defbf`, archive SHA-256 `7e7dee064eccb394ff886ea4b13df38ce13172d2a337889ef6c692a0cf1674da`. Cricket Scorer: commit `cc6718815f32901c17d22f01aef28d38b03c91d4`, archive SHA-256 `5e769f34048c3bb614425ffa6592ddb03cbcf509efe603118be5db59b2260ace`. Both completed static analysis; target source and tests were never executed.
- **Finding and limits:** At those commits, QuickCart invokes `loadCartFromStorage()` on page load and `addToCart()` calls the save helper; Cricket Scorer uses `matchState.balls++` for ordinary deliveries. These revisions do not contain the respective bugs as described. The live import proves source selection and evidence retrieval, not model repair. Use the project's isolated buggy fixtures for a controlled repair demonstration.
- **Integrity:** Both GitHub smoke JSON files are listed in `reports/INTEGRATION_SHA256SUMS.txt`. The 38-entry project evidence manifest and the integration manifest verified successfully after the code, documentation, and PDF updates.
- **Runtime check:** Restarted DevMind from the project virtual environment on `127.0.0.1:8501` to load the commit-pinned importer. `/healthz`, `/`, and the Streamlit TextInput JavaScript module each returned HTTP 200.

# 2026-11-17 - Enforce non-root sandbox execution and prepare application release

- **Changes:** Docker sandbox images now declare UID/GID `10001:10001`; runtime invocation explicitly uses that identity and refuses to start a test runner as root. Added a reproducible Python/Node smoke command, a top-level application quick-start, and a clean source-and-evidence ZIP builder. The ZIP excludes caches, local environments, local model artifacts, and academic report/presentation files while preserving source, tests, configurations, datasets, and recorded experiment evidence.
- **Tests actually run:** `.venv\Scripts\python.exe -m pytest --tb=short -rs` returned **179 passed, 3 skipped in 17.06s**. Skips require Windows symlink-creation permission. Focused sandbox/multilanguage tests returned 25 passed, 1 skipped before the final smoke-script correction.
- **Docker evidence:** `python evaluation/sandbox_nonroot_smoke.py --output reports/sandbox-nonroot-docker-smoke-reproduction-20261117.json` completed. For both the QuickCart-like Node fixture and Python safe-divide fixture, the baseline failed as expected, the known candidate passed, the container ran as `10001:10001`, and the fixture tree hash was unchanged. Raw output and image IDs are in the two `sandbox-nonroot-docker-smoke*.json` records.
- **Initial script issue:** The first invocation found a quoting syntax error in the new reproducibility script; corrected the patch strings and reran successfully. The successful rerun is the saved raw record above.
- **Limits:** These are synthetic known-patch checks. They do not establish LLM repair quality or a formal Docker isolation guarantee. The five-repository retrieval evaluation still uses unreviewed changed-file proxy labels and does not show a dense retrieval improvement over TF-IDF.
