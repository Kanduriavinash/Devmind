# 08. Dataset and Experimental Setup

## 1. Development Evaluation Split (SWE-bench Lite Pilot)
To ground retrieval evaluation in real-world software maintenance tasks, DevMind evaluated a development split of five instances from the official SWE-bench Lite benchmark (dataset revision: `b0dde1093fe417d83b7184254edf8199c1f0dff5`):

| Evaluation ID | Repository Full Name | Pinned Base Commit SHA | Base Snapshot SHA-256 Digest | Indexed Chunks | Target Test Runner | Ground-Truth Proxy Path |
|---|---|---|---|---|---|---|
| `pilot-01` | `marshmallow-code/marshmallow` | `2be2d83a1a9a6d3d9b85804f3ab545cecc409bb0` | `ef3246f5237d09b497dcea471a8c3ac2b82e627e6cd3fa1446c12ae291d648c0` | 1,455 | pytest | `src/marshmallow/schema.py` |
| `pilot-02` | `pvlib/pvlib-python` | `04a523fafbd61bc2e49420963b84ed8e2bd1b3cf` | `68c9951af9c69d037abcdc6ec2800ffdee735f4ae21e19a1bc51272de5173a5b` | 1,233 | pytest | `pvlib/temperature.py` |
| `pilot-03` | `pydicom/pydicom` | `b9fb05c177b685bf683f7f57b2d57374eb7d882d` | `55065620aed3f0c18b5d26612b8ad9de262a04ac7a213508d839cab3048efb0f` | 2,156 | pytest | `pydicom/valuerep.py` |
| `pilot-04` | `pylint-dev/astroid` | `39c2a9805970ca57093d32bbaf0e6a63e05041d8` | `af81367b2d99162b04fcb7659bf583aeb86d589487565a8730161f43ce7a7c86` | 3,162 | pytest | `astroid/nodes/node_classes.py` |
| `pilot-05` | `sqlfluff/sqlfluff` | `304a197829f98e7425a46d872ada73176137e5ae` | `78cc37316dd845fe1171e9ff2a8c35127f89b621f9c69aec5efe3a309bc3bf13` | 1,618 | pytest | `src/sqlfluff/core/parser/helpers.py` |

### Inclusion & Exclusion Criteria:
- **Exclusion Record:** `pyvista/pyvista` was evaluated as a candidate but excluded because its pinned Git repository archive exceeded DevMind's configured 100 MiB intake limit prior to indexing.
- **Ground-Truth Annotation Rigor:** Labels represent **unreviewed changed-file proxies** derived from fixing pull request commits. They represent file-level proxy relevance, not human-adjudicated function-level fault localization. This distinction is strictly maintained to uphold academic integrity.

---

## 2. Controlled Bug Fixtures (Multi-Language Repair Trials)
In addition to the SWE-bench pilot, DevMind utilized two controlled multi-language test fixtures to evaluate live sandbox patch application and regression testing:
1. **QuickCart Store (`examples/quickcart-buggy`):** E-commerce Python/JavaScript application exhibiting cart persistence regression upon browser reload. Test runner: `pytest` and Node tests.
2. **Cricket Scorer Pro (`examples/cricket-scorer-pro-buggy`):** Interactive frontend scoring application exhibiting a batsman ball-tally double increment bug (`matchState.balls += 2`). Test runner: `node --test test/scoring.test.cjs`.

---

## 3. Hardware & Software Runtime Specifications
- **Operating System:** Windows 11 Build 26300 (AMD64)
- **Python Environment:** Python 3.12.5 (64-bit)
- **ML / NLP Libraries:** `sentence-transformers 5.7.0`, `transformers 4.57.6`, `torch 2.13.0+cpu`, `numpy 2.2.2`
- **Dense Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (pinned revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, 384 dimensions)
- **Compute Execution:** CPU inference, 10 PyTorch worker threads, FAISS disabled (exact NumPy cosine similarity fallback).
- **Container Sandbox:** Docker Desktop 29.9.1 (Linux container engine).
