# DevMind project overview

**Project area:** Text Analytics and repository-aware software maintenance  
**Project type:** Local prototype and term-project evaluation framework  
**Status reviewed:** 17 November 2026

## What DevMind is

DevMind accepts a bug report and either a local repository folder or a public GitHub repository URL. It analyzes the report with deterministic text rules, statically indexes repository source, retrieves traceable code evidence, and can request an optional patch proposal from a configured language model. When Docker and a compatible image are available, a candidate can be tested in a disposable copy. A person remains responsible for reviewing every proposed change.

The project is an evidence-oriented educational prototype. It is not a guaranteed autonomous repair service. A candidate patch is a proposal until the selected tests run; passing those tests still does not prove that the bug is fully resolved.

## Text Analytics implementation

The Task Analyzer performs normalization and tokenization, splits common snake-case and camel-case identifiers, removes stop words, ranks keywords, extracts code-like component hints, and assigns a coarse category using exact-token rules. It is deterministic and rule-based. It is not a trained classifier, named-entity recognizer, sentiment model, or topic model. No independent issue-classification labels exist, so classification accuracy, precision, recall, and F1 are unknown.

The separate query evaluator preserves the original issue and generates four deterministic conditions: raw, normalized, keywords and identifiers, and structured text with observed component hints and a non-default category when available. Each condition records its transformation trace.

## How analysis works

1. The user supplies a bug report and a local folder or public GitHub repository URL.
2. For a public URL, DevMind downloads a bounded ZIP snapshot. It does not execute repository code on the host.
3. The indexer extracts source chunks and retains paths, symbols, and line ranges. Python uses AST extraction; JavaScript and TypeScript use lexical extraction, including inline scripts in HTML and HTM.
4. The application defaults to TF-IDF cosine retrieval. The research evaluator also supports BM25 and lexical reciprocal-rank fusion. An optional Sentence Transformers path is available when its dependency and a local model are supplied.
5. The bounded investigation workflow produces traceable evidence. A configured model may optionally propose hypotheses or a unified diff.
6. With a working Docker engine and compatible image, a candidate is tested only in a disposable copy.
7. Reports retain the evidence, proposed patch, and observed test outcome. A test-passing candidate remains subject to human review.

The public GitHub importer resolves the selected default branch to a full commit SHA, downloads the archive by that SHA, and records the commit and ZIP SHA-256 in the run report. It enforces archive, file-count, file-size, extracted-size, and path limits; private repositories are not supported. A live static-import smoke succeeded on both presentation repositories; their current commits do not exhibit the two described bugs, so use the separate buggy fixtures for a reproducible repair demonstration.

## Current retrieval pilot

A reproducible exploratory run was completed on five SWE-bench Lite development instances from five repositories. Four query variants were compared with TF-IDF, BM25, and lexical RRF, producing 60 completed records. The raw JSONL is in evaluation/raw_runs/swebench_lite_dev_pilot_20261117_anonymized.jsonl; command, input hashes, runtime, and sampled process memory are in its adjacent run metadata file.

The labels are one changed-file proxy per issue, extracted from fixing-patch metadata and not independently reviewed. They are not exact fault locations. The sample was chosen before scoring, and evaluation IDs and snapshot paths were anonymized. The base snapshot content hashes were checked before indexing. One additional candidate was excluded before indexing because its archive exceeded the importer's 100 MiB limit. The result is descriptive pilot evidence only; it does not establish general retrieval accuracy, semantic quality, or a statistically reliable improvement.

On this sample, raw TF-IDF averaged Recall@1/3/5 of 0.40/0.60/0.80, MRR 0.550, and nDCG@5 0.612. Adding extracted keywords and identifiers changed TF-IDF Recall@3 to 0.80, with Recall@1 and Recall@5 unchanged. Lexical RRF averaged Recall@1/3/5 of 0.60/0.80/0.80, MRR 0.667, and nDCG@5 0.700. All methods missed the proxy file for the pydicom instance. See reports/experiments/RESULTS.md for every method and query condition.

The paired CPU comparison ran 100 records for five methods, including all-MiniLM-L6-v2 at pinned revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41. Dense cosine averaged Recall@5 0.40, MRR 0.400, and nDCG@5 0.400, below same-run TF-IDF at 0.80, 0.550, and 0.612. Dense document embedding and index construction took 594.737 seconds; sampled peak process-tree RSS was 932.89 MiB. This is a model- and machine-specific result on five unreviewed file proxies.

## Project components

- src/devmind/analyzer.py: deterministic issue-text analysis.
- src/devmind/indexer.py: static source indexing.
- src/devmind/retrieval.py: default TF-IDF retrieval and evidence ranking.
- src/devmind/embeddings.py and src/devmind/vector_index.py: optional local dense retrieval.
- src/devmind/planner.py, investigator.py, and pipeline.py: bounded investigation and reporting.
- src/devmind/code_agent.py and src/devmind/orchestrator.py: optional patch proposal, validation, and bounded repair attempts.
- src/devmind/sandbox.py: Docker-only disposable candidate testing.
- streamlit_app.py: local Streamlit interface.
- browser-extension/: unpacked Manifest V3 Chrome/Brave launcher for the local DevMind page.
- CLI and optional loopback-only API: additional local interfaces.

The browser extension is not published in either store. There is no hosted service, private-repository authentication, automatic merge, or deployment integration.

## Controlled demonstration fixtures

The examples under examples/ are intentionally separate from the users' public repositories.

The Cricket Scorer fixture injects a ball-counting bug; its baseline Node test fails and the candidate test passed in a historical Docker run. The current public Cricket Scorer repository already increments once and was not modified.

The QuickCart-like fixture omits a local-storage restore call. In the current Docker run, its Node baseline failed and a known candidate passed 1/1 tests. A deterministic two-attempt repair then failed once, retrieved the regression test as new evidence, and passed on retry; the fixture hash was unchanged. This is a controlled integration smoke, not an upstream QuickCart repair. The current public QuickCart file already contains local-storage save/load logic and was not modified.

## Current environment and verification

- Python 3.12.5, Windows 11 build 26300, pytest 8.4.2.
- The pre-change baseline suite returned 142 passed and 2 skipped; see audit/BASELINE_TEST_RESULTS.md.
- Retrieval evaluator regressions: 13 passed in 0.70s. Latest full suite on 17 November 2026: 179 passed, 3 skipped in 17.06s; skips require Windows symlink permission. See the latest verification entry in `docs/CHANGELOG.md`.
- Public GitHub imports now pin a full commit SHA and store the exact ZIP SHA-256 in run reports. Both presentation repositories were imported and analyzed statically; the saved records include commit and archive identities. Their current source revisions already contain the described cart persistence and single-ball increment behavior, so they are not valid buggy demo inputs in their current state.
- The optional Sentence Transformers stack was installed in the project virtual environment for the pinned local-model comparison. Pip reported dependency conflicts with unrelated packages exposed from the base Python installation; the project venv uses system site packages.
- Docker Desktop 29.9.1 is currently responsive. The synthetic Docker smoke passed for the known candidate and deterministic retry. A local Qwen3 1.7B patch failed `git apply`; its follow-up model request timed out after 180 seconds. No LLM repair success or official SWE-bench grade is established.
- This workspace has no Git metadata, so it has no recoverable source commit or feature branch.
- The main app and health endpoints returned HTTP 200 on 127.0.0.1:8501. The extension service-worker suite returned 3 passed. A source-and-evidence ZIP was built and passed its archive integrity check; the builder also writes `dist/devmind-project.zip.sha256`.

## Evidence boundaries and pending work

- Retrieval pilot labels are unreviewed changed-file proxies; arrange independent human review and expand the sample before drawing conclusions.
- No supervised classification experiment or classifier accuracy result exists.
- No matched repair-arm experiment, official SWE-bench grade, or independently adjudicated resolution label exists.
- Both supplied Docker images and sandbox invocations run as UID/GID `10001:10001`; Node and Python fixture smokes passed known candidates and left source fixtures unchanged. The smoke does not establish isolation against malicious repositories.
- The dense result is limited to one pinned general-purpose model, CPU execution, five repositories, and unreviewed changed-file proxies.
- Academic report and presentation preparation are outside this application delivery. The project ZIP excludes those files and preserves the application source and experiment evidence.

The authoritative experiment record and current paper limitations are maintained in reports/experiments/ and docs/IMPLEMENTATION_STATUS.md.
