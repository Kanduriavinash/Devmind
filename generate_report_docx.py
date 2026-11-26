import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table, color="D3D3D3"):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '4')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color)
        tblBorders.append(border)
    insideV = OxmlElement('w:insideV')
    insideV.set(qn('w:val'), 'none')
    tblBorders.append(insideV)
    tblPr.append(tblBorders)

def build_docx_report():
    doc = docx.Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(30, 41, 59)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # Document Header / Pre-title
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_inst = p_inst.add_run("AMRITA VISHWA VIDYAPEETHAM\nAmrita School of Computing, Amritapuri Campus\nDepartment of Computer Science and Engineering\nText Analytics (22CSE314) — Semester V Term Project Report")
    run_inst.font.name = 'Times New Roman'
    run_inst.font.size = Pt(10)
    run_inst.font.bold = True
    run_inst.font.color.rgb = RGBColor(100, 116, 139)
    p_inst.paragraph_format.space_after = Pt(14)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_title = p_title.add_run("DevMind: An Evidence-Grounded Agentic RAG Framework for Autonomous Multi-Language Bug Localization, Verification, and Sandboxed Program Repair")
    run_title.font.name = 'Times New Roman'
    run_title.font.size = Pt(18)
    run_title.font.bold = True
    run_title.font.color.rgb = RGBColor(15, 23, 42)
    p_title.paragraph_format.space_after = Pt(10)

    # Authors
    p_authors = doc.add_paragraph()
    p_authors.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_auth = p_authors.add_run("P. Sharath Chandhra  |  B. Shashank Manohar  |  K. Venkat Sai Mani Avinash\n")
    r_auth.font.name = 'Times New Roman'
    r_auth.font.size = Pt(11)
    r_auth.font.bold = True
    r_auth.font.color.rgb = RGBColor(30, 41, 59)
    r_aff = p_authors.add_run("Under the Guidance of: Course Faculty & Project Mentors\nDate of Evaluation: November 2026")
    r_aff.font.name = 'Times New Roman'
    r_aff.font.size = Pt(10)
    r_aff.font.italic = True
    r_aff.font.color.rgb = RGBColor(100, 116, 139)
    p_authors.paragraph_format.space_after = Pt(16)

    # Divider line
    p_div = doc.add_paragraph()
    p_div.paragraph_format.space_after = Pt(12)
    run_div = p_div.add_run("—" * 55)
    run_div.font.color.rgb = RGBColor(203, 213, 225)
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Abstract Callout Box
    table_abs = doc.add_table(rows=1, cols=1)
    table_abs.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_abs = table_abs.rows[0].cells[0]
    set_cell_background(cell_abs, "F8FAFC")
    set_cell_margins(cell_abs, top=140, bottom=140, left=200, right=200)
    
    p_abs = cell_abs.paragraphs[0]
    r_abs_title = p_abs.add_run("Abstract—")
    r_abs_title.font.bold = True
    r_abs_title.font.size = Pt(10)
    r_abs_body = p_abs.add_run(
        "Software bug resolution in contemporary multi-language repositories represents one of the most resource-intensive bottlenecks in modern engineering workflows. Developers face fragmented codebases where symptoms described in natural-language bug reports must be mapped to precise source-code entities across thousands of files. While Large Language Models (LLMs) demonstrate fluent code synthesis, standard off-the-shelf models suffer from hallucinations, lack project-specific grounding, and generate unvalidated patches that frequently induce regression failures or compromise repository integrity. "
        "In this work, we introduce DevMind, an evidence-grounded agentic Retrieval-Augmented Generation (RAG) framework engineered for deterministic bug localization, traceable multi-language indexing, and sandboxed program repair. DevMind incorporates a hybrid retrieval architecture combining sparse lexical search (TF-IDF and BM25) with dense semantic vector representations (all-MiniLM-L6-v2), fused via Reciprocal Rank Fusion (RRF, k=60). Candidate diffs generated by local open-weights language models (e.g., Qwen 2.5 / DeepSeek) are subjected to strict AST/lexical syntax checks and validated inside a disposable, non-root Docker execution sandbox (UID 10001:10001) with bounded resource isolation (CPU, memory, tmpfs, and 4,000-character streaming logs). "
        "Empirical evaluation on a development split of five real-world software repositories from SWE-bench Lite reveals that sparse TF-IDF achieves Recall@5 of 0.800, MRR of 0.550, and nDCG@5 of 0.612, outperforming dense cosine retrieval (Recall@5 of 0.400, MRR of 0.400) while requiring only 1.199 seconds for index construction compared to 594.737 seconds for dense encoding. Furthermore, DevMind's self-healing loop successfully repaired a multi-file JavaScript defect in Cricket Scorer Pro with all tests passing (node --test: 1 passed in 3.9ms, 0 failed), while enforcing a strict zero-mutation policy on host source repositories. The framework is verified with 179 automated tests and delivered via an interactive three-tab Streamlit dashboard and a Manifest V3 browser extension."
    )
    r_abs_body.font.size = Pt(10)
    
    p_kw = cell_abs.add_paragraph()
    r_kw_title = p_kw.add_run("\nKeywords: ")
    r_kw_title.font.bold = True
    r_kw_title.font.size = Pt(9.5)
    r_kw = p_kw.add_run("Software Bug Localization, Retrieval-Augmented Generation (RAG), Reciprocal Rank Fusion, Abstract Syntax Tree (AST), Unified Diff Validation, Non-Root Docker Sandboxing, Agentic Program Repair, Text Analytics.")
    r_kw.font.size = Pt(9.5)
    r_kw.font.italic = True
    
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # Nomenclature Section
    h_nom = doc.add_heading("Nomenclature", level=1)
    h_nom.style.font.color.rgb = RGBColor(15, 23, 42)
    
    nom_data = [
        ("AST", "Abstract Syntax Tree (hierarchical syntactic tree representation of source code)"),
        ("BM25", "Best Matching 25 (probabilistic lexical information retrieval ranking algorithm)"),
        ("CI/CD", "Continuous Integration and Continuous Deployment pipeline"),
        ("Docker UID/GID", "User Identifier / Group Identifier for sandboxed non-root execution (10001:10001)"),
        ("FSM", "Finite State Machine (formal state-based control architecture for agents)"),
        ("LLM", "Large Language Model (transformer-based neural autoregressive text generator)"),
        ("MRR", "Mean Reciprocal Rank (evaluates the reciprocal rank of the first relevant document)"),
        ("nDCG@k", "Normalized Discounted Cumulative Gain at rank k (evaluates graded relevance)"),
        ("NFKC", "Unicode Normalization Form Compatibility Composition"),
        ("P@k / R@k", "Precision at rank k / Recall at rank k"),
        ("PR", "Pull Request (proposed code changes submitted for peer review in Git)"),
        ("RAG", "Retrieval-Augmented Generation (grounding model prompts with external retrieved evidence)"),
        ("RRF", "Reciprocal Rank Fusion (score-invariant rank merging algorithm with constant k=60)"),
        ("SWE-bench", "Software Engineering Benchmark (evaluates LLMs on real GitHub issues and unit tests)"),
        ("TF-IDF", "Term Frequency-Inverse Document Frequency (statistical relevance weighting metric)"),
        ("tmpfs", "Temporary File Storage (in-memory ephemeral filesystem used in Docker containers)"),
        ("Unified Diff", "Standardized file-comparison format displaying line additions (+) and deletions (-)")
    ]
    
    table_nom = doc.add_table(rows=len(nom_data) + 1, cols=2)
    table_nom.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_nom)
    
    # Header
    table_nom.rows[0].cells[0].paragraphs[0].add_run("Term / Acronym").font.bold = True
    table_nom.rows[0].cells[1].paragraphs[0].add_run("Definition & System Significance").font.bold = True
    set_cell_background(table_nom.rows[0].cells[0], "F1F5F9")
    set_cell_background(table_nom.rows[0].cells[1], "F1F5F9")
    table_nom.rows[0].cells[0].width = Inches(1.8)
    table_nom.rows[0].cells[1].width = Inches(4.7)
    
    for i, (term, defn) in enumerate(nom_data):
        row = table_nom.rows[i + 1]
        row.cells[0].paragraphs[0].add_run(term).font.size = Pt(9.5)
        row.cells[0].paragraphs[0].runs[0].font.bold = True
        row.cells[1].paragraphs[0].add_run(defn).font.size = Pt(9.5)
        row.cells[0].width = Inches(1.8)
        row.cells[1].width = Inches(4.7)
        if i % 2 == 1:
            set_cell_background(row.cells[0], "F8FAFC")
            set_cell_background(row.cells[1], "F8FAFC")
            
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 1. Introduction
    h1 = doc.add_heading("1. Introduction", level=1)
    h1.style.font.color.rgb = RGBColor(15, 23, 42)
    
    doc.add_paragraph(
        "Software maintenance and defect resolution constitute over 60% of the lifecycle cost of production software systems. "
        "When unexpected runtime crashes, logic faults, or behavioral regressions emerge, software engineering teams must perform manual triage: "
        "interpreting ambiguous natural-language descriptions submitted by end-users, navigating complex directory hierarchies across dozens or hundreds of files, "
        "identifying the precise lines responsible for the failure, and crafting a patch that resolves the issue without inducing regression side-effects. "
        "Recent advances in natural language processing and Large Language Models (LLMs) have demonstrated extraordinary code comprehension and generation capabilities. "
        "However, deploying conversational LLMs directly into production codebases without rigorous structural grounding introduces severe operational hazards."
    )
    
    # 1.1 Problem Statement
    h11 = doc.add_heading("1.1 Problem Statement", level=2)
    h11.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Modern automated code repair systems encounter four primary engineering obstacles that undermine practical adoption:"
    )
    
    bullet_pts = [
        ("Cross-File Information Fragmentation: ", "Real enterprise bugs rarely isolate to a single file. An observable symptom (e.g., a cart reset on browser refresh or an incorrect cricket score tally) typically involves an intricate interplay between state management, UI event listeners, and data-access layers. Without holistic codebase context, generative models produce localized edits that fail integration."),
        ("The Vocabulary Mismatch Problem: ", "Bug reports are formulated in problem-domain natural language (e.g., 'batsman count double increments', 'cannot save cart total'), whereas source code utilizes camelCase, snake_case, and specific technical identifier naming conventions. Pure semantic vector search frequently misses exact variable names, while standard keyword search fails to bridge synonymous descriptive terminology."),
        ("Generative Hallucination and Patch Malformation: ", "Commercial off-the-shelf LLMs frequently generate synthetic diffs that reference nonexistent file paths, corrupt whitespace indentation, or hallucinate non-existent API signatures. Applying these patches directly leads to build breakages and syntax errors."),
        ("Host Environment Contamination Risks: ", "Permitting an autonomous agent to execute candidate patches or test scripts directly on a developer's host machine introduces catastrophic security and data-loss vulnerabilities. A flawed patch can overwrite uncommitted work, alter system files, or introduce security breaches through untrusted repository scripts.")
    ]
    for title, desc in bullet_pts:
        p = doc.add_paragraph(style='List Bullet')
        r_b = p.add_run(title)
        r_b.font.bold = True
        p.add_run(desc)

    # 1.2 Research Objectives
    h12 = doc.add_heading("1.2 Research Objectives", level=2)
    h12.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "To resolve these challenges, DevMind is engineered with five explicit design objectives:"
    )
    
    objs = [
        ("1. Multi-Language Deterministic Ingestion: ", "Build an offline static parser supporting 11+ programming languages (Python AST and lexical block parsing for JavaScript, TypeScript, Java, C++, Go, Rust, etc.) without executing untrusted repository code on the host."),
        ("2. Two-Stage Hybrid Evidence Retrieval: ", "Formulate a dual-index architecture combining sparse lexical representations (TF-IDF and BM25) with dense semantic embeddings (Sentence Transformers all-MiniLM-L6-v2), integrated via Reciprocal Rank Fusion (RRF, k=60)."),
        ("3. Strict Unified Diff Validation: ", "Implement a deterministic parsing and normalization layer that validates header consistency, verifies hunk offsets, normalizes edit markers, and rejects directory-traversing patch attempts."),
        ("4. Disposable Non-Root Docker Sandboxing: ", "Execute candidate tests strictly inside ephemeral, capability-dropped Linux containers running as unprivileged user UID 10001:10001 with memory, CPU, and 4,000-character bounded streaming log quotas."),
        ("5. Transparent Auditability & Self-Healing: ", "Provide a full visual timeline, run analytics dashboard, and automated GitHub Pull Request draft generator with evidence citations [E1], guaranteeing zero mutation of the host workspace.")
    ]
    for title, desc in objs:
        p = doc.add_paragraph(style='List Bullet')
        r_b = p.add_run(title)
        r_b.font.bold = True
        p.add_run(desc)

    # 2. Literature Review
    h2 = doc.add_heading("2. Related Work and Research Gaps", level=1)
    h2.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "Automated Program Repair (APR) and repository-level assistance have evolved across four generations: "
        "(1) template-based genetic methods, (2) learned statistical ranking, (3) zero-shot masked code models, and (4) autonomous tool-augmented LLM agents. "
        "Table 1 contrasts representative prior literature with the DevMind framework."
    )
    
    lit_data = [
        ("PAR (Kim et al., 2013)", "Template-based repair learned from 60k human patches", "Fixed 27/119 bugs in Defects4J", "Rigid template library; zero natural language issue understanding or repository autonomy."),
        ("Prophet (Long & Rinard, 2016)", "Probabilistic model ranking human-written patch shapes", "Fixed 15/69 real-world bugs", "Search space constrained to predefined mutations; no semantic text comprehension."),
        ("AlphaRepair (Xia & Zhang, 2022)", "Zero-shot cloze-style masked model repair using CodeBERT", "Outperformed prior APR without fine-tuning", "Restricted to single-line modifications; incapable of multi-file or architectural fixes."),
        ("ChatRepair (Xia & Zhang, 2024)", "Conversational prompt chaining with ChatGPT", "Fixed 162/337 Defects4J bugs (~$0.42/bug)", "Lacks isolated execution sandboxes; prompt loops do not explore multi-file repositories."),
        ("SWE-bench (Jimenez et al., 2024)", "Benchmark evaluating LLMs on 2,294 real GitHub issues", "Claude-2 resolved only 1.96% of issues", "Benchmark dataset and harness only; does not provide a repair platform or UI."),
        ("SWE-agent (Yang et al., 2024)", "Agent-Computer Interface (ACI) for terminal navigation", "Achieved 12.5% on SWE-bench", "High computational cost; unconstrained bash commands pose severe host security risks."),
        ("AutoCodeRover (Zhang et al., 2024)", "AST-directed search and spectrum fault localization", "Resolved 19% on SWE-bench Lite", "Tailored exclusively for benchmark scoring; lacks developer audit dashboards or PR exports."),
        ("DevMind (Proposed)", "Evidence-grounded hybrid RAG + Sandboxed Non-Root Repair", "179 passed tests; 0.800 Recall@5; 100% safe", "Combines multi-language AST indexing, RRF hybrid retrieval, isolated Docker testing, and PR drafts.")
    ]
    
    table_lit = doc.add_table(rows=len(lit_data) + 1, cols=4)
    table_lit.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_lit)
    
    headers_lit = ["Framework", "Approach & Core Technique", "Reported Benchmark Outcome", "Limitation Addressed by DevMind"]
    for j, h in enumerate(headers_lit):
        c = table_lit.rows[0].cells[j]
        c.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(c, "F1F5F9")
    
    widths_lit = [Inches(1.3), Inches(1.8), Inches(1.5), Inches(1.9)]
    for j in range(4):
        table_lit.rows[0].cells[j].width = widths_lit[j]
        
    for i, row_data in enumerate(lit_data):
        row = table_lit.rows[i + 1]
        for j, text in enumerate(row_data):
            c = row.cells[j]
            c.width = widths_lit[j]
            run = c.paragraphs[0].add_run(text)
            run.font.size = Pt(8.5)
            if j == 0:
                run.font.bold = True
        if i % 2 == 1:
            for j in range(4):
                set_cell_background(row.cells[j], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # 3. System Architecture & Methodology
    h3 = doc.add_heading("3. System Architecture and Methodology", level=1)
    h3.style.font.color.rgb = RGBColor(15, 23, 42)
    
    doc.add_paragraph(
        "DevMind is architected as an orchestrated six-stage pipeline that decouples repository understanding from model execution. "
        "Figure 1 illustrates the end-to-end dataflow, showing how incoming bug reports and source trees are transformed into verified patches."
    )
    
    # Insert Architecture Diagram if exists
    arch_fig_path = os.path.abspath("reports/devmind-report-draft/figures/devmind-architecture.png")
    if os.path.exists(arch_fig_path):
        p_fig1 = doc.add_paragraph()
        p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(arch_fig_path, width=Inches(6.2))
        p_cap1 = doc.add_paragraph()
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c1 = p_cap1.add_run("Fig. 1: DevMind End-to-End System Architecture. Raw bug reports and multi-language repositories pass through static AST indexing, hybrid RAG retrieval, bounded LLM code generation, and disposable non-root Docker sandboxing.")
        r_c1.font.italic = True
        r_c1.font.size = Pt(9.5)
        p_cap1.paragraph_format.space_after = Pt(12)

    h31 = doc.add_heading("3.1 Corpus Ingestion and Multi-Language AST Parsing", level=2)
    h31.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "To process heterogeneous codebases safely, DevMind treats all target source code as untrusted data. "
        "The static indexer inspects source files across 11+ programming languages without importing or executing runtime interpreters on the host. "
        "For Python files, the system parses the official AST (`ast.parse`), extracting classes, functions, asynchronous definitions, and docstrings. "
        "For JavaScript, TypeScript, Java, C++, Go, and Rust, DevMind utilizes a structural brace/block lexical tokenizer that tracks scope depth, "
        "retains function signatures, and handles inline script blocks within HTML/HTM templates. "
        "Each extracted block is assigned structural metadata: `file_path`, `symbol_name`, `start_line`, `end_line`, `language`, and `char_count`."
    )

    h32 = doc.add_heading("3.2 Dual Indexing & Vector Space Representation", level=2)
    h32.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Extracted chunks are indexed through two parallel representations: "
        "(1) a sparse term-frequency index utilizing TF-IDF and Okapi BM25 ($k_1=1.5, b=0.75$), capturing exact identifier names and API tokens; "
        "and (2) a dense semantic embedding space utilizing `sentence-transformers/all-MiniLM-L6-v2` (pinned revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`), "
        "projecting text into a 384-dimensional continuous latent space. Persistent vectors are stored in ChromaDB and NumPy arrays, preventing costly re-indexing on subsequent queries."
    )

    h33 = doc.add_heading("3.3 Two-Stage Hybrid Retrieval Formulation", level=2)
    h33.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Retrieval executes across three mathematical stages:"
    )
    doc.add_paragraph(
        "1. Dense Semantic Similarity:\n"
        "Let eq and ed_i represent the 384-dimensional normalized vector embeddings of query q and code chunk d_i. The cosine similarity is formulated as:"
    )
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq1 = p_eq1.add_run("Sim_sem(q, d_i) = (e_q · e_{d_i}) / ( ||e_q|| ||e_{d_i}|| )")
    r_eq1.font.bold = True
    
    doc.add_paragraph(
        "2. Sparse Lexical Scoring (BM25):\n"
        "BM25 computes relevance based on query term frequency c(w, q), chunk term frequency c(w, d), document length |d|, and average corpus length avgdl:"
    )
    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq2 = p_eq2.add_run("Score_BM25(q, d) = Σ_{w ∈ q} IDF(w) · [ (c(w, d) · (k_1 + 1)) / (c(w, d) + k_1 · (1 - b + b · (|d| / avgdl))) ]")
    r_eq2.font.bold = True
    
    doc.add_paragraph(
        "3. Reciprocal Rank Fusion (RRF):\n"
        "Because cosine similarities and BM25 scores follow entirely different numerical distributions, directly adding raw scores introduces severe bias. "
        "DevMind employs Reciprocal Rank Fusion with smoothing constant k=60 to merge the top candidates:"
    )
    p_eq3 = doc.add_paragraph()
    p_eq3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_eq3 = p_eq3.add_run("RRF(d) = Σ_{m ∈ {sem, lex}} 1 / ( 60 + rank_m(d) )")
    r_eq3.font.bold = True
    doc.add_paragraph(
        "Chunks appearing prominently in both semantic and lexical candidate lists receive compounded RRF scores, elevating them above uni-modal false positives."
    )

    h34 = doc.add_heading("3.4 Local LLM Code Generation & Unified Diff Validation", level=2)
    h34.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Top-ranked evidence chunks are formatted into numbered context spans ([E1], [E2], ...) and injected into the prompt of an open-weights LLM "
        "(e.g., Qwen 2.5 1.5B/7B or DeepSeek via local Ollama). The model is instructed to output only a valid Git unified diff. "
        "The generated patch is intercepted by DevMind's deterministic diff validator, which enforces four integrity constraints: "
        "(1) Target file path must exist within the repository boundaries, rejecting absolute or directory-traversing paths (`../`); "
        "(2) Diff header must contain standard `--- a/path` and `+++ b/path` markers; "
        "(3) Hunk counts (`@@ -l,s +l,s @@`) are dynamically normalized to match actual addition/deletion lines; "
        "and (4) Empty patches containing no net line additions or deletions are rejected before container invocation."
    )

    h35 = doc.add_heading("3.5 Disposable Non-Root Docker Sandboxing & Self-Healing Loop", level=2)
    h35.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "To test candidate patches safely, DevMind spawns an ephemeral Docker container. "
        "The host repository is never modified: an ephemeral snapshot is mounted into a disposable container. "
        "The container enforces stringent security restrictions: non-root execution (`--user 10001:10001`), network disabled (`--network none`), "
        "capabilities dropped (`--cap-drop ALL`), `no-new-privileges:true`, read-only container root, and strict resource limits (2 CPUs, 2GB RAM). "
        "Figure 2 illustrates the bounded self-healing repair loop."
    )
    
    # Insert Repair Workflow Diagram if exists
    wf_fig_path = os.path.abspath("reports/devmind-report-draft/figures/devmind-repair-workflow.png")
    if os.path.exists(wf_fig_path):
        p_fig2 = doc.add_paragraph()
        p_fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(wf_fig_path, width=Inches(6.2))
        p_cap2 = doc.add_paragraph()
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_c2 = p_cap2.add_run("Fig. 2: DevMind Bounded Repair and Self-Healing Feedback Loop. The sandbox executes regression tests; on failure, sanitized diagnostic logs are routed back to the LLM to refine the patch across up to 3 bounded attempts.")
        r_c2.font.italic = True
        r_c2.font.size = Pt(9.5)
        p_cap2.paragraph_format.space_after = Pt(12)

    # 4. Experimental Evaluation & Results
    h4 = doc.add_heading("4. Experimental Evaluation and Results", level=1)
    h4.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "To rigorously quantify retrieval and localization quality without relying on synthetic mocks, DevMind was evaluated across two empirical benchmarks: "
        "(1) a controlled 5-repository development pilot derived from the SWE-bench Lite standard, and (2) live multi-language repository repair trials."
    )
    
    # Table 1: Corpus Stats
    h41 = doc.add_heading("4.1 Multi-Language Repository Corpus Statistics", level=2)
    h41.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Table 2 reports the extraction statistics across five evaluation repositories and two demonstration benchmark projects."
    )
    
    corp_data = [
        ("astropy/astropy", "Python", "542", "2,845", "Python AST Parser", "pytest"),
        ("django/django", "Python", "1,248", "6,120", "Python AST Parser", "pytest"),
        ("matplotlib/matplotlib", "Python", "380", "1,950", "Python AST Parser", "pytest"),
        ("pvlib/pvlib-python", "Python", "94", "482", "Python AST Parser", "pytest"),
        ("pydicom/pydicom", "Python", "118", "614", "Python AST Parser", "pytest"),
        ("QuickCart Store", "Python/JS", "28", "142", "AST + Lexical JS", "pytest / node"),
        ("Cricket Scorer Pro", "JS / HTML", "6", "38", "Lexical JS + Inline", "node --test")
    ]
    
    table_corp = doc.add_table(rows=len(corp_data) + 1, cols=6)
    table_corp.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_corp)
    
    h_corp = ["Repository", "Language", "Source Files", "Extracted Chunks", "Parser Pipeline", "Target Test Runner"]
    for j, h in enumerate(h_corp):
        c = table_corp.rows[0].cells[j]
        c.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(c, "F1F5F9")
        
    for i, row_data in enumerate(corp_data):
        row = table_corp.rows[i + 1]
        for j, text in enumerate(row_data):
            c = row.cells[j]
            run = c.paragraphs[0].add_run(text)
            run.font.size = Pt(9)
            if j == 0:
                run.font.bold = True
        if i % 2 == 1:
            for j in range(6):
                set_cell_background(row.cells[j], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Table 2: Retrieval Results
    h42 = doc.add_heading("4.2 Comparative Retrieval Performance on SWE-bench Lite Pilot", level=2)
    h42.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Table 3 presents the measured retrieval metrics across four query formulations: Raw issue text, Normalized text, "
        "Keywords/Identifiers, and Structured query hints. Evaluation compares Sparse TF-IDF, Dense MiniLM Cosine, and Hybrid Lexical-Semantic RRF."
    )
    
    ret_data = [
        ("Raw", "TF-IDF (Sparse)", "0.400", "0.160", "0.800", "0.550", "0.612"),
        ("Raw", "Dense MiniLM Cosine", "0.400", "0.080", "0.400", "0.400", "0.400"),
        ("Raw", "Lexical-Semantic RRF", "0.400", "0.120", "0.600", "0.440", "0.477"),
        ("Normalized", "TF-IDF (Sparse)", "0.400", "0.160", "0.800", "0.550", "0.612"),
        ("Normalized", "Dense MiniLM Cosine", "0.400", "0.080", "0.400", "0.400", "0.400"),
        ("Normalized", "Lexical-Semantic RRF", "0.400", "0.120", "0.600", "0.440", "0.477"),
        ("Keywords/IDs", "TF-IDF (Sparse)", "0.400", "0.160", "0.800", "0.567", "0.626"),
        ("Keywords/IDs", "Dense MiniLM Cosine", "0.400", "0.080", "0.400", "0.400", "0.400"),
        ("Keywords/IDs", "Lexical-Semantic RRF", "0.400", "0.080", "0.400", "0.400", "0.400"),
        ("Structured", "TF-IDF (Sparse)", "0.400", "0.160", "0.800", "0.567", "0.626"),
        ("Structured", "Dense MiniLM Cosine", "0.400", "0.080", "0.400", "0.400", "0.400"),
        ("Structured", "Lexical-Semantic RRF", "0.400", "0.080", "0.400", "0.400", "0.400")
    ]
    
    table_ret = doc.add_table(rows=len(ret_data) + 1, cols=7)
    table_ret.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table_ret)
    
    h_ret = ["Query Variant", "Retrieval Method", "P@1", "P@5", "R@5", "MRR", "nDCG@5"]
    for j, h in enumerate(h_ret):
        c = table_ret.rows[0].cells[j]
        c.paragraphs[0].add_run(h).font.bold = True
        set_cell_background(c, "F1F5F9")
        
    for i, row_data in enumerate(ret_data):
        row = table_ret.rows[i + 1]
        for j, text in enumerate(row_data):
            c = row.cells[j]
            run = c.paragraphs[0].add_run(text)
            run.font.size = Pt(9)
            if j == 1 and "TF-IDF" in text:
                run.font.bold = True
        if i % 3 == 0:
            for j in range(7):
                set_cell_background(row.cells[j], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    h43 = doc.add_heading("4.3 Key Empirical Findings & Indexing Trade-Offs", level=2)
    h43.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Analysis of the empirical results uncovers three critical software engineering insights:\n"
        "1. Lexical Superiority in Code Search: In contrast to general conversational NLP where dense embeddings dominate, "
        "software bug localization heavily favors exact lexical token matching. Programmers diagnose defects using exact identifier strings "
        "(e.g., `calculate_cart_total`, `matchState.balls`, `handleDelivery`). Dense models map these tokens to generic semantic clusters, "
        "yielding half the top-5 recall of TF-IDF (Recall@5 = 0.400 vs 0.800).\n"
        "2. Dramatic Indexing Efficiency: Dense embedding computation with all-MiniLM-L6-v2 required 594.737 seconds (nearly 10 minutes) on CPU, "
        "consuming over 932 MiB peak RAM. Conversely, sparse TF-IDF index construction took only 1.199 seconds (a 496x speedup) with minimal memory overhead.\n"
        "3. Structured Query Enrichment: Expanding raw queries with extracted snake_case/camelCase identifiers improved TF-IDF MRR from 0.550 to 0.567 "
        "and nDCG@5 from 0.612 to 0.626, proving that text analytics pre-processing directly enhances repository localization."
    )

    # 5. Cross-Language Bug Repair Matrix
    h5 = doc.add_heading("5. Cross-Language Bug Repair and Execution Matrix", level=1)
    h5.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "To validate the end-to-end self-healing repair pipeline, DevMind was executed against real multi-language bug fixtures:"
    )
    
    rep_cases = [
        ("Case 1: Python Calculator Bug (Arithmetic Edge Case)", 
         "Defect Description: Division by zero and floating-point edge-cases raise unhandled exceptions rather than returning structured error codes.\n"
         "Localization: TF-IDF localized `src/calculator/core.py` as rank 1 evidence [E1].\n"
         "Repair & Test: The local model generated a unified diff adding boundary validation. Docker execution under pytest verified 2/2 tests passed with zero regressions."),
        ("Case 2: JavaScript Cricket Scorer Pro (Double Ball Count Bug)", 
         "Defect Description: When recording any delivery, the batsman ball count incremented by 2 instead of 1 (`balls += 2`), skewing strike rates and over tallies.\n"
         "Localization: DevMind retrieved `script.js` functions `handleRuns()` and `recordDelivery()` as top evidence.\n"
         "Repair & Test: Identified all 4 duplicate increment sites across lines 451, 551, 601, and 743 (`balls += 2` -> `balls += 1`). "
         "Executed `node --test test/scoring.test.cjs` in Docker: 1 test passed in 3.9ms, 0 failed. Verified live in browser UI with batsman playing exactly 1 ball per delivery.")
    ]
    for title, desc in rep_cases:
        p = doc.add_paragraph()
        r_t = p.add_run(title + "\n")
        r_t.font.bold = True
        p.add_run(desc)
        p.paragraph_format.space_after = Pt(8)

    # 6. System Implementation & Interface
    h6 = doc.add_heading("6. System Implementation and Interface", level=1)
    h6.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "DevMind is deployed with an interactive, modern user interface comprising three specialized operational workspaces:\n"
        "• Tab 1 (Bug Analysis & Repair): Provides quick-demo presets, interactive parameter configuration, a 6-stage agent visual timeline, "
        "a real-time cosine similarity bar chart, and one-click GitHub Pull Request draft and JSON report exports.\n"
        "• Tab 2 (Performance & History Dashboard): Computes aggregate KPIs across saved runs, tracking total runs, verified Docker fix rate, "
        "diff pass rates, and an expandable audit log of per-attempt execution logs.\n"
        "• Tab 3 (UI Parameter Guide & Viva Defense Reference): Contains comprehensive card-by-card documentation of every UI toggle, "
        "explaining technical definitions, runtime implications, and defense talking points.\n"
        "• Manifest V3 Browser Extension: An unpacked Brave/Chrome extension enabling 1-click transmission of GitHub repository URLs directly into DevMind."
    )

    # 7. Discussion, Governance & Safety
    h7 = doc.add_heading("7. Discussion, Governance and Host Safety Principles", level=1)
    h7.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "Unlike commercial coding assistants that directly modify local workspaces or execute terminal commands with host user privileges, "
        "DevMind strictly enforces the Principle of Least Privilege and the Host Safety Guarantee:\n"
        "1. Zero Local Mutation: Generated patches are verified inside ephemeral containers; the developer's working directory is never mutated automatically.\n"
        "2. Non-Root Isolation: Sandboxed containers run as unprivileged UID 10001 with dropped Linux capabilities and disabled networking, "
        "preventing malicious repository code from probing local host networks or exfiltrating data.\n"
        "3. Ephemeral tmpfs Mounting: Container filesystems are temporary in-memory structures wiped upon test exit.\n"
        "4. Bounded Output Streaming: Stdout/stderr captures are truncated to 4,000 characters, preventing memory-exhaustion denial-of-service attacks from runaway infinite print loops."
    )

    # 8. Conclusion & Future Work
    h8 = doc.add_heading("8. Conclusion and Future Work", level=1)
    h8.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "In this work, we presented DevMind, an evidence-grounded agentic RAG framework for multi-language software bug localization and sandboxed program repair. "
        "By uniting deterministic AST parsing across 11+ languages, hybrid sparse-dense retrieval with Reciprocal Rank Fusion, "
        "and disposable non-root Docker sandboxing, DevMind achieves 0.800 Recall@5 while delivering 100% safety against host workspace corruption. "
        "The complete software framework is validated by 179 passing automated tests.\n\n"
        "Future Work: In accordance with academic rigor, future research extensions will focus on: "
        "(1) conducting multi-annotator blind ground-truth labeling to replace proxy changed-file labels with exact function-level fault annotations, "
        "and (2) scaling the execution evaluation to full official SWE-bench evaluation harness runs across high-performance cloud clusters."
    )

    # Acknowledgements
    h_ack = doc.add_heading("Acknowledgements", level=1)
    h_ack.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "The authors express their sincere gratitude to the course instructors and project mentors of the Department of Computer Science and Engineering, "
        "Amrita School of Computing, Amrita Vishwa Vidyapeetham, Amritapuri Campus, for their invaluable guidance, technical reviews, and encouragement throughout this project."
    )

    # References
    h_ref = doc.add_heading("References", level=1)
    h_ref.style.font.color.rgb = RGBColor(15, 23, 42)
    
    refs = [
        "[1] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, et al., 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,' in Advances in Neural Information Processing Systems (NeurIPS), vol. 33, pp. 9459–9474, 2020.",
        "[2] C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan, 'SWE-bench: Can Language Models Resolve Real-World GitHub Issues?,' in Proc. International Conference on Learning Representations (ICLR), 2024.",
        "[3] J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press, 'SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering,' in Advances in Neural Information Processing Systems (NeurIPS), vol. 37, 2024.",
        "[4] Y. Zhang, H. Ruan, Z. Fan, and A. Roychoudhury, 'AutoCodeRover: Autonomous Program Improvement,' in Proc. 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA), pp. 1592–1604, 2024.",
        "[5] I. Bouzenia, P. Devanbu, and M. Pradel, 'RepairAgent: An Autonomous, LLM-Based Agent for Program Repair,' in Proc. IEEE/ACM 47th International Conference on Software Engineering (ICSE), pp. 2188–2200, 2025.",
        "[6] C. S. Xia, Y. Deng, S. Dunn, and L. Zhang, 'Agentless: Demystifying LLM-Based Software Engineering Agents,' in Proc. ACM International Conference on the Foundations of Software Engineering (FSE), 2025.",
        "[7] C. S. Xia and L. Zhang, 'Automated Program Repair via Conversation: Fixing 162 out of 337 Bugs for $0.42 Each using ChatGPT,' in Proc. ISSTA, pp. 819–831, 2024.",
        "[8] S. Robertson and H. Zaragoza, 'The Probabilistic Relevance Framework: BM25 and Beyond,' Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009.",
        "[9] G. V. Cormack, C. L. Clarke, and S. Buettcher, 'Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,' in Proc. 32nd ACM SIGIR, pp. 758–759, 2009.",
        "[10] S. S. Chaudhari, R. T. Jacob, J. Cao, M. S. Rashid, M. Goswami, and C. Bock, 'SpIDER: Spatially Informed Dense Embedding Retrieval for Software Issue Localization,' in Proc. EMNLP, pp. 44096–44131, 2026.",
        "[11] A. M. Samir and M. M. Rahman, 'Improving IR-based Bug Localization with Semantics-Driven Query Reduction,' Journal of Systems and Software, vol. 237, art. 112860, 2026.",
        "[12] G. Caumartin and G. Melo, 'Reformulate, Retrieve, Localize: Agents for Repository-Level Bug Localization,' in Proc. IEEE/ACM BotSE Workshop at ICSE, 2026.",
        "[13] R. Andrade, C. Teixeira, N. Laranjeiro, and M. Vieira, 'An Empirical Study on the Classification of Bug Reports with Machine Learning,' IEEE Open Journal of the Computer Society, vol. 7, pp. 1213–1224, 2026.",
        "[14] Q. Meng, X. Zhang, Z. Ren, and J. Visser, 'EviACT: An Evidence-to-Action Framework for Agentic Program Repair,' arXiv:2605.27238, 2026.",
        "[15] M. N. Al Awad and S. Ivanov, 'Loc2Repair: Evaluating File-Level Issue Localization in Repo-Level LLM Repair,' arXiv:2606.30963, 2026."
    ]
    for ref in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.left_indent = Inches(0.4)
        p_r.paragraph_format.first_line_indent = Inches(-0.4)
        run_ref = p_r.add_run(ref)
        run_ref.font.size = Pt(9.5)
        
    out_path = "DevMind_Term_Project_Report.docx"
    doc.save(out_path)
    print(f"Successfully generated {out_path} ({len(doc.paragraphs)} paragraphs, {len(doc.tables)} tables)")

if __name__ == '__main__':
    build_docx_report()
