# 05. Text Analytics Methodology

## 1. Overview
As a core Text Analytics project, DevMind treats bug report triage as a disciplined natural language processing and information extraction task. The Task Analyzer (`src/devmind/task_analyzer.py`) transforms unstructured user reports into structured linguistic features.

All preprocessing techniques implemented in DevMind are **deterministic and rule-based**. No black-box machine learning classifier is used for triage, ensuring 100% reproducible, explainable feature extraction.

---

## 2. Text Preprocessing and Feature Extraction Pipeline

### 2.1 Unicode Normalization & Cleaning
- **Function:** `_clean_text()` in `src/devmind/task_analyzer.py` (Lines 15–28)
- **Algorithm:** Unicode NFKC (Compatibility Decomposition followed by Canonical Composition).
- **Purpose:** Standardizes typographic single/double quotes (`’`, `“`, `”`), curly apostrophes, mathematical minus signs, and non-breaking spaces (`\u00a0`) into standardized ASCII equivalents.
- **Input:** Raw bug report string.
- **Output:** Cleaned string with uniform whitespace and standardized punctuation.

### 2.2 Tokenization and Compound Identifier Splitting
- **Function:** `_extract_identifiers()` and `_tokenize()` in `src/devmind/task_analyzer.py` (Lines 35–65)
- **Regex Heuristics:**
  - CamelCase / PascalCase Splitting: `(?<=[a-z])(?=[A-Z])` (e.g., `calculateTotal` $ightarrow$ `['calculate', 'Total']`).
  - Snake_case / Kebab-case Splitting: `[_-]` (e.g., `match_state` $ightarrow$ `['match', 'state']`).
  - Dotted Path Splitting: `\.` (e.g., `core.utils.parser` $ightarrow$ `['core', 'utils', 'parser']`).
- **Why Crucial for Code Search:** Bug reports frequently mention colloquial terms ('total calculate'), whereas code contains `calculateTotal`. Identifier tokenization bridges this morphological gap.

### 2.3 Stop-Word Filtering & Term Frequency Ranking
- **Implementation:** Configured domain-specific stop-word set (standard English stop-words plus noisy conversational tokens like `'please'`, `'error'`, `'bug'`, `'issue'`, `'problem'`, `'fix'`).
- **Algorithm:** Frequency histogram computation $f(t) = \sum_{w \in Q} \mathbb{I}(w = t)$. Terms are ranked in descending order of frequency to select the Top-10 salient keywords.

### 2.4 Component-Hint and Path Extraction
- **Function:** `_extract_component_hints()` in `src/devmind/task_analyzer.py` (Lines 70–95)
- **Heuristic Pattern:** Detects file extensions (`.py`, `.js`, `.ts`, `.java`, `.cpp`, `.html`), directory slashes (`/` or `\\`), and backtick-enclosed identifiers (`` `save_cart` ``).
- **Output:** Explicit candidate file and component constraints that boost retrieval relevance.

### 2.5 Deterministic Issue Classification
- **Function:** `_classify_issue_type()` in `src/devmind/task_analyzer.py` (Lines 100–135)
- **Rule Set:**
  - `AttributeError` / `TypeError` / `NullPointer`: Categorized as **Type / Attribute Error**.
  - `SyntaxError` / `IndentationError`: Categorized as **Syntax Defect**.
  - `Timeout` / `Hang` / `Memory`: Categorized as **Performance / Resource Bug**.
  - `Test` / `Assert` / `Expected`: Categorized as **Regression Failure**.
  - Default fallback: **General Logic Defect**.

---

## 3. The Four Experimental Query Conditions (`devmind-query-v1`)
To measure the impact of text analytics on code retrieval (RQ1), DevMind defines four reproducible query variants in `src/devmind/retrieval_experiment.py`:

1. **Condition 1 (Raw Query):** The verbatim bug report string as submitted by the user.
2. **Condition 2 (Normalized Query):** Text after NFKC normalization, lowercase conversion, and punctuation standardization.
3. **Condition 3 (Keywords & Identifiers):** Normalized text augmented with extracted camelCase/snake_case tokens and Top-10 frequency keywords.
4. **Condition 4 (Structured Query):** The complete enriched query string: `[Category] + [Component Hints] + [Extracted Identifiers] + [Normalized Text]`.
