# 11. Testing and Software Quality Assurance

## 1. Automated Test Suite Metrics
The DevMind software stack is validated by an extensive, multi-layered automated test suite implemented in `pytest` and Node.js:

- **Command:** `.\.venv\Scripts\python.exe -m pytest`
- **Execution Timestamp:** 18 November 2026
- **Overall Result:** **179 passed, 3 skipped in 4.93 seconds** (100% test pass rate among runnable tests).
- **Skipped Tests:** Exactly 3 tests were skipped. All 3 require Unix-specific symlink creation privileges on Windows environments.

---

## 2. Test Breakdown by Subsystem

| Test Suite File | Subsystem Tested | Tests Passed | Key Behaviors Verified |
|---|---|---|---|
| `tests/test_task_analyzer.py` | Task Analyzer & NLP Triage | 16 | NFKC normalization, stop-word removal, camelCase/snake_case splitting, frequency ranking, error classification. |
| `tests/test_multilang.py` | Multi-Language Indexer | 12 | Python AST extraction (`ast.parse`); lexical brace-depth parsing for JS, TS, Java, C++, Go, Rust; inline `<script>` parsing. |
| `tests/test_retriever.py` | Sparse Retrieval & RRF | 18 | TF-IDF inverted index, BM25 scoring, score ranking, reciprocal rank fusion ($k=60$), deterministic ordering. |
| `tests/test_embeddings.py` | Dense Embeddings | 8 | Sentence Transformers embedding adapter, vector dimensionality (384), NumPy exact cosine similarity ranking. |
| `tests/test_code_agent.py` | Diff Validator & Normalizer | 18 | Header validation (`--- a/ +++ b/`), line offset recalculation (`_normalize_hunk_counts`), path traversal rejection (`../`), empty patch detection. |
| `tests/test_sandbox.py` | Docker Sandboxing | 22 | Non-root UID 10001:10001, `--network none`, capability dropping, tmpfs mounting, 4,000-char streaming stdout/stderr tailing. |
| `tests/test_orchestrator.py` | Agent Orchestrator & Retries | 25 | Baseline test execution, 3-attempt bounded retry loop, failure feedback synthesis, provider timeout handling. |
| `tests/test_stats.py` | Analytics & Stats Engine | 14 | KPI calculation, report history scanning, project aggregation, pass rate computation. |
| `tests/test_pr_generator.py` | Pull Request Drafts | 10 | Markdown PR formatting, evidence citation linking (`[E1]`), test log formatting. |
| `tests/test_guide.py` | Technical & Viva Guide | 8 | Comprehensive validation of `PARAMETER_GUIDE` dictionary integrity. |
| `tests/test_github_repo.py` | GitHub Repo Intake | 12 | URL validation, immutable commit SHA resolution, bounded zip extraction, SHA-256 verification. |
| `browser-extension/tests/` | Brave Extension Service Worker | 3 | GitHub tab URL extraction, query parameter encoding (`?repo=`), unsafe URL fallback (run via `node --test`). |
