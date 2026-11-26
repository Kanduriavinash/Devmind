# 07. Implementation Details

## 1. Codebase Architecture & Module Mapping
All core application code resides strictly within `src/devmind/`, written in Python 3.12+ with type hints and explicit domain exception hierarchies:

| Module File | Key Functions / Classes | Implementation Responsibility | Verified Tests |
|---|---|---|---|
| `task_analyzer.py` | `analyze_issue()`, `_clean_text()`, `_extract_identifiers()` | Deterministic bug report cleaning, tokenization, camel/snake splitting, error categorization. | `tests/test_task_analyzer.py` (16 passed) |
| `indexer.py` | `index_repository()`, `_extract_python_chunks()`, `_extract_lexical_chunks()` | Static AST parsing for Python; lexical brace-depth scope parsing for 10+ languages; HTML `<script>` extraction. | `tests/test_multilang.py` (12 passed) |
| `retriever.py` | `TFIDFRetriever`, `BM25Retriever`, `reciprocal_rank_fusion()` | Sparse inverted index, term saturation, cosine scoring, and reciprocal rank fusion ($k=60$). | `tests/test_retriever.py` (18 passed) |
| `embeddings.py` | `SentenceTransformerEmbeddingAdapter`, `DenseRetriever` | Dense 384-d continuous vector embeddings via Sentence Transformers; exact NumPy cosine ranking. | `tests/test_embeddings.py` (8 passed) |
| `code_agent.py` | `validate_unified_diff()`, `_normalize_hunk_counts()` | Deterministic diff syntax parser, line offset recalculator, path traversal guard, no-op patch detector. | `tests/test_code_agent.py` (18 passed) |
| `sandbox.py` | `run_tests()`, `_build_docker_command()`, `_stream_output()` | Non-root container lifecycle, capability dropping, ephemeral tmpfs mounting, 4,000-char streaming logs. | `tests/test_sandbox.py` (22 passed) |
| `orchestrator.py` | `run_repair()`, `run_analysis()` | Coordinates 6-stage repair flow, executes baseline tests, manages 3-attempt retry loop with feedback synthesis. | `tests/test_orchestrator.py` (25 passed) |
| `stats.py` | `compute_dashboard_stats()`, `load_report_history()` | Ingests `reports/*.json` audit logs, calculates KPIs (Docker fix rate, patch syntax validity). | `tests/test_stats.py` (14 passed) |
| `pr_generator.py` | `generate_pr_draft()` | Formats Markdown Pull Request templates citing evidence spans `[E1]` and Docker test logs. | `tests/test_pr_generator.py` (10 passed) |
| `guide.py` | `PARAMETER_GUIDE` | Comprehensive technical reference dictionary documenting all UI parameters for viva defense. | `tests/test_guide.py` (8 passed) |
| `github_repo.py` | `download_public_repository()`, `parse_public_repository_url()` | Resolves default branch to immutable Git commit SHA, fetches bounded zip snapshot, verifies SHA-256. | `tests/test_github_repo.py` (12 passed) |

---

## 2. Mathematical Formulations

### 2.1 Dense Cosine Similarity
Given normalized query vector $\mathbf{e}_q \in \mathbb{R}^{384}$ and code chunk vector $\mathbf{e}_{d_i} \in \mathbb{R}^{384}$:
$$\text{Sim}_{\text{sem}}(q, d_i) = \frac{\mathbf{e}_q \cdot \mathbf{e}_{d_i}}{\|\mathbf{e}_q\| \|\mathbf{e}_{d_i}\|}$$

### 2.2 Okapi BM25 Lexical Ranking
Given query $q$ with terms $w$, code chunk $d$, corpus average length $\text{avgdl}$, and parameters $k_1=1.5, b=0.75$:
$$\text{Score}_{\text{BM25}}(q, d) = \sum_{w \in q} \text{IDF}(w) \cdot \frac{c(w, d) \cdot (k_1 + 1)}{c(w, d) + k_1 \cdot \left(1 - b + b \cdot \frac{|d|}{\text{avgdl}}\right)}$$
where:
$$\text{IDF}(w) = \ln \left( \frac{N - n(w) + 0.5}{n(w) + 0.5} + 1 \right)$$

### 2.3 Reciprocal Rank Fusion (RRF)
To fuse ordinal rankings from sparse lexical and dense semantic retrieval without scale distortion:
$$\text{RRF}(d) = \sum_{m \in \{\text{sem}, \text{lex}\}} \frac{1}{60 + \text{rank}_m(d)}$$
