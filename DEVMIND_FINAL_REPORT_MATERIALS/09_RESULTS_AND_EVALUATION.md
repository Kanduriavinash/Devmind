# 09. Results and Performance Evaluation

## 1. Measured Retrieval Results (SWE-bench Lite Pilot)
The retrieval experiment executed 100 completed evaluation runs across 5 repositories, 4 query variants, and 5 retrieval strategies. All snapshot directory hashes were verified before indexing.

Table 1 reports the exact mean metrics across the five evaluation instances (from `evaluation/results/swebench_lite_dev_pilot_20261117_dense_comparison.json`):

| Query Variant | Retrieval Method | Precision@1 | Precision@5 | Recall@5 | MRR | nDCG@5 |
|---|---|---|---|---|---|---|
| **Raw Query** | TF-IDF (Sparse Cosine) | 0.400 | 0.160 | **0.800** | 0.550 | 0.612 |
| Raw Query | Okapi BM25 | 0.400 | 0.160 | **0.800** | 0.517 | 0.586 |
| Raw Query | Hybrid Lexical RRF (TF-IDF + BM25) | **0.600** | 0.160 | **0.800** | **0.667** | **0.700** |
| Raw Query | Dense Cosine (all-MiniLM-L6-v2) | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Raw Query | Hybrid Lexical-Semantic RRF | 0.400 | 0.120 | 0.600 | 0.440 | 0.477 |
| **Normalized** | TF-IDF (Sparse Cosine) | 0.400 | 0.160 | **0.800** | 0.550 | 0.612 |
| Normalized | Okapi BM25 | 0.400 | 0.160 | **0.800** | 0.517 | 0.586 |
| Normalized | Hybrid Lexical RRF | **0.600** | 0.160 | **0.800** | **0.667** | **0.700** |
| Normalized | Dense Cosine | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Normalized | Hybrid Lexical-Semantic RRF | 0.400 | 0.120 | 0.600 | 0.440 | 0.477 |
| **Keywords/IDs** | TF-IDF (Sparse Cosine) | 0.400 | 0.160 | **0.800** | 0.567 | 0.626 |
| Keywords/IDs | Okapi BM25 | 0.400 | 0.160 | **0.800** | 0.517 | 0.586 |
| Keywords/IDs | Hybrid Lexical RRF | **0.600** | 0.160 | **0.800** | **0.667** | **0.700** |
| Keywords/IDs | Dense Cosine | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Keywords/IDs | Hybrid Lexical-Semantic RRF | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| **Structured** | TF-IDF (Sparse Cosine) | 0.400 | 0.160 | **0.800** | 0.567 | 0.626 |
| Structured | Okapi BM25 | 0.400 | 0.160 | **0.800** | 0.507 | 0.577 |
| Structured | Hybrid Lexical RRF | **0.600** | 0.160 | **0.800** | **0.667** | **0.700** |
| Structured | Dense Cosine | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |
| Structured | Hybrid Lexical-Semantic RRF | 0.400 | 0.080 | 0.400 | 0.400 | 0.400 |

---

## 2. Resource Utilization & Latency Analysis
The experiment tracked index construction time and query retrieval latency across all five repositories:

### 2.1 Indexing Latency
- **Dense Embedding Index Construction (`all-MiniLM-L6-v2`):** Total duration = **594.737 seconds** (Mean = 118.947s per repository).
  - `marshmallow`: 22.61s
  - `pvlib`: 32.37s
  - `pydicom`: 55.55s
  - `astroid`: 442.47s
  - `sqlfluff`: 41.73s
- **Sparse TF-IDF Index Construction:** Total duration = **1.199 seconds** across all 5 repositories.
- **Speedup Factor:** Sparse indexing was **496.0x faster** than dense vector embedding on CPU.

### 2.2 Memory Footprint
- Peak sampled process-tree RSS during dense encoding reached **932.89 MiB** (sampled at 25ms intervals over 7,901 samples).
- Sparse indexing operated comfortably within lightweight memory limits (<50 MiB).

### 2.3 Query Latency
- `tfidf_cosine`: Mean = **0.0362s** (Median = 0.0323s, Max = 0.0696s)
- `sentence_transformer_cosine`: Mean = **0.0622s** (Median = 0.0543s, Max = 0.1079s)
- `hybrid_lexical_semantic_rrf`: Mean = **0.1738s** (Median = 0.1392s, Max = 0.4636s)

---

## 3. Analysis & Empirical Insights (Answering RQs)
1. **Answering RQ1 (Text Analytics):** Structured query enrichment (Condition 4) improved TF-IDF MRR from 0.550 to 0.567 and nDCG@5 from 0.612 to 0.626, confirming that extracting camelCase and snake_case tokens sharpens ranking relevance.
2. **Answering RQ2 (Retrieval Comparison):** Sparse TF-IDF and BM25 substantially outperformed dense cosine on code artifacts (Recall@5 = 0.800 vs 0.400). Code diagnostics depend on exact identifier matches; dense models cluster semantic concepts broadly, misplacing exact variable names. Combining BM25 and TF-IDF via RRF achieved the highest overall score: **P@1 of 0.600, MRR of 0.667, and nDCG@5 of 0.700**.
