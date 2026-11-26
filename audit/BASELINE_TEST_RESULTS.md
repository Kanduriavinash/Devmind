# DevMind pre-change baseline

**Date:** 17 November 2026  
**Workspace:** `C:\TECH\S5\TEXT ANALYTICS\PROJECT`  
**Git commit:** unavailable; there is no `.git` metadata.  
**Source state:** no application source changes had been made for this task.

## Environment

| Item | Observed value |
|---|---|
| OS | Windows 11, build `10.0.26300` |
| Python | CPython 3.12.5, 64-bit, `.venv\Scripts\python.exe` |
| Pytest | 8.4.2 |
| Streamlit | 1.62.0 |
| NumPy | 2.2.2 |
| FastAPI / HTTPX / Pydantic | 0.115.14 / 0.28.1 / 2.6.1 |
| Docker | CLI 29.9.1 present; daemon reported “Docker Desktop is unable to start” |
| Node.js | Installed; version not captured in this baseline run |
| Sentence Transformers / FAISS | Not installed |
| LaTeX | `pdflatex`, `tectonic`, `latexmk` not found on `PATH` |

## Test command and result

```powershell
.\.venv\Scripts\python.exe -m pytest --tb=short -rs
```

```text
142 passed, 2 skipped in 4.11s
```

No tests failed. Skips:

- `tests/test_indexer_retrieval.py:79`: Windows denied symlink creation with `WinError 1314` because the required privilege was unavailable.
- `tests/test_sandbox.py:95`: Windows did not permit creating a file symlink.

An immediately preceding `.venv\Scripts\python.exe -m pytest --tb=short` run also returned **142 passed, 2 skipped**, in 16.84 seconds. Both runs used the same source state; runtime varied.

## Blockers and interpretation

- No Git commit or feature branch can be reported because the folder is not a Git repository.
- Docker sandbox execution/security could not be checked because its daemon was unavailable.
- No model request was made in this audit. Historical model-backed run reports are not reruns against this environment.
- No LaTeX compilation or slide visual review was completed; a compiler was unavailable and no deck rendering was attempted.
- This baseline measures automated test coverage only. It does not measure retrieval quality, localization accuracy, patch correctness, or general repair reliability.

Prior successful synthetic fixture records and blocked attempts were inspected. The successful records remain narrow test evidence with human review required. There is no official SWE-bench grading or completed matched three-arm experiment. See `audit/FEATURE_IMPLEMENTATION_MATRIX.md`.
