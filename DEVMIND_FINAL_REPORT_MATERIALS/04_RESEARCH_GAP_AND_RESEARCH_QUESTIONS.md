# 04. Research Gap and Research Questions

## 1. Identified Research Gaps
Despite recent breakthroughs in LLM-based software engineering, a rigorous synthesis of the literature reveals three persistent research and engineering voids:

### Gap 1: Neglect of Classical Text Analytics in the Issue Intake Stage
Most modern agentic repair frameworks (e.g., SWE-agent, AutoCodeRover) pass raw issue descriptions directly into LLM prompts without structured text analytics preprocessing. As demonstrated by Long et al. (2025) and Caumartin & Melo (2026), raw issue text contains colloquial noise, unparsed error traces, and redundant conversational filler that degrades vector retrieval. There is a lack of systematic evaluation comparing how classical text-analytics triage (identifier splitting, term frequency ranking, rule-based category extraction) influences downstream repository localization.

### Gap 2: The Code Search Evaluation Trade-off: Sparse vs. Dense on Technical Identifiers
While conversational RAG predominantly favors dense semantic embeddings (Sentence Transformers, DPR), source code contains domain-specific naming conventions (`matchState.balls`, `calculate_cart_total`) where exact token matching is paramount. Systems like SpIDER (2026) advocate dense models, but few studies quantify the practical engineering trade-offs: indexing latency, CPU memory saturation, and Top-K recall comparing sparse TF-IDF, Okapi BM25, and dense embeddings on real SWE-bench repositories.

### Gap 3: Absence of Developer-Facing Auditability and Host Execution Safety
Existing APR systems are optimized almost exclusively for benchmark leaderboard metrics (e.g., SWE-bench resolution percentage). They treat the repair process as an opaque black box:
- They do not output an evidence-grounded Pull Request draft citing exact line spans for human developer sign-off.
- They execute unconstrained bash commands directly on the host or inside privileged root containers, creating vulnerabilities.
- They do not provide an interactive visual dashboard for developers to inspect cosine similarities, per-attempt unified diffs, and container test output tails.

---

## 2. Formal Research Questions (RQs)
To directly address these gaps, DevMind formulates four empirical research questions:

- **RQ1 (Text Analytics & Query Enrichment):** How does deterministic text preprocessing (identifier splitting, stop-word removal, component hint extraction) affect code localization precision and recall compared to raw natural-language issue queries?
- **RQ2 (Retrieval Architecture Comparison):** How does sparse lexical retrieval (TF-IDF, Okapi BM25) compare against dense semantic vector retrieval (`all-MiniLM-L6-v2`) and hybrid Reciprocal Rank Fusion (RRF) in terms of Recall@5, MRR, nDCG@5, index construction latency, and memory utilization?
- **RQ3 (Syntactic Patch Validation & Integrity):** To what extent does a deterministic unified diff validation layer eliminate malformed patches, line-count errors, and directory traversal vulnerabilities produced by local open-weights LLMs?
- **RQ4 (Isolated Program Repair & Verification):** Can a bounded, failure-informed feedback loop inside a non-root, capability-dropped Docker container successfully repair multi-file defects across different programming languages without mutating the host workspace?
