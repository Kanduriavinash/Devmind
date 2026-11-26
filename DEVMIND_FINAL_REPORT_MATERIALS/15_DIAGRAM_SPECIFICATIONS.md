# 15. Diagram Specifications (For Manual Drawing)

As per faculty guidelines, all diagrams must be drawn manually using tools like draw.io, Lucidchart, or PowerPoint (AI-generated diagrams are strictly prohibited). Below are the exact specifications for the seven required figures:

---

### Figure 1: Overall DevMind System Architecture
- **Title:** `Fig. 1: DevMind System Architecture`
- **Caption:** `Overall multi-stage architecture of DevMind, illustrating the dataflow from natural language bug report intake through multi-language AST indexing, hybrid RAG retrieval, bounded LLM code generation, and disposable non-root Docker sandboxing.`
- **Blocks to Draw:**
  1. `Bug Report + Target Repository` (Input block)
  2. `Task Analyzer` (NFKC cleaning, identifier tokenization, rule categorization)
  3. `Static Multi-Language Indexer` (Python AST `ast.parse` + Lexical brace tokenizer for 10+ languages)
  4. `Dual Index Store` (Sparse TF-IDF/BM25 inverted index + Dense 384-d vector database)
  5. `Reciprocal Rank Fusion Engine` (RRF $k=60$ rank combiner)
  6. `Agent Orchestrator` (Local LLM via Ollama + Evidence Span Injector `[E1..E5]`)
  7. `Deterministic Diff Validator` (Syntax checking, hunk offset recalculation, path guard)
  8. `Disposable Docker Sandbox` (Unprivileged UID 10001:10001, `--network none`, tmpfs)
  9. `Presentation & Export Layer` (Streamlit 3-Tab UI, PR Draft Generator, Run Reports)
- **Connections:** Sequential arrows 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9.

---

### Figure 2: End-to-End Bug Analysis & Repair Workflow
- **Title:** `Fig. 2: End-to-End Bug Localization and Repair Workflow`
- **Caption:** `Sequential workflow of a repair session, showing candidate patch generation, syntax auditing, sandboxed test execution, and the failure-informed retry loop.`
- **Blocks to Draw:**
  1. `Start: Receive Issue Query`
  2. `Run Baseline Test Suite` (Determines if test currently fails)
  3. `Retrieve Top-5 Ranked Evidence Spans`
  4. `Synthesize Candidate Diff (LLM)`
  5. `Audit Diff Syntax & Paths (Python)`
  6. `Apply Patch in Ephemeral Container Copy`
  7. `Execute Test Suite (pytest / node)`
  8. `Decision Diamond: All Tests Pass?`
     - `Yes` -> `Approve & Generate Pull Request Draft` -> `End`
     - `No` -> `Attempt < 3?`
       - `Yes` -> `Sanitize Assertion Error Tail` -> Loop back to Block 4
       - `No` -> `Mark as repair_attempt_limit_reached` -> `End`

---

### Figure 3: Text Analytics & Preprocessing Pipeline
- **Title:** `Fig. 3: Task Analyzer NLP Preprocessing Pipeline`
- **Caption:** `Deterministic text analytics stages applied to raw bug reports to extract salient keywords, split code identifiers, and classify defect types.`
- **Blocks to Draw:**
  1. `Raw Issue Text String`
  2. `Unicode NFKC Normalization & Whitespace Cleanup`
  3. `Identifier Tokenizer` (Splits `camelCase` and `snake_case`)
  4. `Domain Stop-Word Pruning`
  5. `Term-Frequency Histogram & Salience Ranking`
  6. `Component & Path Hint Regex Extractor`
  7. `Deterministic Issue Classifier`
  8. `Output: Structured Query Vector q*`

---

### Figure 4: Repository Indexing and Hybrid Retrieval Architecture
- **Title:** `Fig. 4: Multi-Language Indexing and Hybrid RRF Retrieval`
- **Caption:** `Dual-index construction and Reciprocal Rank Fusion architecture balancing exact lexical token matching with dense semantic embeddings.`
- **Blocks to Draw:**
  1. `Source Files Tree` (11+ Languages)
  2. `Language Dispatcher` (Python vs Lexical)
  3. `Metadata Chunker` (Assigns file, symbol, line spans)
  4. `Parallel Branching:`
     - `Branch A:` `TF-IDF / Okapi BM25 Indexer` -> `Top-50 Lexical Candidates`
     - `Branch B:` `all-MiniLM-L6-v2 Encoder` -> `Top-50 Semantic Candidates`
  5. `RRF Fusion Node` ($1/(60+r_{sem}) + 1/(60+r_{lex})$)
  6. `Context Window Formatter` (Numbered spans `[E1]`, `[E2]`)

---

### Figure 5: Agent Investigation and Patch-Generation Workflow
- **Title:** `Fig. 5: Prompt Construction and Evidence-Grounded Generation`
- **Caption:** `Local LLM prompting structure, showing system role definition, evidence injection, and unified diff output constraints.`
- **Blocks to Draw:**
  1. `System Prompt: Senior Maintenance Engineer`
  2. `Structured Bug Report Summary`
  3. `Numbered Evidence Blocks [E1..E5]`
  4. `Output Constraint: Unified Diff ONLY`
  5. `Local Model Engine (Ollama / Qwen / DeepSeek)`
  6. `Raw Model Completion String`

---

### Figure 6: Patch Validation and Sandbox Testing Workflow
- **Title:** `Fig. 6: Deterministic Diff Validation and Sandbox Isolation Hardening`
- **Caption:** `Multi-stage security and syntax audit intercepting model patches before execution in unprivileged Docker containers.`
- **Blocks to Draw:**
  1. `Raw Model Diff`
  2. `Path Traversal Check` (Rejects `../` and absolute paths)
  3. `Header Format Check` (Requires `--- a/` and `+++ b/`)
  4. `Hunk Counter Recalculator` (`_normalize_hunk_counts`)
  5. `Empty Diff Rejection`
  6. `Ephemeral Docker Container Launch` (`UID 10001`, `--network none`, `tmpfs`)
  7. `Test Runner Dispatcher` (`pytest` / `node --test`)
  8. `4,000-Character Streaming Buffer`

---

### Figure 7: Experimental Evaluation Workflow
- **Title:** `Fig. 7: Paired Retrieval Evaluation Protocol`
- **Caption:** `Controlled experimental protocol evaluating five SWE-bench Lite repositories across four query conditions and three retrieval strategies.`
- **Blocks to Draw:**
  1. `5 Pinned SWE-bench Repositories (SHA-256 Verified)`
  2. `4 Query Conditions` (Raw, Normalized, Keywords/IDs, Structured)
  3. `Paired Evaluator Execution` (TF-IDF vs Dense vs Hybrid)
  4. `File-Level Collapsing`
  5. `Ground-Truth Proxy Matching`
  6. `Metric Computation Engine` (P@K, Recall@5, MRR, nDCG@5, Latency, Memory)
