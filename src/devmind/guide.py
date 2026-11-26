"""Documentation and parameter definitions for the DevMind user interface."""

from __future__ import annotations

from typing import Any

# Comprehensive documentation dictionary for every control in DevMind
PARAMETER_GUIDE: dict[str, dict[str, Any]] = {
    "preset": {
        "title": "🎯 Quick Demo Presets",
        "badge": "Demo Automation",
        "summary": "Pre-configured repository paths and verified bug reports for live evaluation and viva demonstrations.",
        "what_it_does": (
            "Selecting a preset automatically populates the repository path, issue description, "
            "and sets the optimal parameters without needing to manually type or copy-paste long Windows paths."
        ),
        "how_it_works": (
            "Pre-loads verified test cases:\n"
            "- **Cricket Scorer (JavaScript):** Targets `examples/cricket-scorer-pro-buggy` where `matchState.balls += 2` is fixed to `+= 1`.\n"
            "- **Safe Divide Calculator (Python):** Targets `examples/buggy_project` where division by zero raises `ZeroDivisionError` instead of returning `None`.\n"
            "- **Custom Bug:** Leaves fields open for any custom repository folder."
        ),
        "viva_talking_point": (
            "Examiners love to see working live demonstrations. Use this dropdown to switch instantly "
            "between JavaScript (Node.js test runner) and Python (pytest runner) bug repairs in seconds."
        ),
    },
    "repository": {
        "title": "📁 Repository Folder",
        "badge": "Input Target",
        "summary": "The local filesystem path to the codebase containing the bug to analyze or repair.",
        "what_it_does": (
            "DevMind's AST and lexical indexer crawls all supported source files in this folder "
            "without ever importing or executing them on the host system."
        ),
        "how_it_works": (
            "1. Scans eligible extensions across 11+ languages (`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.go`, `.rs`, `.cs`, etc.).\n"
            "2. Filters out ignored directories (`.git`, `.venv`, `node_modules`, `dist`, `__pycache__`).\n"
            "3. Splits code into discrete functional chunks (`FunctionDef`, `ClassDef`, `struct`, `methods`) with exact line spans."
        ),
        "safety_guarantee": (
            "Code is parsed purely as text or syntax trees. It is **never** imported or executed on your host machine."
        ),
        "viva_talking_point": (
            "In traditional debugging tools, importing code can execute malicious top-level code. "
            "DevMind maintains strict host isolation by using AST and lexical brace matching instead of imports."
        ),
    },
    "embedding_model": {
        "title": "🧠 Local Embedding Model Folder (Optional)",
        "badge": "Dense RAG",
        "summary": "Path to a local SentenceTransformers model directory for semantic vector retrieval.",
        "what_it_does": (
            "Switches DevMind from default sparse TF-IDF retrieval to dense semantic vector embeddings."
        ),
        "how_it_works": (
            "1. Loads models such as `all-MiniLM-L6-v2` locally using `SentenceTransformerProvider`.\n"
            "2. Encodes each code chunk into a high-dimensional vector representation.\n"
            "3. Operates in local-only mode: no weights or tokens are sent over the internet."
        ),
        "viva_talking_point": (
            "If the bug report uses synonyms (e.g. 'crashes on zero' vs code 'ZeroDivisionError'), "
            "dense vector embeddings map both concepts into nearby regions in vector space, finding matches that lexical keyword search might miss."
        ),
    },
    "vector_index": {
        "title": "💾 Saved Vector Index Folder (Optional)",
        "badge": "Persistence & Cache",
        "summary": "Folder outside the source repository where vector embeddings and metadata are cached.",
        "what_it_does": (
            "Persists embeddings to disk so large repositories do not need to be re-embedded on every single bug analysis."
        ),
        "how_it_works": (
            "1. Saves the embedding matrix as `vectors.npy` and chunk details as `metadata.json`.\n"
            "2. Uses **FAISS** (Facebook AI Similarity Search) when available, or exact NumPy inner-product cosine search.\n"
            "3. Validates model ID and source chunk fingerprints: automatically rebuilds the cache if repository files change."
        ),
        "viva_talking_point": (
            "Embedding thousands of code chunks is computationally heavy. Caching vectors on disk "
            "drops retrieval latency from seconds to under 5 milliseconds on repeated queries."
        ),
    },
    "top_k": {
        "title": "🔢 Evidence Results (Top-K)",
        "badge": "Context Boundary",
        "summary": "The maximum number of relevant code chunks retrieved by RAG to present to the investigator and LLM.",
        "what_it_does": (
            "Controls the size of the retrieved evidence context window (options: 3, 5, 8, 12)."
        ),
        "how_it_works": (
            "Top-K chunks are ranked by cosine similarity score. Higher K provides broader repository context, "
            "while lower K (e.g. 3–5) produces focused prompts that run faster on small local LLMs."
        ),
        "viva_talking_point": (
            "Why not send the whole codebase? LLMs suffer from 'Lost in the Middle' and hallucination when context is too large. "
            "Top-K evidence bounding isolates only the necessary context, keeping inference fast and diffs precise."
        ),
    },
    "issue_text": {
        "title": "📝 Bug Report Description",
        "badge": "Query Input",
        "summary": "Natural-language description of the software defect, expected behavior, or error logs.",
        "what_it_does": (
            "Serves as the natural-language query that drives both RAG retrieval and the agentic repair prompt."
        ),
        "how_it_works": (
            "1. `TaskAnalyzer` extracts keywords, exception types, and component hints.\n"
            "2. TF-IDF and vector similarity match issue terms against code symbols and comments.\n"
            "3. The Code Agent receives the issue alongside retrieved code snippets to write the patch."
        ),
        "viva_talking_point": (
            "Developers write bug reports in natural language, not code. DevMind bridges this gap using "
            "Text Analytics tokenization, classification, and RAG semantic matching."
        ),
    },
    "workflow_mode": {
        "title": "⚙️ Workflow Mode",
        "badge": "Execution Control",
        "summary": "Choose how deep the DevMind pipeline executes.",
        "what_it_does": (
            "- **Analyze and retrieve evidence:** Fast offline mode. Indexes repository, retrieves top-K code chunks, and generates diagnostic hypotheses. Requires NO model or Docker.\n"
            "- **Propose a patch:** Requests a unified diff from the configured LLM (e.g. Ollama Qwen3 or OpenAI API) grounded strictly in retrieved evidence.\n"
            "- **Repair and test in Docker:** The full agentic feedback loop. Generates diff, spins up a Docker container, applies diff, runs test suite, and iterates on failures."
        ),
        "viva_talking_point": (
            "This 3-tier architecture allows offline code exploration on any machine, "
            "while reserving Docker and LLM execution for verified patch synthesis."
        ),
    },
    "model_investigation": {
        "title": "🔬 Model-Cited Investigation Hypotheses",
        "badge": "Reasoning Layer",
        "summary": "Asks the LLM to hypothesize root causes citing evidence IDs (e.g. `[E1]`, `[E2]`).",
        "what_it_does": (
            "Instead of just retrieving code, the model reasons about *why* a specific function is causing the reported error."
        ),
        "how_it_works": (
            "Output claims must cite exact evidence IDs (`[E1]`). DevMind validates citations and attaches explicit "
            "uncertainty warnings (e.g. 'Similarity does not establish causality; verify with targeted tests')."
        ),
        "viva_talking_point": (
            "Crucial AI safety principle: Hypotheses are treated as unverified leads, never as facts. "
            "Only container test execution can verify a fix."
        ),
    },
    "max_attempts": {
        "title": "🔁 Repair Attempts (Agentic Feedback Loop)",
        "badge": "Feedback Loop",
        "summary": "Maximum number of iterative repair cycles (1 to 3) in Docker.",
        "what_it_does": (
            "If the candidate patch fails compiler or test checks in Docker, DevMind captures stderr/stdout "
            "and sends the error back to the Code Agent to formulate a revised patch."
        ),
        "how_it_works": (
            "Attempt 1: Generates initial diff -> Container tests fail -> Stderr captured.\n"
            "Attempt 2: LLM receives failed test output -> Generates refined diff -> Tests pass -> Reviewer approves."
        ),
        "viva_talking_point": (
            "This is the core of **Agentic AI**: unlike single-shot prompting which gives up on the first failure, "
            "DevMind reflects on runtime feedback to self-correct."
        ),
    },
}
