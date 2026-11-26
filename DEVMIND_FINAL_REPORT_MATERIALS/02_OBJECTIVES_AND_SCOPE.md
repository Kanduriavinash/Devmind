# 02. Project Objectives and Scope

## 1. Primary Research and Engineering Objectives
DevMind was engineered to achieve six specific, testable objectives:

1. **Objective 1: Deterministic Text Analytics for Issue Triage**
   - Implement an offline, deterministic task analysis engine that preprocesses natural-language bug reports through Unicode NFKC normalization, whitespace standardization, camelCase and snake_case identifier splitting, frequency-based term ranking, and token-based error classification.
   - Deliver four reproducible query conditions: Raw, Normalized, Keywords/Identifiers, and Structured hints.

2. **Objective 2: Safe Multi-Language Static Indexing**
   - Ingest multi-file codebases across 11+ programming languages without executing target code on the host.
   - Use Python's built-in `ast.parse` for Python AST extraction (classes, functions, async methods) and a lexical brace-depth scope parser for JavaScript, TypeScript, Java, C++, Go, Rust, C#, Ruby, PHP, Kotlin, and Swift.

3. **Objective 3: Two-Stage Hybrid Evidence Retrieval**
   - Construct a dual-indexing pipeline:
     - Sparse representation: TF-IDF and Okapi BM25 ($k_1=1.5, b=0.75$) for exact identifier tokens.
     - Dense representation: Sentence Transformers `all-MiniLM-L6-v2` (384 dimensions) for semantic conceptual similarity.
   - Fuse rankings using Reciprocal Rank Fusion (RRF, $k=60$) to balance exact variable names with conceptual relevance.

4. **Objective 4: Deterministic Patch Validation and Normalization**
   - Validate model-generated unified diffs prior to execution.
   - Enforce repository path containment (rejecting directory traversal attacks like `../../`), verify standard header syntax, recalculate hunk addition/deletion offsets, and discard no-op patches.

5. **Objective 5: Disposable Non-Root Sandboxed Verification**
   - Execute test suites only in ephemeral Docker containers running as unprivileged user `UID 10001:10001`.
   - Enforce strict resource boundaries: `--network none`, `--cap-drop ALL`, `no-new-privileges:true`, read-only root with temporary in-memory tmpfs, 2 CPU limits, 2GB RAM limits, and 4,000-character streaming log capture.

6. **Objective 6: Auditable Evidence Reporting & UI Cockpit**
   - Deploy an interactive 3-tab Streamlit interface (Live Bug Repair & Pipeline Visualizer, Performance & History Dashboard, UI Parameter Guide).
   - Generate evidence-grounded Pull Request drafts linking citations `[E1]` directly to source line numbers, backed by an unpacked Manifest V3 Brave/Chrome browser extension.

---

## 2. Project Scope & Boundaries

### In-Scope (Implemented & Verified):
- Local-first processing of local folders and public GitHub repositories (via bounded immutable zip archives).
- Static AST/lexical code indexing across 11+ languages.
- Sparse TF-IDF, BM25, and dense embedding retrieval comparison.
- Local LLM connectivity (Ollama / OpenAI-compatible API endpoints).
- Deterministic diff validation and line offset recalculation.
- Ephemeral non-root Docker sandboxing with multi-runner support (`pytest`, `node --test`).
- Bounded 3-attempt self-healing retry loop.
- Full automated test suite (179 passing tests).

### Out-of-Scope (Explicitly Demarcated):
- Private GitHub repository authentication (OAuth/Tokens).
- Automated direct Git pushes or auto-merging to production branches.
- Full cloud cluster grading across the entire 2,294 SWE-bench benchmark.
- Fine-tuning of proprietary foundation LLMs.
