# DevMind User and Contributor Manual

DevMind analyzes software bug reports against a local source repository. It extracts text features, retrieves traceable source locations, and can ask a configured language model for a candidate diff. If Docker and a compatible test image are configured, the candidate can be tested in a disposable copy. A passing test result still requires a person to review the change.

## Current scope

- The interface is a local Streamlit application with a fixed black-and-white theme and the supplied galaxy video as its page background, darkened slightly for text contrast. Static media is served from the project `static/` directory by Streamlit. The CLI and optional loopback-only API are also available.
- The app accepts a local folder or public GitHub repository URL. For a GitHub URL, DevMind resolves the default branch to a full commit SHA, downloads that exact commit as a bounded ZIP snapshot, and records the commit and archive SHA-256 in the JSON report. Private repositories are not supported.
- An unpacked Manifest V3 extension opens the configured DevMind page and pre-fills the current GitHub repository URL. The default page is the local Streamlit app at `http://localhost:8501`.
- A hosted service and store-published Brave/Chrome extension are not included. Public GitHub snapshots are currently analyzed on the local machine.
- Python and JavaScript/TypeScript are the most complete example workflows. Inline JavaScript/TypeScript functions inside `.html` and `.htm` files are now indexed with original file line numbers; HTML markup is never executed. The indexer recognizes additional languages, but test-runner support and safety validation vary by language; see `docs/ACCEPTANCE_CHECKLIST.md`.
- Retrieval defaults to lexical TF-IDF. The research evaluator also supports BM25, lexical reciprocal-rank fusion, and optional local Sentence Transformers retrieval. In the five-instance pilot, dense cosine Recall@5 was 0.40 versus 0.80 for TF-IDF and required about 595 seconds to build dense indexes on this CPU. All labels are unreviewed changed-file proxies; see reports/experiments/RESULTS.md.
- An optional `devmind-swebench` command accepts an exported SWE-bench Lite JSONL file and explicit instance IDs, downloads each public repository at its benchmark `base_commit`, and writes patch predictions plus untested run notes. It creates proposals only; grading requires the official SWE-bench Docker harness.
- The Task Analyzer uses deterministic, rule-based text analytics. It is not a trained classifier.
- Model-generated patches are proposals. They are never applied to the selected checkout by DevMind; candidate testing uses a disposable Docker copy.

## Install and launch

Use Python 3.12 or later. From the project directory, install only the components needed for your workflow:

```powershell
python -m pip install -e ".[dev,ui]"
streamlit run streamlit_app.py
```

If the page shows `Failed to fetch dynamically imported module` for old files under `/static/js/`, hard-refresh with `Ctrl+Shift+R`. If the errors remain, clear site data/cache for `localhost:8501` and reload; the server may already be serving the current version while the browser keeps an older hashed bundle.

For the optional local API, install its extra and run `devmind-api`. It binds to `127.0.0.1:8000`; analysis requests are restricted to repository paths under the configured `DEVMIND_API_REPOSITORY_ROOTS`. The API exposes analysis and recent in-memory reports, not patch generation or test execution.

For local model calls, configure the OpenAI-compatible endpoint and model through the environment variables documented in `src/devmind/providers.py` and `.env.example`. Do not commit secrets. Model-backed actions require an available provider. Repair testing additionally requires Docker and the matching sandbox image and test-runner settings. Before starting Streamlit, set the process environment for the repository language. In PowerShell, use `$env:DEVMIND_TEST_RUNNER='node'` and `$env:DEVMIND_NODE_DOCKER_IMAGE='devmind-sandbox:node22'` for the supplied JavaScript/HTML demo; use `pytest` with `devmind-sandbox:py312` for Python projects. Restart the app after changing these values.

## Typical workflow

1. Open **Analyze and repair**. Expand **Load a demo case** to choose a preset:
   - **Cricket scorer · JavaScript ball-count bug**: Populates the cricket scorer repository, bug description, and `node` test runner.
   - **QuickCart · JavaScript cart-reload persistence bug**: Populates the QuickCart e-commerce repository, cart disappearance bug report, and `node` test runner.
   - **Safe divide · Python zero-division bug**: Populates the calculator repository and `pytest` runner.
   - **Boundary limit test · Max 3 attempts limit demo**: Demonstrates the autonomous self-healing safety boundary condition halting after 3 failed test iterations (`repair_attempt_limit_reached`).
   - **Custom Bug (Manual Entry)**: Clears the fields for manual inputs.
2. Select **Local folder** or **Public GitHub URL** inside step 1 (**Choose a repository**). This selector is live; the repository field changes immediately. Enter a local path or public `github.com` URL and describe the bug.
3. Choose **Analyze and retrieve evidence**, then press **Analyze repository** (hovering lifts the button and adds a soft outline glow). For GitHub, DevMind resolves the branch to a commit, downloads a size-limited ZIP snapshot of that commit into `.devmind/repositories`, indexes source files without executing them, and uses the bug description to retrieve relevant code. The JSON report records the full commit SHA and archive digest. The default analysis uses TF-IDF and runs locally.
4. Choose **Propose a patch** to request a model-generated candidate, or **Repair and test in Docker** to test it in a disposable copy. These options need a configured model; Docker testing also needs the Docker engine and sandbox image. If an isolated attempt fails and another attempt is allowed, DevMind parses retained test names and stack-frame cues, searches the unchanged repository again with TF-IDF, and records the new evidence selected for the retry.
5. Inspect retrieved file paths, symbols, line ranges, and snippets. Review each attempt's evidence IDs, patch digest, configured test command, result, and retained output. Sandbox reports stream output while retaining at most the final 4,000 characters of stdout/stderr and mark clipping. `tests_passed_review_required` means the selected tests passed and human review is still required.
6. **Human Review Gate & Live Code Synchronization**: When candidate patches pass sandbox tests, DevMind enforces an interactive Human Review Gate: *"❓ Should DevMind update the code in your files?"*. Clicking `[ ✅ Yes, Update Code in Files ]` writes the verified fix to the target source files (`script.js` line 451 `+= 1` or `calculator.py`) and provides exact line-by-line resolution tables. Demonstrators can refresh their web browser (`Ctrl + R`) to show the bug resolved live in the web application. A `[ 🔄 Reset Website to Buggy State ]` toggle is provided to restore the buggy state on demand for repeated presentations.
7. Save the JSON run report and candidate diff with the issue notes. The dashboard counts test-passing candidates, not verified fixes.

For a controlled cart-persistence example, `examples/quickcart-cart-reload-buggy/` contains a minimal HTML/inline-JavaScript reproduction and a Node regression test. It intentionally omits the storage restore call and is not a copy of the current public QuickCart repository; confirm any reported upstream behavior against the actual selected revision.

The dashboard shows the test pass rate only when at least one report contains an executed test run. If no test ran, it displays `N/A` rather than treating missing evidence as a 0% pass rate.
The dashboard also uses safe defaults for newer KPI fields so an older long-running Streamlit process cannot crash the whole history view during a code update. Restart the app after updating the project to load the latest statistics module.

## SWE-bench Lite evaluation

SWE-bench is an **evaluation benchmark**, not a claim that DevMind was trained on its data. Export the official `test` instances as JSONL (one record per line, retaining `instance_id`, `repo`, `base_commit`, and `problem_statement`). Run only explicit task IDs while developing:

```powershell
devmind-swebench --instances path\to\swebench-lite-test.jsonl --instance-ids django__django-12345 --top-k 4 --context-chars 1500 --predictions reports\swebench-predictions.jsonl --run-notes reports\swebench-run-notes.jsonl
```

The command statically analyzes a bounded ZIP snapshot at the exact base commit; it does not check out or execute repository code on the host. For SWE-bench only, archive symlinks are skipped rather than created on the host; run notes record how many were skipped. This may leave incomplete source context for affected tasks. The prediction file is intended for the official SWE-bench harness. Run that harness in its Docker-based environment to measure resolution; the DevMind run-notes file marks every generated patch `patch_tested: false`. Empty patches indicate a blocked or unsuccessful proposal and must not be counted as a resolved task. The official guide recommends 16 GiB RAM and 120 GiB free storage; verify host capacity before grading. Do not run the full 300-case set until a small subset, model configuration, disk capacity, and Docker setup have been checked. Keep held-out benchmark tasks out of prompt tuning and report the exact IDs and harness result.

The UI's supplied galaxy video and poster fallback load from the `static/` directory through Streamlit's static endpoint. Keep that folder alongside `streamlit_app.py` when packaging or deploying the local app. The video remains enabled when reduced motion is set because the user explicitly chose it as the page background.

## Text analytics and retrieval

The Task Analyzer applies normalization, identifier-aware tokenization, stop-word filtering, frequency-ranked keyword extraction, code-like hint extraction, and exact-token issue-category rules. Its output is deterministic and explainable, but its category accuracy has not been measured on an independently labelled corpus. TF-IDF retrieval measures lexical overlap; cosine scores rank chunks and do not establish causality. Optional embeddings require a locally available Sentence Transformers model. A five-repository CPU pilot compared dense retrieval with TF-IDF, but its one-per-issue changed-file proxy labels are weak; consult the recorded results and do not present them as validated localization accuracy.

For a controlled retrieval ablation, `devmind-query-v1` retains the raw report and generates raw, normalized, keyword/identifier, and structured query conditions. The CSV evaluation runner compares TF-IDF cosine, BM25, and equal-weight lexical reciprocal-rank fusion over the same ordered chunks and labels. If a local Sentence Transformers model is explicitly supplied, it also records dense cosine and a lexical-semantic RRF hybrid; it never downloads a model. The runner records query traces, file-level metrics, retrieval latency, index-build time, evidence spans, and an approximate whitespace-token count for retrieved source context. Its command is `devmind-retrieval-evaluate`; issue inputs and labels are separate under `datasets/`.

The checked-in SWE-bench Lite development pilot contains five instances, four query variants, and five methods: TF-IDF, BM25, lexical RRF, Sentence Transformers cosine, and lexical-semantic RRF. Dense cosine did not improve agreement with the proxy labels in this sample. The label is a fixing-patch changed-file proxy, not an independently reviewed fault location. Read reports/experiments/RESULTS.md and REPRODUCIBILITY.md before interpreting or rerunning these experiments. Do not report the pilot as benchmark resolution, exact localization accuracy, or a general semantic-retrieval result.

To install optional dense-retrieval dependencies, use `python -m pip install -e ".[embeddings]"`. Download a model separately, record its exact revision, and pass its local directory with `--embedding-model`. The evaluator will not fetch model files itself. Never commit model caches or artifacts under `.devmind/`.

```powershell
devmind-retrieval-evaluate --inputs datasets\evaluation_inputs.csv --labels datasets\retrieval_ground_truth.csv --output reports\experiments\retrieval-run.jsonl --top-k 5
# Optional, only if a model is already present locally:
devmind-retrieval-evaluate --inputs datasets\evaluation_inputs.csv --labels datasets\retrieval_ground_truth.csv --output reports\experiments\retrieval-semantic-run.jsonl --top-k 5 --embedding-model C:\models\sentence-transformer
```

The runner accepts only the documented input columns and rejects patch/fix metadata columns. It statically indexes the local base snapshot; it does not execute repository code. It writes a new JSONL file and refuses to overwrite an existing one. See [dataset instructions](datasets/README.md), [annotation rules](datasets/annotation_guidelines.md), and [retrieval protocol](evaluation/retrieval/README.md).

## Repair-strategy comparison

`devmind-evaluate` runs LLM-only, one-shot RAG, and iterative DevMind on the same supplied issue records. It runs the unmodified test suite once per issue and tests each valid candidate only in the Docker sandbox. If Docker is missing, statuses remain blocked; no patch is counted as passing. Run records include test output, prompt-size estimates, call counts, and null issue-resolution labels until a person supplies adjudicated ground truth. The current environment has no completed matched comparison. See [baseline protocol](evaluation/baselines/README.md).

## Safety and interpretation

Repository source and model output are treated as untrusted. DevMind does not import target modules to analyze them. Candidate patches are validated and tested only in a disposable Docker copy running as UID/GID `10001:10001`, with networking disabled, all Linux capabilities dropped, privilege gain disabled, a read-only container root, bounded writable tmpfs, and CPU/memory/process/time limits. These controls reduce risk but do not prove that all threats are prevented. Missing Docker configuration and operating-system launch failures are reported as blocked test runs, never as successful tests. A passing selected test suite is evidence for that run only; it does not prove the issue is resolved in every case or that regressions are absent.

The GitHub importer contacts only GitHub's repository metadata and archive hosts, accepts public HTTPS `github.com` links, caps archive and extracted sizes, rejects symlinks and unsafe paths, and never executes downloaded files. See [browser-extension/README.md](browser-extension/README.md) to install the local extension prototype.

## Project status and references

- [Implementation status](docs/IMPLEMENTATION_STATUS.md) â€” implemented work, verification evidence, and open gaps.
- [Acceptance checklist](docs/ACCEPTANCE_CHECKLIST.md) ? application and experiment evidence status.
- [Architecture](docs/ARCHITECTURE.md), [learning guide](docs/LEARNING_GUIDE.md), [glossary](docs/GLOSSARY.md), and [changelog](docs/CHANGELOG.md).
- The application ZIP contains technical documentation and experiment evidence. Academic report and presentation files are prepared separately and are excluded from the application archive.
- Project tests are in `tests/`. Run them only in an environment with the projectâ€™s development dependencies installed; record the actual command and result in the changelog.

