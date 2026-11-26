# 00. Project Executive Summary: DevMind

## 1. Project Identity & Context
- **Project Title:** DevMind: An Evidence-Grounded Framework for Explainable Bug Analysis, Repository Localization and Sandboxed Software Repair
- **Academic Context:** B.Tech Computer Science and Engineering, Semester V
- **Course:** Text Analytics (Course Code: 22CSE314)
- **Institution:** Amrita School of Computing, Amrita Vishwa Vidyapeetham, Amritapuri Campus
- **Evaluation Cutoff Date:** 18 November 2026
- **Target Publication Venue / Format:** Procedia Computer Science (Elsevier CRC format, matching ICMLDE template)

---

## 2. Core Architectural Concept
DevMind is an evidence-grounded, local-first repository analysis and automated program repair framework. It addresses the fundamental disconnect between how users report software defects (unstructured natural language, observed runtime symptoms, partial stack traces) and how codebases represent program logic (formal abstract syntax trees, modular class/function scopes, exact token identifiers).

Rather than acting as an unconstrained, black-box agent executing arbitrary shell commands on a developer's host machine, DevMind enforces an auditable, six-stage pipeline:
1. **Deterministic Task Analysis:** Normalizes raw bug reports, splits code identifiers (`camelCase`, `snake_case`), extracts error hints, and assigns rule-based categories without black-box model drift.
2. **Static Multi-Language Ingestion:** Parses 11+ programming languages (Python AST via `ast.parse`, lexical brace-depth tracking for JS, TS, Java, C, C++, Go, Rust, C#, Ruby, PHP, Kotlin, Swift) without executing target code on the host.
3. **Two-Stage Hybrid Evidence Retrieval:** Pairs sparse lexical representations (TF-IDF and Okapi BM25) with dense semantic vector representations (`all-MiniLM-L6-v2`, 384 dimensions) using Reciprocal Rank Fusion (RRF, $k=60$) to locate culprit source functions.
4. **Deterministic Patch Validation:** Audits model-generated unified diffs for path boundary compliance, header formatting, and line offset consistency (`_normalize_hunk_counts`), rejecting directory traversal attacks and empty edits.
5. **Disposable Non-Root Docker Sandboxing:** Tests proposed patches strictly inside isolated, capability-dropped Linux containers (`UID 10001:10001`, `--network none`, `--cap-drop ALL`, `no-new-privileges`, read-only root, bounded 4,000-char streaming logs).
6. **Auditable Evidence Reporting & PR Generation:** Assembles a verified run report, cosine similarity visualizations, and Markdown Pull Request drafts citing evidence IDs (`[E1]`), maintaining a strict zero-mutation policy on the host workspace.

---

## 3. Key Empirical & Experimental Findings
1. **Lexical Superiority in Code Search:** In a controlled 5-repository pilot from SWE-bench Lite (`marshmallow`, `pvlib`, `pydicom`, `astroid`, `sqlfluff`), sparse TF-IDF achieved **Recall@5 of 0.800**, **MRR of 0.550**, and **nDCG@5 of 0.612**, outperforming dense Sentence Transformers cosine retrieval (**Recall@5 of 0.400**, **MRR of 0.400**).
2. **Indexing Efficiency:** Sparse TF-IDF indexed the pilot repositories in **1.199 seconds**, whereas dense vector embedding and index construction required **594.737 seconds** (~10 minutes, a 496x computational penalty) with 932.89 MiB peak RAM on CPU.
3. **Structured Query Enrichment:** Augmenting raw issue text with extracted code identifiers and component hints boosted TF-IDF MRR from 0.550 to 0.567 and nDCG@5 from 0.612 to 0.626.
4. **Live Defect Repair Verification:** Fixed a multi-location frontend defect in Cricket Scorer Pro (`matchState.balls += 2` changed to `+= 1` across 4 locations in `script.js`). Verified in Docker using `node --test`: **1 test passed in 3.9ms, 0 failed**.
5. **Software Rigor:** The complete codebase is verified by **179 passing automated tests** (3 skipped due to Windows symlink creation permissions).

---

## 4. Defensible Academic Positioning
- **What DevMind Is:** An engineered, reproducible, local-first text analytics and repair verification platform with empirical benchmarking of retrieval strategies on code artifacts.
- **What DevMind Is NOT:** It is not an autonomous cloud agent claiming SOTA SWE-bench resolution. It does not auto-merge patches to production. It treats model outputs and repository files as untrusted.
