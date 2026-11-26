# 10. Code Repair, Validation, and Verification

## 1. Live LLM Generation Audit
To rigorously verify that DevMind genuinely invokes LLMs and generates original code patches (rather than replaying hardcoded templates), an audited live test was conducted using local Ollama (`qwen3:1.7b` / `qwen2.5-coder:1.5b`) against the Cricket Scorer Pro repository.

- **Audit Record:** `reports/live_model_generation_audit.json`
- **Model Invocation Details:**
  - Endpoint: `http://localhost:11434/v1`
  - Model ID: `qwen3:1.7b`
  - Temperature: 0.0 (deterministic generation)
  - Numbered Evidence Injected: 5 code snippets (`[E1]` through `[E5]`) from `script.js`.
- **Observed Model Generation Behavior:**
  - Small models (1.7B) correctly localized the logic fault: identified that `balls += 2` must be changed to `balls += 1`.
  - However, small open-weights models occasionally omitted standard diff edit operators (`+` or `-`), generating replacement lines with leading whitespace.
  - DevMind's deterministic diff validator intercepted this anomaly, categorized it as an empty edit / malformed patch, and halted execution before calling Docker, successfully preventing corrupt patch application.

---

## 2. Live Verification of the Cricket Scorer Defect
When supplied with a syntactically conforming unified diff targeting `examples/cricket-scorer-pro-buggy/script.js`:
- **Defect Located:** Four separate double-increment sites:
  - Line 451: `matchState.balls += 2;` $ightarrow$ `matchState.balls += 1;`
  - Line 551: `matchState.balls += 2;` $ightarrow$ `matchState.balls += 1;`
  - Line 601: `matchState.balls += 2;` $ightarrow$ `matchState.balls += 1;`
  - Line 743: `matchState.balls += 2;` $ightarrow$ `matchState.balls += 1;`
- **Sandbox Test Execution:** Ephemeral Node.js container executed `node --test test/scoring.test.cjs`:
  - **Outcome:** **1 test passed in 3.9ms, 0 failed**.
  - **Host Integrity:** Host source repository SHA-256 verified byte-identical before and after execution.
- **Live Browser Verification:** Verified in browser UI: recording deliveries increments the batsman balls by exactly 1, correctly calculating strike rate and over progression.

---

## 3. Four Levels of Verification Rigor
In academic defense, DevMind strictly separates four distinct levels of verification:
1. **Level 1 (Syntactic Diff Validity):** Diff adheres to Git unified format, valid file paths, and normalized hunk counts.
2. **Level 2 (Sandboxed Test Pass):** Candidate patch passes project unit tests inside disposable Docker container.
3. **Level 3 (Human Review Gate):** Even when tests pass, DevMind marks the status as `tests_passed_review_required`.
4. **Level 4 (SWE-bench Benchmark Grade):** Formal grading against official evaluation harness clusters (reserved for future work).
