# DevMind — Complete File Guide & Viva Cheatsheet 📂

> **Quick Reference Guide for Project Viva & Demo**  
> Everything you need to know about every file in the repository, organized by importance so you can answer any faculty question instantly.

---

## 🎯 At a Glance: What to Open Tomorrow

If the evaluator asks *"Show me your project"*, open these 5 files:

| # | File Path | What It Is | Why It Matters |
|---|---|---|---|
| **1** | [`streamlit_app.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/streamlit_app.py) | **The Live Web UI** | Runs the interactive dashboard at `http://localhost:8501`. Features all 4 presets, live RAG retrieval cards, diff viewer, and the **Human Approval Gate** (`[ ✅ Yes, Update Code in Files ]`). |
| **2** | [`quickcart/index3.html`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/quickcart/index3.html) | **QuickCart E-Commerce App** | Full real e-commerce website with 46 loaded images. Line 2530 has the cart-reload bug where items vanish upon refresh. |
| **3** | [`cricket-scorer-pro/script.js`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/cricket-scorer-pro/script.js) | **Cricket Scorer Web App** | Live sports tracking app. Line 147 has the ball-count bug where extra deliveries count toward the 6-ball over. |
| **4** | [`src/devmind/orchestrator.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/orchestrator.py) | **Agentic AI Engine** | The autonomous multi-step loop: Plan $\to$ Tool Execution $\to$ Verification $\to$ Reflection $\to$ Halt on 3 attempts. |
| **5** | [`DEVMIND_MASTER_EXPLAINER.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/DEVMIND_MASTER_EXPLAINER.md) | **Master Theory & Math Guide** | Detailed breakdown of RAG formulas (BM25 + Cosine + RRF $k=60$), 1.7B LLM parameters, Agentic AI, and viva Q&A. |

---

## 🏗️ 1. Core Agentic AI System (`src/devmind/`)

These 8 files contain our entire self-healing software engineering pipeline:

### 1. [`src/devmind/orchestrator.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/orchestrator.py) — The Autonomous Brain 🧠
- **What it does:** Coordinates the entire repair workflow. Takes a bug report $\to$ queries the index via RAG $\to$ prompts the LLM for candidate diffs $\to$ executes tests in isolated sandbox $\to$ reads output $\to$ reflects $\to$ retries or stops.
- **Safety Boundary Limit:** Enforces `max_iterations = 3`. If tests do not pass after 3 attempts, it halts automatically to prevent infinite looping and runaway API costs.
- **Viva Hook:** *"This implements the ReAct (Reason + Act) loop pattern for code generation."*

### 2. [`src/devmind/code_agent.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/code_agent.py) — The Code Generator & Reflector ✍️
- **What it does:** Manages prompting the LLM (OpenAI-compatible or local DeepSeek/Qwen).
- **Key Feature:** Parses unified diffs (`--- a/file +++ b/file`), validates syntax before running, and constructs the "Reflection Prompt" when tests fail by feeding compiler/runtime errors back into the context.

### 3. [`src/devmind/analyzer.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/analyzer.py) — Text Analytics & Error Parser 🔍
- **What it does:** Analyzes bug reports and stack traces using NLP/text analytics techniques.
- **Key Feature:** Extracts error types (e.g., `ZeroDivisionError`, `AssertionError`, `TypeError`), target file names, line numbers, and tokenizes error logs to build semantic search queries for retrieval.

### 4. [`src/devmind/indexer.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/indexer.py) — Semantic Code Chunker 📑
- **What it does:** Indexes the codebase into searchable segments.
- **Key Feature:** Doesn't just do dumb line splitting. Uses Python AST (`ast.parse`) for Python and brace-depth/regex parsers for JavaScript to extract entire functions and classes as discrete units with docstrings and signatures preserved.

### 5. [`src/devmind/retrieval.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/retrieval.py) — Hybrid RAG Search Engine 🔎
- **What it does:** Locates buggy code snippets using a 2-stage hybrid search:
  1. **Lexical:** BM25 / TF-IDF keyword frequency scoring.
  2. **Dense Semantic:** Cosine similarity via embedding vectors ($\vec{u} \cdot \vec{v} / (\|\vec{u}\|\|\vec{v}\|)$).
  3. **Fusion:** Reciprocal Rank Fusion (RRF with constant $k=60$) merges both rankings into a final top-$k$ context window.

### 6. [`src/devmind/sandbox.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/sandbox.py) — Disposable Isolation Environment 🛡️
- **What it does:** Runs tests in disposable Docker containers or isolated subprocesses.
- **Rule (`AGENTS.md`):** Untrusted LLM-generated code is **never** executed directly on the host machine. The sandbox runs the test suite, captures exit codes and stdout/stderr, and returns telemetry to the orchestrator.

### 7. [`src/devmind/guardrails.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/guardrails.py) — Safety Guardrails 🚧
- **What it does:** Enforces strict code boundaries before candidate diffs reach testing:
  - AST validity check (disallows syntax errors).
  - Dangerous call prevention (blocks `eval()`, `exec()`, `os.system("rm -rf ...")`).
  - Line-churn bounds (rejects patches that delete or replace >50% of an unrelated file).

### 8. [`src/devmind/config.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/config.py) & [`models.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/src/devmind/models.py) — Configuration & Data Schemas ⚙️
- `config.py`: Environment variables, API keys (`OPENAI_API_KEY`, `DEEPSEEK_API_KEY`), model selection (`qwen2.5-coder:1.5b`, `deepseek-chat`), timeouts.
- `models.py`: Strongly typed dataclasses/Pydantic models for `PatchCandidate`, `ExecutionResult`, `RetrievalChunk`, and `DiagnosisReport`.

---

## 🌐 2. Web Application & Demo Files

### 1. [`streamlit_app.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/streamlit_app.py) — The Showcase Dashboard
- **Location:** Project root.
- **How to run:**
  ```powershell
  .\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
  ```
- **What it contains:**
  - **4 Presets:**
    1. `QuickCart · JavaScript cart-reload persistence bug`
    2. `Cricket scorer · JavaScript ball-count bug`
    3. `Safe divide · Python zero-division bug`
    4. `Boundary limit test · Max 3 attempts limit demo`
  - **Interactive Workflow:**
    1. Select preset or enter custom prompt.
    2. Click **Start DevMind Analysis & Repair**.
    3. See live step-by-step agent telemetry (Retrieval $\to$ Analysis $\to$ Patch generation $\to$ Verification).
    4. View unified diff comparing buggy vs repaired code.
    5. **Human Review Gate:** DevMind asks *"Should I update the code in the files?"* with:
       - `[ ✅ Yes, Update Code in Files ]`
       - `[ 🔄 Reset Website to Buggy State ]`
    6. Shows table of exact updated files and line numbers.

---

### 2. [`quickcart/`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/quickcart/) — Real Cloned E-Commerce Website 🛒
- **Source:** Directly cloned from `https://github.com/Kanduriavinash/QuickCart`.
- **Files of interest:**
  - [`quickcart/index3.html`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/quickcart/index3.html): Main store page.
    - **Line 2530:** The bug location! When buggy, `loadCartFromStorage()` is missing from `window.addEventListener('load')`, so cart items stored in `localStorage` are not populated into the UI when the user hits refresh.
    - When DevMind repairs it, `loadCartFromStorage();` is inserted back at line 2530.
  - [`quickcart/test/cart-reload.test.cjs`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/quickcart/test/cart-reload.test.cjs): Node.js test runner suite.
    - Fails on buggy code: `AssertionError [ERR_ASSERTION]: Expected 1 cart item, got 0`.
    - Passes on repaired code: `cart-reload persistence test passed`.
  - Image directories (`slider_images/`, `popular_images/`, `newarrival_images/`, `deal_images/`, `women_accesories/`, `brief_images/`): 46 high-resolution product images linked directly so the website looks crisp with zero white boxes.

---

### 3. [`cricket-scorer-pro/`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/cricket-scorer-pro/) — Live Cricket Scorer Web App 🏏
- **Files of interest:**
  - [`cricket-scorer-pro/index.html`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/cricket-scorer-pro/index.html): UI showing scoreboard, batsman runs, bowler stats, over balls.
  - [`cricket-scorer-pro/script.js`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/cricket-scorer-pro/script.js):
    - **Line 147:** The bug location! Wides (`wd`) and No-balls (`nb`) were incorrectly incrementing `currentOverBalls++`. An over was ending after 6 deliveries even if 2 were wides.
    - When DevMind repairs it: `if (!isExtra) currentOverBalls++;` is applied.
  - [`cricket-scorer-pro/test/score.test.js`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/cricket-scorer-pro/test/score.test.js): Automated Node.js test verifying extra deliveries don't increment regular balls.

---

### 4. [`examples/buggy_project/`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/examples/buggy_project/) — Python Math Module 🐍
- [`examples/buggy_project/calculator.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/examples/buggy_project/calculator.py): `divide(a, b)` does raw `return a / b`, crashing with `ZeroDivisionError` when `b == 0`.
- [`examples/buggy_project/test_calculator.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/examples/buggy_project/test_calculator.py): Pytest verifying `divide(10, 0)` returns `0` or handles division safely.

---

## 📚 3. Documentation & Viva Preparation Files

| File Path | Description |
|---|---|
| [`DEVMIND_MASTER_EXPLAINER.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/DEVMIND_MASTER_EXPLAINER.md) | **The Ultimate Viva Cheat Sheet.** Explains RAG mathematics, Reciprocal Rank Fusion, 1.7B edge parameters vs 70B+ cloud LLMs, Agentic AI feedback loop, 10-step demo breakdown, and top 10 likely examiner questions. |
| [`MANUAL.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/MANUAL.md) | User manual documenting the CLI commands (`devmind diagnose`, `devmind patch`, `devmind run`) and Streamlit web interface. |
| [`docs/ARCHITECTURE.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/docs/ARCHITECTURE.md) | Deep dive into architecture diagrams, component interactions, AST indexing, and data models. |
| [`docs/IMPLEMENTATION_STATUS.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/docs/IMPLEMENTATION_STATUS.md) | Current project status tracking all implemented features, test counts (180 passing), and presets. |
| [`docs/CHANGELOG.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/docs/CHANGELOG.md) | Audit trail of all engineering modifications, test runs, and additions. |
| [`AGENTS.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/AGENTS.md) | Project contributor guidelines and engineering safety rules. |

---

## 🧪 4. Test Suite (`tests/`)

We have **180 automated unit and integration tests** ensuring zero regressions:

```powershell
.\.venv\Scripts\python.exe -m pytest
# Result: 180 passed, 3 skipped in 13.91s
```

- [`tests/test_streamlit_app.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/tests/test_streamlit_app.py): Tests the Streamlit UI helper functions, preset resolution, patch simulation, file updating, and reset functions.
- [`tests/test_orchestrator.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/tests/test_orchestrator.py): Tests the multi-step agentic loop and verifies the 3-attempt safety halt.
- [`tests/test_retrieval.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/tests/test_retrieval.py): Tests hybrid RAG search (BM25 + Cosine similarity + RRF).
- [`tests/test_guardrails.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/tests/test_guardrails.py): Tests syntax validation and malicious code blocking.
- [`tests/test_sandbox.py`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/tests/test_sandbox.py): Tests isolation and command execution timeout handling.

---

## ⚡ 60-Second Viva Summary: What to Say

When the examiner asks: *"What did your team build, and what technologies did you use?"*

> **"We built DevMind: an Agentic AI Software Self-Healing System powered by Hybrid RAG and Text Analytics.**
> 
> 1. **Text Analytics & RAG:** When an error occurs or a bug is described, our `analyzer.py` extracts syntactic error signatures. Our `retrieval.py` executes **Hybrid RAG** combining BM25 keyword matching with dense embedding cosine similarity, fused via **Reciprocal Rank Fusion ($k=60$)** to pinpoint the exact 15 lines of buggy code across hundreds of files.
> 2. **Agentic AI:** Instead of a single one-shot text completion, DevMind runs an **autonomous ReAct loop**. It formulates a plan, generates a unified diff, executes tests in a safe sandbox, reads compiler feedback, reflects on failures, and iteratively self-corrects.
> 3. **Safety & Human Review Gate:** We implement a **strict 3-attempt iteration limit** so the agent never enters an infinite loop or drains API quota. Once verified, it asks the developer: *'Should I update the code in files?'* and applies the patch to disk only upon human approval.
> 4. **Live Verification:** We demonstrate this on real production websites—including **QuickCart** (a multi-page e-commerce app with cart-reload persistence bugs) and **Cricket Scorer Pro** (a JavaScript sports tracker with over-calculation bugs)."
