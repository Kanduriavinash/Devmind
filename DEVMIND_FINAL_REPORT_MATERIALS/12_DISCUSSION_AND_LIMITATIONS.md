# 12. Discussion and Technical Limitations

## 1. Synthesis of Findings
DevMind demonstrates that an evidence-grounded, local-first framework can successfully bridge the gap between natural language defect reports and executable codebases. Three key insights emerge:
1. **The Domain Nuance of Code Retrieval:** In natural language NLP, dense semantic search frequently outperforms keyword search by resolving synonyms. In software engineering, however, exact identifier tokens (`function_name`, `class_name`, `variable`) are the definitive anchors of program logic. Sparse TF-IDF and BM25 achieved double the Recall@5 of dense Sentence Transformers (0.800 vs 0.400).
2. **Computational Sustainability:** Dense vector encoding required nearly 10 minutes on CPU and saturated ~1 GB RAM for five small repositories, whereas sparse TF-IDF completed in 1.199 seconds. For developer-facing IDE and CLI tools, sparse indexing delivers superior recall with negligible latency.
3. **The Necessity of Hardened Isolation:** Permitting autonomous LLMs to execute code on host developer machines poses intolerable security and corruption risks. Enforcing unprivileged non-root execution (`UID 10001:10001`) with ephemeral tmpfs ensures complete safety.

---

## 2. Transparent Engineering & Academic Limitations

### 2.1 Benchmark Scale and Proxy Labels
- The formal retrieval comparison evaluated five SWE-bench Lite development instances. While these instances are real GitHub repositories, five cases constitute an exploratory development pilot, not a statistically exhaustive benchmark.
- Ground truth is based on **changed-file proxy labels** extracted from fixing commits. These proxies do not capture multi-file contextual relevance or function-level fault localization.

### 2.2 Local Model Sensitivity
- Small local language models (1.5B–7B parameters) are prone to diff formatting errors, requiring DevMind's deterministic offset recalculator to repair malformed hunks.
- Large context windows on CPU lead to inference latency; local Ollama calls can experience timeouts if hardware resources are constrained.

### 2.3 Docker Sandboxing Boundaries
- While the sandbox drops Linux capabilities and runs as non-root UID 10001 with ephemeral tmpfs, it is not a formal cryptographic hypervisor guarantee. Highly adversarial repositories with zero-day container escape exploits could theoretically pose risks.
- Output log streaming is truncated to recent 4,000 characters; highly verbose test suites may truncate earlier compiler diagnostics.
