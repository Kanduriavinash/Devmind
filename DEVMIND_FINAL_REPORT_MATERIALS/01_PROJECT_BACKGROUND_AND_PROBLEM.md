# 01. Project Background and Problem Statement

## 1. Background
Software engineering maintenance consumes 50% to 70% of total lifecycle resources in commercial software development. A predominant fraction of this time is spent on debugging: analyzing bug reports, navigating complex codebase hierarchies, formulating hypotheses about root causes, writing corrective patches, and verifying that fixes do not introduce regressions.

In recent years, Large Language Models (LLMs) such as GPT-4, Claude, DeepSeek-Coder, and Qwen-Coder have demonstrated remarkable fluency in code comprehension and synthesis. However, applying conversational LLMs directly to real-world software maintenance introduces substantial failure modes:
1. **Lack of Repository-Wide Visibility:** LLMs operate within constrained context windows. Feeding an entire multi-thousand-file repository into a prompt is impossible, economically prohibitive, and degrades retrieval precision ('lost in the middle' phenomenon).
2. **The Natural Language to Code Gap:** Bug reports describe user-facing symptoms ('the shopping cart resets on refresh', 'the batsman score counts double'), whereas codebases represent state machines and programmatic logic using strict syntax, camelCase/snake_case tokens, and deeply nested module hierarchies.
3. **Hallucination and Patch Malformation:** Generative models frequently hallucinate non-existent imports, misalign indentation whitespace, generate invalid Git diff headers, or propose changes to files that do not exist.
4. **Host Workspace Contamination:** Giving an AI agent direct terminal or execution access to a developer's working machine presents severe security hazards. Unverified patches can corrupt uncommitted work, alter local environment paths, or execute malicious repository scripts.

---

## 2. Formal Problem Statement
Given:
1. An unstructured natural language bug report $q$ describing a software defect, failure symptom, or regression;
2. A multi-file software repository snapshot $R = \{f_1, f_2, ..., f_N\}$ comprising source code, configuration files, and regression test suites;

The objective of DevMind is to:
1. **Understand and Enrich:** Parse and normalize $q$, extracting salient technical tokens, error categories, and component hints into a structured query $q^*$;
2. **Localize:** Retrieve a ranked set of candidate code locations $C = \{c_1, c_2, ..., c_k\} \subset R$ containing the root cause of the defect with file path, symbol, and line-span provenance;
3. **Propose:** Synthesize a syntactically valid unified diff patch $P$;
4. **Verify in Isolation:** Execute project test suites against $P$ strictly within an isolated, disposable sandbox environment, determining whether $P$ resolves the defect without introducing regressions;
5. **Audit:** Present an evidence-backed report and Pull Request draft without modifying the original host repository $R$.

---

## 3. Core Technical Challenges
- **Repository-Scale Code Search:** High-cardinality search spaces containing millions of tokens across heterogeneous languages.
- **Vocabulary Mismatch:** Resolving colloquial problem phrasing with formal programmatic identifiers.
- **Diff Parsing Fragility:** Small models (1.5B–7B parameters) frequently omit diff markers or produce incorrect hunk line counters (`@@ -l,s +l,s @@`).
- **Bounded Self-Healing:** Designing a failure feedback loop that informs the model of specific test assertion failures without leaking raw, unbounded stack traces into the prompt.
- **Host Defense:** Ensuring complete isolation of untrusted target repository code from the developer's host operating system.
