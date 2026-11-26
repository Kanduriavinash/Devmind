# 🌐 Master Text Analytics & Social NLP Project Auditor & Builder Prompt

> **Instructions for your friends:**  
> Copy the prompt below and paste it directly into Antigravity in your project workspace. Antigravity will examine whatever codebase, data, and notebooks you have already created, check what was promised vs. implemented, find any research gaps, and build the missing components (RAG, Agentic AI, UI, metrics, and viva materials) to make your social text analytics project top-grade!

---

```markdown
# 🔍 COMPREHENSIVE TEXT ANALYTICS PROJECT AUDIT, RESEARCH GAP RESOLUTION & IMPLEMENTATION

You are my senior Natural Language Processing (NLP) researcher, Text Analytics expert, and lead software architect. 
We are working on a **Text Analytics / Social Media NLP project** (e.g., social media analytics, sentiment analysis, topic modeling, aspect extraction, fake news/misinformation detection, community detection, or social intelligence). 

We have an upcoming project evaluation / viva voce and need to ensure our project is 100% complete, scientifically sound, academically rigorous, and ready for an outstanding demonstration.

I want you to examine whatever we have already implemented in this repository (Python scripts, Jupyter notebooks, datasets, models, or APIs), check what we proposed vs. what is actually working, find all missing research gaps, and systematically build/fix any missing components so we have a complete, cohesive end-to-end project.

Please execute the following 8-Phase Engineering & Audit Workflow:

---

### PHASE 1: REPOSITORY DISCOVERY & RESEARCH PROPOSAL AUDIT
1. Read all files in this repository: README, project proposal documents, PPT presentations, lab reports, Jupyter notebooks, and source code.
2. Cross-reference: What research problem was proposed? What dataset(s) are used (e.g., Twitter/X, Reddit, YouTube comments, news feeds, social posts)?
3. Identify:
   - What features were promised in our presentation/report vs. what is actually implemented in code?
   - What research gaps exist? (e.g., missing baseline models, lack of ablation experiments, no comparison between traditional NLP vs. LLMs, missing error analysis)?
4. Output a clear Audit Table: Feature / Component | Proposed Status | Current Code Status | Action Needed.

---

### PHASE 2: CORE TEXT ANALYTICS & PREPROCESSING PIPELINE AUDIT
1. Audit the text analytics preprocessing:
   - Social media text cleaning: handling hashtags, mentions (@user), emojis, URLs, slang/informal abbreviations, contractions, and punctuation.
   - Core NLP stages: tokenization, stop-word removal, lemmatization/stemming, POS tagging, or Named Entity Recognition (NER).
   - Vectorization / Representation: Check representation methods used (TF-IDF, Bag-of-Words, Word2Vec/GloVe, FastText, or Transformer-based embeddings).
2. If any preprocessing steps are broken or missing, implement clean, modular Python functions in a dedicated module (e.g., `src/preprocessing.py` or similar).

---

### PHASE 3: HYBRID RAG (RETRIEVAL-AUGMENTED GENERATION) FOR SOCIAL TEXT
1. Audit or implement a **RAG (Retrieval-Augmented Generation)** subsystem tailored to our social text domain:
   - **Why RAG is needed here:** Social media posts are noisy, short, and lack context. RAG enriches short posts by retrieving background context, verified knowledge bases, previous social threads, or domain lexicons.
   - **Hybrid Retrieval:** Implement a hybrid search:
     - *Lexical Matching:* BM25 / TF-IDF for exact keywords, hashtags, and entity mentions.
     - *Dense Semantic Search:* Sentence-Transformer embeddings (e.g. `all-MiniLM-L6-v2`) via Cosine Similarity for semantic context.
     - *Reciprocal Rank Fusion (RRF):* Merge rankings with $k=60$ to get the top contextual references:
       $$\text{RRF Score}(d) = \sum_{m \in \{\text{BM25}, \text{Dense}\}} \frac{1}{k + r_m(d)}$$
   - **Storage:** Persist vector embeddings and metadata locally (e.g., `.npy` + `metadata.json` or FAISS). Keep it lightweight with zero heavy external DB setup.

---

### PHASE 4: LLM INTEGRATION & PARAMETER ANALYSIS
1. Audit how Large Language Models (LLMs) are utilized:
   - Check LLM support for analyzing, summarizing, classifying, or explaining social text patterns.
   - Ensure support for both **Cloud APIs** (OpenAI, Gemini, Anthropic, or DeepSeek) and **Local / Edge Models** (e.g. Ollama with Qwen2.5 / Llama 1B-3B parameters).
   - Document the **Parameter Analysis**: Why smaller edge models (1B–3B parameters) are effective when augmented with Text Analytics and RAG vs. massive 70B+ cloud models.
2. Implement structured prompting: Ensure LLM outputs structured JSON or clear analytical explanations with confidence scores, avoiding freeform hallucinations.

---

### PHASE 5: AGENTIC AI & MULTI-STEP REASONING LOOP
Verify that our project includes **Agentic AI** capabilities rather than being a passive one-shot classifier:
1. **Multi-Step Agentic Workflow:**
   - *Perception:* Ingest social text and retrieve relevant contextual evidence via RAG.
   - *Reasoning & Tool Use:* Agent calls specialized tools (e.g., sentiment analyzer tool, entity extractor tool, fact-checker tool, toxicity checker tool).
   - *Reflection & Self-Correction:* If an initial analysis or classification is uncertain, conflicting, or fails validation checks, the agent reflects on the discrepancy, queries additional context, and refines its verdict.
2. **Deterministic Safety Boundary:** Enforce a maximum iteration limit (e.g., max 3 reflection steps) so the agent never enters an infinite reasoning loop.

---

### PHASE 6: QUANTITATIVE EVALUATION & METRICS
1. Audit the evaluation pipeline:
   - Classification/Analytics Metrics: Precision, Recall, F1-Score (macro/weighted), Confusion Matrix, and ROC-AUC.
   - For Topic Modeling / Unsupervised clustering: Topic Coherence (C_v or U_mass) and Perplexity.
   - Retrieval/RAG Metrics: Recall@K, Mean Reciprocal Rank (MRR).
2. Generate benchmark tables comparing baseline approaches (e.g. Traditional ML: Naive Bayes / Logistic Regression / SVM + TF-IDF) vs. Modern approaches (Fine-tuned Transformers / RAG + LLM).

---

### PHASE 7: INTERACTIVE DEMO DASHBOARD (STREAMLIT / WEB UI)
1. Build or enhance an interactive web interface (e.g., `streamlit run app.py`):
   - **Interactive Live Input:** Allow the evaluator to type or paste any raw social media post / tweet / comment and see live real-time analysis.
   - **Preset Demos:** Provide 2 to 3 pre-loaded real-world examples representing challenging edge cases (e.g., sarcasm, implicit sentiment, noisy slang, ambiguous context).
   - **Visual Dashboard:** Display sentiment gauges, word clouds, entity tags, RAG retrieved context cards, and agent reflection steps.
   - **Human Review / Feedback Gate:** Allow the user to review the agent's explanation and confirm or adjust annotations.

---

### PHASE 8: AUTOMATED TESTS & VIVA PRESENTATION DELIVERABLES
1. **Automated Testing:** Implement unit and integration tests (`pytest`) covering preprocessing, vector retrieval, model inference, and UI helpers. Run all tests and ensure 100% pass rate.
2. **Viva Documentation:** Generate these markdown guides in the project root:
   - `MASTER_EXPLAINER.md`: 10-step explainer with all mathematical formulas, architecture diagrams, LLM parameter justifications, and answers to the top 10 likely viva questions.
   - `PROJECT_FILES_CHEATSHEET.md`: Quick reference guide of every file in the project, what it does, and what to show the examiner.
   - `PRESENTATION_SCRIPT.md`: Word-for-word timed 15-20 minute presentation script with slide outlines and live demo talking points.

---

**Execution instruction:**  
Begin by scanning this repository, examining our existing code and data, running any existing tests or scripts, outputting the Phase 1 Audit Report, and asking for confirmation before proceeding to build the missing pieces.
```
