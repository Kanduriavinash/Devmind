# 06. System Architecture and Methodology

## 1. End-to-End Architectural Dataflow
DevMind is structured as a decoupled, multi-stage pipeline where natural language text analytics feeds repository indexing, hybrid retrieval, candidate patch synthesis, and sandboxed test execution.

```
+-----------------------------------------------------------------------------------+
|                               1. INTAKE & TRIAGE                                  |
|   +---------------------+         +-------------------------------------------+   |
|   | User / GitHub Repo  | ------> | Task Analyzer (src/devmind/task_analyzer) |   |
|   | Bug Report (Text)   |         | NFKC, Tokenize, Camel/Snake Split, Hints  |   |
|   +---------------------+         +-------------------------------------------+   |
+-----------------------------------------|-----------------------------------------+
                                          v
+-----------------------------------------------------------------------------------+
|                        2. STATIC MULTI-LANGUAGE INDEXING                          |
|   +---------------------------------------------------------------------------+   |
|   | Multi-Language Indexer (src/devmind/indexer.py)                           |   |
|   | - Python: AST parsing (ast.parse) -> Classes, Functions, Async            |   |
|   | - 10+ Languages: Lexical brace-depth parsing -> JS, TS, Java, C++, Go     |   |
|   | - Metadata Payload: file_path, symbol, start_line, end_line, char_count   |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------|-----------------------------------------+
                                          v
+-----------------------------------------------------------------------------------+
|                          3. TWO-STAGE HYBRID RETRIEVAL                            |
|   +----------------------------+                 +----------------------------+   |
|   | Sparse Index (TF-IDF/BM25) |                 | Dense Vector Space         |   |
|   | Inverted Token Matching    |                 | all-MiniLM-L6-v2 (384-d)   |   |
|   +----------------------------+                 +----------------------------+   |
|                 \                                              /                  |
|                  \----> [ Reciprocal Rank Fusion (k=60) ] <---/                   |
|                                         |                                         |
|                                         v                                         |
|                        Top-K Ranked Evidence Spans [E1..E5]                       |
+-----------------------------------------|-----------------------------------------+
                                          v
+-----------------------------------------------------------------------------------+
|                       4. CODE GENERATION & PATCH AUDITING                         |
|   +---------------------------------------------------------------------------+   |
|   | Local LLM Synthesis (Ollama / Qwen 2.5 / DeepSeek via orchestrator.py)    |   |
|   | Output: Unified Diff conditioned strictly on evidence citations [E1]      |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|                                         v                                         |
|   +---------------------------------------------------------------------------+   |
|   | Deterministic Diff Validator (src/devmind/code_agent.py)                  |   |
|   | - Enforces repository boundary containment (no ../ traversal)             |   |
|   | - Validates unified diff header syntax (--- a/ +++ b/)                    |   |
|   | - Normalizes hunk line counts (_normalize_hunk_counts)                    |   |
|   | - Rejects empty / no-op patches                                           |   |
|   +---------------------------------------------------------------------------+   |
+-----------------------------------------|-----------------------------------------+
                                          v
+-----------------------------------------------------------------------------------+
|                       5. DISPOSABLE DOCKER SANDBOX (ISOLATION)                    |
|   +---------------------------------------------------------------------------+   |
|   | Docker Runner (src/devmind/sandbox.py)                                    |   |
|   | - Ephemeral temporary workspace copy (Host Repo Hash 100% Unchanged)      |   |
|   | - Non-Root User: UID 10001:10001                                          |   |
|   | - Hardened: --network none, --cap-drop ALL, no-new-privileges, tmpfs      |   |
|   | - Bounded Streaming: 4,000-char tail buffer for stdout/stderr             |   |
|   | - Multi-runner: pytest, node --test, mvn, cargo test, etc.                |   |
|   +---------------------------------------------------------------------------+   |
|                                         |                                         |
|              [ Tests Failed ]           |           [ Tests Passed ]              |
|                     |                   v                  |                      |
|                     |             +------------+           |                      |
|                     +-----------> | Max Tries? |           |                      |
|            Re-plan & Feed Logs    +------------+           |                      |
|            (Up to 3 attempts)           |                  |                      |
+-----------------------------------------|------------------|----------------------+
                                          v                  v
+-----------------------------------------------------------------------------------+
|                       6. PRESENTATION & AUDIT COCKPIT                             |
|   - Streamlit 3-Tab UI (Live Repair, Analytics Dashboard, Parameter Reference)    |
|   - Generated Markdown Pull Request draft with evidence citations [E1]            |
|   - Machine-Readable JSON Run Reports (reports/ directory)                        |
|   - Brave/Chrome Manifest V3 Extension for 1-Click GitHub Repository Intake       |
+-----------------------------------------------------------------------------------+
```
