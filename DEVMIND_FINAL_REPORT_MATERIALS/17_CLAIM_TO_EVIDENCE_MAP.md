# 17. Claim-to-Evidence Verification Map

This audit matrix maps every major claim required in the research report directly to source code lines, experiment files, test outputs, or published literature:

| # | Academic Claim in Report | Verification Type | Primary File / Artifact | Exact Location / Citation | Verified Status |
|---|---|---|---|---|---|
| 1 | Deterministic task analysis extracts camelCase and snake_case tokens | Source Code & Unit Test | `src/devmind/task_analyzer.py` | Lines 35–65, `_extract_identifiers()` | Verified (16/16 tests pass) |
| 2 | Static parsing covers Python AST without host execution | Source Code & Unit Test | `src/devmind/indexer.py` | Lines 50–110, `ast.parse()` | Verified (12/12 tests pass) |
| 3 | Lexical parser extracts functions across 10+ languages and HTML scripts | Source Code & Unit Test | `src/devmind/indexer.py` | Lines 120–185, `_extract_lexical_chunks()` | Verified (12/12 tests pass) |
| 4 | Sparse TF-IDF achieves Recall@5 of 0.800 on SWE-bench pilot | Empirical Run Log | `evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json` | Lines 158, 195, 232, 269 | Verified (Exact metric: 0.800) |
| 5 | Dense Sentence Transformers scores Recall@5 of 0.400 | Empirical Run Log | `evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json` | Lines 179, 216, 253, 290 | Verified (Exact metric: 0.400) |
| 6 | Dense index construction took 594.737s vs 1.199s for TF-IDF (496x speedup) | Empirical Timing Log | `evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json` | Lines 118, `dense_document_embedding_and_index_build_seconds_total` | Verified (594.737s total) |
| 7 | Peak process memory reached 932.89 MiB RSS on CPU during dense encoding | Empirical Memory Profile | `evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json` | Line 107, `peak_process_tree_rss_mib_sampled` | Verified (932.89 MiB) |
| 8 | Diff validator recalculates line hunk counters | Source Code & Unit Test | `src/devmind/code_agent.py` | Lines 80–125, `_normalize_hunk_counts()` | Verified (18/18 tests pass) |
| 9 | Diff validator rejects directory-traversing file paths (`../`) | Source Code & Security Test | `src/devmind/code_agent.py` | Lines 45–60, path containment check | Verified (18/18 tests pass) |
| 10 | Docker sandbox enforces non-root UID 10001:10001 and `--network none` | Docker Runner & Smoke | `src/devmind/sandbox.py` | Lines 110–135, `reports/sandbox-nonroot-docker-smoke-20261117.json` | Verified (Container runs UID 10001) |
| 11 | Docker stdout/stderr is bounded to recent 4,000 characters | Source Code & Docker Smoke | `src/devmind/sandbox.py` | Line 145, `reports/sandbox-bounded-output-docker-20261117.json` | Verified (`stdout_truncated=true`) |
| 12 | Host source repository SHA-256 remains 100% byte-identical | Integration Run Log | `reports/sandbox-nonroot-docker-smoke-20261117.json` | `source_fixture_hash_matches=true` | Verified (Zero host mutation) |
| 13 | Cricket Scorer defect repaired and verified under Node test runner | Live Run & Test Output | `examples/cricket-scorer-pro-buggy/script.js` | Lines 451, 551, 601, 743, `node --test` | Verified (1 passed in 3.9ms) |
| 14 | Entire regression test suite passes cleanly | Pytest Execution Run | `.\.venv\Scripts\python.exe -m pytest` | Terminal execution timestamp 18 Nov 2026 | Verified (179 passed, 3 skipped) |
| 15 | Brave/Chrome Manifest V3 browser extension service worker operates cleanly | Extension Unit Tests | `browser-extension/tests/service-worker.test.mjs` | Terminal execution via `node --test` | Verified (3/3 passed in 111ms) |
