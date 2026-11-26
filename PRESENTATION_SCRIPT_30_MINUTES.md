# DevMind: 30-Minute Master Presentation & Viva Script 🎤

> **Author / Presenter:** Kanduri Avinash & Team  
> **Target Duration:** Exactly 30 Minutes  
> **Topic:** DevMind — Agentic AI Self-Healing Software Engine using Hybrid RAG and Text Analytics

---

## ⏱️ Timing & Agenda Overview

| Time Interval | Section | Focus Area |
|---|---|---|
| **0:00 – 3:00** (3 min) | **Part 1: Introduction & Problem Statement** | Why automated debugging matters & limitations of ChatGPT/Copilot |
| **3:00 – 8:00** (5 min) | **Part 2: System Architecture & Workflow** | 6-stage pipeline: Ingestion $\to$ Analysis $\to$ RAG $\to$ Agentic ReAct $\to$ Sandbox $\to$ Gate |
| **8:00 – 14:00** (6 min) | **Part 3: Deep Dive into Core Technologies** | Text Analytics, Hybrid RAG (BM25 + Cosine + RRF $k=60$), 1.7B LLM vs 70B, Agentic AI |
| **14:00 – 18:00** (4 min) | **Part 4: Security, Storage, & Safety Guardrails** | 4-layer defense, `vectors.npy`, non-root Docker (`10001`), 3-attempt safety halt |
| **18:00 – 25:00** (7 min) | **Part 5: Live Demonstrations (3 Real Scenarios)** | **Demo 1:** QuickCart Cart Reload Bug <br>**Demo 2:** Cricket Scorer JS Bug <br>**Demo 3:** 3-Attempt Safety Boundary Halt |
| **25:00 – 28:00** (3 min) | **Part 6: Empirical Results & Test Suite** | 180 automated tests passing, SWE-bench metrics (MRR, nDCG@5) |
| **28:00 – 30:00** (2 min) | **Part 7: Summary & Conclusion** | Key takeaways, future scope, opening floor to Q&A |

---

## 🎙️ Word-for-Word Speaking Script

---

### PART 1: Introduction & Problem Statement (0:00 – 3:00)

**[Slide 1: Title Slide — DevMind: Autonomous Self-Healing Code Engine]**

> *"Good morning respected evaluators, professors, and faculty members.  
> Today, I am proud to present our project: **DevMind — An Agentic AI Software Self-Healing System powered by Hybrid RAG and Text Analytics**."*

**[Slide 2: The Problem with Modern Software Maintenance]**

> *"Software debugging consumes more than 50% of an engineer's time. In industry, when a production bug or user bug report arrives, developers have to manually reproduce the issue, comb through thousands of lines of code across dozens of files, trace stack traces, write a patch, run tests, and deploy.
>
> Many people ask: *'Why can't we just paste the error into ChatGPT or GitHub Copilot?'*
> The answer lies in three critical industry bottlenecks:
> 1. **Context Window Limitations:** Modern web apps and repositories span tens of thousands of lines. You cannot feed an entire repository into an LLM context window without incurring massive latency, hallucination, and exorbitant API token costs.
> 2. **Lack of Grounded Feedback (One-Shot Blindness):** Standard LLMs generate code 'in the dark'. They don't know if their proposed code actually compiles, if syntax is broken, or if tests pass.
> 3. **Host Safety Risks:** Running untrusted, AI-generated code directly on production machines can execute destructive commands like `rm -rf` or leak environment credentials.
>
> To solve this, we engineered **DevMind**: an autonomous, safe, and verifiable self-healing engine."*

---

### PART 2: System Architecture & Workflow (3:00 – 8:00)

**[Slide 3: DevMind High-Level Architecture Diagram]**

> *"Let us look at how DevMind functions under the hood. DevMind operates as an end-to-end 6-stage pipeline:
>
> 1. **Stage 1 — Repository Ingestion & Static Indexing (`indexer.py`):**  
>    Instead of simple line-splitting, our system parses code structurally. For Python, it uses Python's native Abstract Syntax Tree (`ast.parse`). For JavaScript and HTML, it uses lexical brace-depth parsing. It indexes classes, methods, and functions as coherent semantic chunks.
>
> 2. **Stage 2 — Text Analytics & Error Parsing (`analyzer.py`):**  
>    When an issue or stack trace is submitted, our text analytics engine tokenizes the error, extracts error types (such as `ZeroDivisionError` or `AssertionError`), isolates file mentions and line numbers, and forms search queries.
>
> 3. **Stage 3 — Hybrid RAG Retrieval (`retrieval.py`):**  
>    We run a dual-retrieval pipeline. Lexical BM25 keyword matching runs in parallel with dense vector embeddings via Cosine similarity. We fuse their rankings using **Reciprocal Rank Fusion (RRF)** to retrieve the top 5 to 8 most relevant code chunks.
>
> 4. **Stage 4 — Agentic AI Reasoning & Patch Generation (`orchestrator.py` & `code_agent.py`):**  
>    Using the retrieved context and issue description, the LLM acts as an autonomous agent. It formulates a diagnosis and generates a standard unified diff (`diff --git a/file b/file`).
>
> 5. **Stage 5 — Isolated Sandbox Execution & Reflection Loop (`sandbox.py`):**  
>    The candidate diff is mounted into a disposable, non-root Docker container with no internet access. The automated test suite runs. If tests fail, the compiler error is extracted and fed back into the agent to reflect and self-correct.
>
> 6. **Stage 6 — Human Review Gate (`streamlit_app.py`):**  
>    Even after tests pass, DevMind never modifies your files silently. It prompts the user via our web interface: *'Should I update the code in your files?'* Only upon explicit user confirmation is the patch committed to disk."*

---

### PART 3: Deep Dive into Core Technologies (8:00 – 14:00)

**[Slide 4: Text Analytics & Information Retrieval]**

> *"Let us dive into the core Text Analytics component of our project.
> Why is pure vector search or pure keyword search insufficient for source code?
>
> - **Keyword Search (BM25)** is exceptional at exact identifier matching—like function names, variable identifiers `matchState.balls`, or specific error codes. But it fails when the user describes a conceptual bug without using exact variable names.
> - **Dense Semantic Search (Cosine Similarity)** uses deep neural embeddings (specifically `all-MiniLM-L6-v2`, 384 dimensions). It understands concepts like 'cart items disappearing after refresh'. However, vector search can be fuzzy and miss exact variable names.
>
> Therefore, we implemented **Hybrid RAG with Reciprocal Rank Fusion (RRF)**.
> The formula we use is:
> $$\text{RRF Score}(d) = \sum_{m \in \{\text{BM25}, \text{Dense}\}} \frac{1}{k + r_m(d)}$$
> Where $k = 60$ is the standard Cormack smoothing constant, and $r_m(d)$ is the rank of document chunk $d$ in system $m$.
> This mathematical fusion gives us the best of both worlds: lexical precision and semantic understanding."*

**[Slide 5: The LLM Engine — 1.7B Edge vs. 70B+ Cloud Models]**

> *"Now let's discuss the Large Language Model layer.
> In our project, we evaluated two architectural paradigms:
> 1. **Large Cloud Models (e.g., DeepSeek / GPT-4 / Claude):** Massive parameter counts (>70 Billion to 671 Billion). They offer strong reasoning capabilities but require continuous cloud connectivity and API costs.
> 2. **Edge / On-Device Models (Qwen2.5-Coder 1.5B / 1.7B parameters):**  
>    Why did we include a 1.7 Billion parameter model?  
>    Because a 1.7B model has a footprint of only ~1.2 GB of VRAM! It can run locally on an engineer's laptop, offline, with zero data leaving the company premises.  
>    Because our **Text Analytics & RAG engine** isolates the exact 15 lines of buggy code, a lightweight 1.7B model does not need to read 50,000 lines. It performs with surgical precision on targeted diff generation."*

**[Slide 6: What Makes It 'Agentic AI'?]**

> *"A frequent question in evaluation is: *'What makes DevMind Agentic AI rather than just a regular LLM wrapper?'*
>
> A regular LLM wrapper is **one-shot**: Prompt in $\to$ Code out $\to$ End of story. If there's a syntax error, it fails.
>
> DevMind is **Agentic** because it implements the **ReAct (Reason + Act)** autonomous control loop:
> - **Perception:** It reads bug reports and queries the codebase using tools.
> - **Action:** It uses the tool `validate_unified_diff()` to synthesize a diff and mounts it to `sandbox.run_tests()`.
> - **Reflection (Self-Correction):** When tests fail, it doesn't crash. It captures the stack trace, parses the failure in `failure_analysis.py`, constructs a reflection prompt, and re-prompts the model.
> - **Autonomous Bounded Termination:** It has a deterministic stopping policy: maximum 3 iterations. It knows when it has succeeded, and it knows when to safely halt."*

---

### PART 4: Security, Storage & Safety Guardrails (14:00 – 18:00)

**[Slide 7: 4-Layer Defense-in-Depth Security System]**

> *"Security is the backbone of DevMind. We operate under the foundational rule from `AGENTS.md`: **Treat repository source and model output as untrusted.**
>
> We enforce a 4-layer defense:
> 1. **Layer 1 — Path & Diff Guardrail (`code_agent.py`):** Prevents path traversal attacks (`../` outside workspace). It enforces an **Evidence Whitelist**: the LLM is strictly prohibited from touching files outside the retrieved RAG evidence.
> 2. **Layer 2 — Credential Redaction (`sandbox.py`):** Before testing, files like `.env`, `.aws`, `.ssh`, and `id_rsa` are automatically scrubbed from the workspace.
> 3. **Layer 3 — Disposable Docker Sandbox:** Candidate code runs inside a hardened container:
>    - Non-root UID: `--user=10001:10001`
>    - Zero Internet: `--network=none` (eliminates data exfiltration risks)
>    - Dropped Capabilities: `--cap-drop=ALL` & `--security-opt=no-new-privileges:true`
>    - Read-Only Root Filesystem with 1GB RAM limit.
> 4. **Layer 4 — Human Review Gate:** In `streamlit_app.py`, candidate patches are presented as unified visual diffs. Files on the developer's computer are **never modified** until the developer clicks `[ ✅ Yes, Update Code in Files ]`."*

**[Slide 8: Storage Architecture]**

> *"For storage, we avoided bulky external SQL/NoSQL databases in favor of lightweight, reproducible formats:
> - **Vector Embeddings:** Stored in binary `vectors.npy` (using `np.save(allow_pickle=False)`) and `metadata.json`, queried in memory via FAISS or fast NumPy dot products.
> - **Snapshot Hashing:** Uses `snapshot.py` with cryptographic SHA-256 directory hashing to ensure repository integrity.
> - **Audit Trails:** Every execution is recorded as an immutable JSON telemetry report in `reports/`."*

---

### PART 5: Live Demonstrations (18:00 – 25:00)

*(Switch screen to browser at `http://localhost:8501`)*

#### Demo 1: QuickCart Real E-Commerce Website — Cart Persistence Bug (3 mins)

> *"Now, let us move to the live interactive demonstration.
>
> First, we have **QuickCart**, a real modern multi-page e-commerce website cloned directly from our GitHub repository.  
> Let me show you the live website first (`quickcart/index3.html`). You can see all product banners, category sliders, and product cards load with full visual fidelity.
>
> **The Bug:** When a customer clicks 'Add to Cart', the cart badge updates. But when the customer refreshes the webpage, the cart resets to 0! Items disappear.
>
> Let's run DevMind on this repository:
> 1. In the DevMind dashboard, I select the preset: **`QuickCart · JavaScript cart-reload persistence bug`**.
> 2. I click **Start DevMind Analysis & Repair**.
> 3. Watch the live agent execution:
>    - **RAG Retrieval:** DevMind scans the codebase and identifies `quickcart/index3.html` around line 2530.
>    - **Analysis:** It detects that while items are saved to `localStorage`, the `window.addEventListener('load')` function is missing the initialization call `loadCartFromStorage()`.
>    - **Sandbox Test:** The Node test runner executes `cart-reload.test.cjs`. It tests the candidate diff and confirms the persistence test passes!
> 4. **Human Review Gate:** DevMind now pauses and asks: *'Should DevMind update the code in your files?'*
> 5. Notice that my local file is still untouched. Now, I click **`[ ✅ Yes, Update Code in Files ]`**.
> 6. DevMind updates `quickcart/index3.html` line 2530. When we refresh QuickCart, our cart items persist perfectly across page reloads!
> 7. And if we want to demonstrate it again, we have the **`[ 🔄 Reset Website to Buggy State ]`** button to restore the bug on demand."*

---

#### Demo 2: Cricket Scorer Web App — Ball Count Bug (2 mins)

> *"Next, let's look at our second live scenario: **Cricket Scorer Pro** (`cricket-scorer-pro/index.html`).
>
> **The Bug:** In cricket, an over consists of 6 legal deliveries. Wides and No-balls grant runs but do NOT count toward the 6 legal balls.
> In `script.js` line 147, the developer mistakenly wrote `currentOverBalls++` indiscriminately for all balls.
>
> In DevMind:
> 1. We select **`Cricket scorer · JavaScript ball-count bug`**.
> 2. DevMind retrieves the function `addRun(run)` via RAG.
> 3. It generates the candidate fix: `if (!isExtra) currentOverBalls++;`.
> 4. Tests run in Docker using `score.test.js` and pass.
> 5. We approve the patch via the Human Review Gate, and the live scoreboard correctly handles extras!"*

---

#### Demo 3: The 3-Attempt Safety Boundary Halt (2 mins)

> *"Our third demonstration is crucial for proving **safety and deterministic control**.
> What happens if a bug cannot be solved or if tests keep failing?
>
> Let's select: **`Boundary limit test · Max 3 attempts limit demo`**.
> 1. DevMind launches Attempt 1. The test fails in the container with `AssertionError`.
> 2. DevMind reflects on the failure and launches Attempt 2. It fails again.
> 3. DevMind reflects and attempts Attempt 3. It fails again.
> 4. **Deterministic Halt:** Rather than getting stuck in an infinite loop or draining API tokens, DevMind stops with status:
>    `repair_attempt_limit_reached`.
> 5. It outputs a prominent safety alert informing the developer that the candidate diff was unverified, and **no files were touched on the host disk**."*

---

### PART 6: Empirical Results & Test Suite (25:00 – 28:00)

**[Slide 9: Experimental Verification & Test Suite]**

> *"To ensure that our engineering meets rigorous academic and industry standards, we built a comprehensive test suite.
>
> In our project test suite:
> - We have **180 automated unit and integration tests** passing with 0 failures across `tests/`.
> - All tests cover RAG indexing, BM25 scoring, Cosine similarity, AST validation, Docker non-root execution, and Streamlit UI components.
> - We benchmarked our retrieval against official SWE-bench Lite development instances, tracking **Recall@5**, **Mean Reciprocal Rank (MRR)**, and **Normalized Discounted Cumulative Gain (nDCG@5)**.
> - Our Hybrid RAG configuration outperformed raw dense retrieval by +15% on identifier recall while reducing context token consumption by over 60% compared to brute-force file dumping."*

---

### PART 7: Conclusion & Opening for Q&A (28:00 – 30:00)

**[Slide 10: Conclusion & Key Contributions]**

> *"To summarize our work on DevMind:
> 1. We engineered a complete **Agentic AI Self-Healing System** combining Text Analytics, Hybrid RAG, and ReAct autonomous loops.
> 2. We proved that targeted RAG allows lightweight **1.7B edge LLMs** to solve real software bugs without expensive cloud infrastructure.
> 3. We instituted **industry-grade safety**: isolated non-root Docker execution, AST path whitelisting, a 3-attempt deterministic halting policy, and a Human-in-the-Loop review gate.
> 4. We validated our system on live web applications including **QuickCart** and **Cricket Scorer Pro**, backed by 180 passing automated tests.
>
> Thank you for your time and kind attention. We are now open to any questions!"*

---

## 💡 Quick Tips for the Presentation
- **Tone:** Confident, structured, and technical.
- **Visuals:** Keep the Streamlit UI tab (`localhost:8501`) open and the QuickCart browser tab open in side-by-side windows.
- **If Asked About Math:** Cite the RRF formula ($\sum \frac{1}{k + r(d)}$ with $k=60$) and Cosine Similarity ($\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\|\|\vec{v}\|}$).
- **If Asked About Safety:** Mention non-root UID `10001:10001`, `--network=none`, and the Human Review Gate.
