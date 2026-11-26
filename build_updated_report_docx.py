"""
Builds the complete DevMind_Term_Project_Report.docx using the user-provided
academic report text and embedding all 7 generated publication-quality figures.
"""
import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

FIG_DIR = Path("reports/devmind-report-draft/figures")

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

def set_table_borders(table, color="B0BEC5"):
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    for border_name in ['top', 'bottom', 'insideH']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '6')
        border.set(qn('w:space'), '0')
        border.set(qn('w:color'), color)
        tblBorders.append(border)
    for no_border in ['left', 'right', 'insideV']:
        b = OxmlElement(f'w:{no_border}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
    tblPr.append(tblBorders)

def add_caption_above(doc, caption_text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(caption_text)
    run.font.name = 'Times New Roman'
    run.font.size = Pt(9.5)
    run.font.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)

def add_figure_with_caption(doc, fig_filename, caption_text):
    fig_path = FIG_DIR / fig_filename
    if fig_path.exists():
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(str(fig_path), width=Inches(6.3))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(12)
        run_cap = p_cap.add_run(caption_text)
        run_cap.font.name = 'Times New Roman'
        run_cap.font.size = Pt(9.0)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(71, 85, 105)

def build_report():
    doc = docx.Document()
    
    # Page Margins (Procedia Computer Science ~ 20mm/25mm)
    for section in doc.sections:
        section.top_margin = Inches(0.9)
        section.bottom_margin = Inches(0.9)
        section.left_margin = Inches(0.9)
        section.right_margin = Inches(0.9)
        
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = RGBColor(15, 23, 42)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(5)

    # Document Header / Pre-title
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_hdr = p_header.add_run("International Conference on Machine Learning & Data Engineering (ICMLDE)\nProcedia Computer Science (Elsevier)  ·  Amrita Vishwa Vidyapeetham\nText Analytics (22CSE314) Semester V Project Report")
    r_hdr.font.name = 'Times New Roman'
    r_hdr.font.size = Pt(9.5)
    r_hdr.font.bold = True
    r_hdr.font.color.rgb = RGBColor(100, 116, 139)
    p_header.paragraph_format.space_after = Pt(12)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("DevMind: An Evidence-Grounded Text Analytics Framework for Explainable Bug Localization and Sandboxed Code Repair")
    r_title.font.name = 'Times New Roman'
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(15, 23, 42)
    p_title.paragraph_format.space_after = Pt(8)

    # Authors
    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_auth = p_auth.add_run("P. Sharath Chandhraᵃ, B. Shashank Manoharᵃ, K. Venkat Sai Mani Avinashᵃ*\n")
    r_auth.font.name = 'Times New Roman'
    r_auth.font.size = Pt(11)
    r_auth.font.bold = True
    r_aff = p_auth.add_run("ᵃDepartment of Computer Science and Engineering, Amrita School of Computing, Amrita Vishwa Vidyapeetham, Amritapuri, India\n*Corresponding Author: [institutional e-mail to be confirmed before final submission]")
    r_aff.font.name = 'Times New Roman'
    r_aff.font.size = Pt(9.5)
    r_aff.font.italic = True
    r_aff.font.color.rgb = RGBColor(100, 116, 139)
    p_auth.paragraph_format.space_after = Pt(12)

    # Abstract Callout Box
    table_abs = doc.add_table(rows=1, cols=1)
    table_abs.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_abs = table_abs.rows[0].cells[0]
    set_cell_background(cell_abs, "F8FAFC")
    set_cell_margins(cell_abs, top=120, bottom=120, left=180, right=180)
    
    p_abs = cell_abs.paragraphs[0]
    r_atitle = p_abs.add_run("Abstract—")
    r_atitle.font.bold = True
    r_atitle.font.size = Pt(9.5)
    r_abody = p_abs.add_run(
        "Software maintenance often begins with a description of what went wrong, rather than a clear indication of where the defect lies. "
        "DevMind was developed to examine how such reports can be connected to source code in a way that developers can inspect and test. "
        "The framework combines rule-based text analysis, static code indexing, retrieval, guarded patch handling and isolated test execution. "
        "Its issue analyzer normalizes text, separates compound identifiers, removes selected conversational terms, ranks informative words, extracts component hints and assigns a provisional issue category. "
        "For indexing, Python files are parsed with the language's abstract syntax tree facilities; other supported languages are handled through lexical scope extraction. "
        "Retrieval was studied on five pinned SWE-bench Lite development instances, using four versions of each issue query and five retrieval strategies. "
        "In this small file-level pilot, TF-IDF reached a mean Recall@5 of 0.800, compared with 0.400 for dense cosine retrieval. "
        "Combining TF-IDF and BM25 with rank fusion gave P@1 = 0.600, MRR = 0.667 and nDCG@5 = 0.700. "
        "Adding identifiers to the query made a small improvement to TF-IDF MRR, from 0.550 to 0.567. "
        "TF-IDF indexing took 1.199 s; dense index construction took 594.737 s and recorded a sampled peak process-tree memory of 932.89 MiB. "
        "The Python test suite reported 179 passes and three environment-dependent skips. "
        "A live Qwen response was rejected before execution, while separate controlled patch fixtures passed their targeted sandbox tests. "
        "The present evidence therefore supports the retrieval and sandbox components, but not reliable end-to-end LLM repair."
    )
    r_abody.font.size = Pt(9.5)
    
    p_kw = cell_abs.add_paragraph()
    r_kt = p_kw.add_run("Keywords: ")
    r_kt.font.bold = True
    r_kt.font.size = Pt(9.0)
    r_kv = p_kw.add_run("Software Bug Localization; Text Analytics; Repository Retrieval; Retrieval-Augmented Generation; Automated Program Repair; Sandboxed Verification.")
    r_kv.font.size = Pt(9.0)
    r_kv.font.italic = True
    
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Nomenclature Box
    add_caption_above(doc, "Nomenclature")
    nom_data = [
        ("APR", "Automated Program Repair", "AST", "Abstract Syntax Tree"),
        ("BM25", "Best Matching 25 ranking function", "Docker", "Container platform for isolated execution"),
        ("LLM", "Large Language Model", "MRR", "Mean Reciprocal Rank"),
        ("nDCG@5", "Normalized Discounted Cumulative Gain at rank 5", "NLP", "Natural Language Processing"),
        ("P@K", "Precision among top K retrieved items", "RAG", "Retrieval-Augmented Generation"),
        ("RRF", "Reciprocal Rank Fusion", "RSS", "Resident Set Size"),
        ("SWE-bench", "Benchmark of real GitHub software issues", "TF-IDF", "Term Frequency–Inverse Document Frequency"),
        ("UID", "User Identifier", "RQ", "Research Question")
    ]
    t_nom = doc.add_table(rows=len(nom_data) + 1, cols=4)
    t_nom.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t_nom)
    
    t_nom.rows[0].cells[0].paragraphs[0].add_run("Term").font.bold = True
    t_nom.rows[0].cells[1].paragraphs[0].add_run("Definition").font.bold = True
    t_nom.rows[0].cells[2].paragraphs[0].add_run("Term").font.bold = True
    t_nom.rows[0].cells[3].paragraphs[0].add_run("Definition").font.bold = True
    for j in range(4):
        set_cell_background(t_nom.rows[0].cells[j], "F1F5F9")
        t_nom.rows[0].cells[j].paragraphs[0].runs[0].font.size = Pt(9.0)
        
    for i, row in enumerate(nom_data):
        r = t_nom.rows[i + 1]
        for c_idx in range(4):
            r.cells[c_idx].paragraphs[0].add_run(row[c_idx]).font.size = Pt(8.5)
            if c_idx in [0, 2]:
                r.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        if i % 2 == 1:
            for c_idx in range(4):
                set_cell_background(r.cells[c_idx], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    # 1. Introduction
    h1 = doc.add_heading("1. Introduction", level=1)
    h1.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "A developer usually encounters a defect through a report of an observable symptom: a value is wrong, a page behaves unexpectedly, "
        "or an operation fails after a particular sequence of actions. The source of that behaviour may be several layers away from the place where the symptom appears. "
        "In a repository, behaviour is distributed across functions, classes, identifiers, data structures and their interactions. "
        "A useful debugging workflow must therefore do more than find words that resemble the report. It needs to extract the report's technical clues, "
        "narrow the search to plausible code, preserve the evidence used to reach that decision and test any proposed change. "
        "Repository-level benchmarks show why this is difficult: resolving an issue can involve several files and feedback from project tests, "
        "not simply editing the first matching function [2]."
    )
    doc.add_paragraph(
        "Earlier work on bug reports has explored text cleaning, token representation and automatic categorization. "
        "More recent studies have used language models to reformulate issue descriptions or guide the search for relevant code [8–12]. "
        "Research on automated repair has also moved toward repository-aware workflows. SWE-agent, AutoCodeRover, RepairAgent and Agentless, for example, "
        "differ in how they navigate code, use program structure, select repair locations and incorporate test feedback [3–6]. "
        "Taken together, these studies suggest that a proposed edit should be judged as part of a traceable process: "
        "generating a plausible patch is only one step, and it does not by itself show that the defect has been resolved."
    )
    doc.add_paragraph(
        "This study presents DevMind as a local-first implementation of that workflow. It first converts an issue report into a set of structured text features, "
        "then indexes source code and retrieves candidate code units using lexical and semantic methods. Where a model provider is configured, "
        "an orchestration stage can request a patch using the retrieved evidence. The proposed diff is checked for structural validity and repository-boundary violations "
        "before any test command is run. Accepted candidates are tested in a disposable, non-root Docker environment, and the run outcome is retained with its supporting evidence. "
        "The paper's contribution is deliberately limited to the implemented system and an exploratory comparison of query formulations and retrieval methods; "
        "it does not claim a leading result on an established automated-repair leaderboard."
    )

    # 1.1 Problem formulation
    h11 = doc.add_heading("1.1. Problem formulation", level=2)
    h11.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Let q represent a bug report written in natural language, and let R = {f₁, f₂, …, fₙ} represent a fixed snapshot of the repository being examined. "
        "The task analyzer transforms q into a structured representation q*. The retriever then ranks candidate code units C = {c₁, …, cₖ} drawn from R. "
        "If a model is available, it may use the selected evidence to suggest a patch P. That patch must first pass checks on diff structure and file-path boundaries. "
        "Only then can the candidate be applied to a disposable copy and evaluated with the repository's tests. DevMind records the evidence and each verification outcome separately. "
        "A passing targeted test is useful evidence, but it cannot establish complete semantic correctness or replace review by a developer."
    )

    # 1.2 Objectives and research questions
    h12 = doc.add_heading("1.2. Objectives and research questions", level=2)
    h12.style.font.color.rgb = RGBColor(30, 41, 59)
    objs = [
        "Build a deterministic issue-analysis stage that cleans natural-language reports, extracts useful terms and identifiers, and assigns rule-based issue categories.",
        "Create a static index of repository code using Python AST parsing and lexical extraction for additional languages, without running the target code during ingestion.",
        "Measure how TF-IDF, BM25, dense embeddings and rank-fusion variants perform under consistent issue-query conditions.",
        "Check candidate unified diffs for malformed syntax, empty edits and paths that escape the repository before allowing execution.",
        "Run candidate tests in disposable Docker containers configured with a non-root user, restricted capabilities and bounded output.",
        "Make retrieved evidence, validation decisions and test outcomes inspectable through the application and its generated reports."
    ]
    for ob in objs:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.add_run(ob)

    doc.add_paragraph(
        "The experiments address three questions. RQ1 asks whether deterministic transformations of an issue report change file-level retrieval rankings in the available pilot. "
        "RQ2 compares sparse, dense and fused retrieval in ranking quality and indexing cost. "
        "RQ3 examines what the patch-validation and isolated-execution evidence can establish, while identifying the parts of live LLM repair that remain unverified."
    )

    # 2. Related Work
    h2 = doc.add_heading("2. Related Work", level=1)
    h2.style.font.color.rgb = RGBColor(15, 23, 42)
    
    h21 = doc.add_heading("2.1. Bug-report analysis and query formulation", level=2)
    h21.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Bug-report analysis has a substantial research history. Long and colleagues reviewed machine-learning approaches to understanding and extracting information "
        "from software reports, documenting the use of preprocessing and text representations alongside limitations in evaluation practice [8]. "
        "A large 2026 study of more than 660,000 issue reports found that classification outcomes vary with factors such as project language and the issue-tracking environment [12]. "
        "These findings support careful treatment of report content, but they also caution against assuming that a single preprocessing recipe will work equally well across projects."
    )
    doc.add_paragraph(
        "Query formulation is also being studied directly in bug localization. BRaIn uses language-model feedback to revise a query and rerank source documents [9]. "
        "Caumartin and Melo examine an agent that extracts identifiers and code cues from a report before carrying out BM25 retrieval [10]. "
        "IQLoc similarly uses semantic reasoning to reduce and reformulate queries for information-retrieval-based localization [11]. "
        "These approaches make it clear that query reformulation is not an unexplored problem. DevMind instead evaluates a simpler, deterministic set of query transformations "
        "and measures their effect in a small, controlled repository pilot."
    )

    h22 = doc.add_heading("2.2. Retrieval and repository structure", level=2)
    h22.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Retrieval-augmented generation gives a language model access to information retrieved for a particular task, rather than relying only on knowledge held in its parameters [1]. "
        "In code search, exact identifiers can be especially informative. BM25 accounts for term frequency and document length [17], while Reciprocal Rank Fusion (RRF) "
        "combines ranked lists without requiring their original scores to be directly comparable [18]. Dense embeddings offer another way to connect related descriptions, "
        "although semantic proximity alone does not represent the structure of a codebase. SpIDER, presented at EMNLP 2026, adds graph-based exploration to dense retrieval "
        "and reports gains on its own multilingual benchmark [13]. This work is a reminder that representation, repository structure and evaluation data all affect retrieval results; "
        "the small DevMind pilot should not be read as a general verdict against dense methods."
    )

    h23 = doc.add_heading("2.3. Repository-level repair and validation", level=2)
    h23.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "SWE-bench introduced a repository-level evaluation task built from real GitHub issues and their associated fixes [2]. "
        "SWE-agent studies how an agent-computer interface affects repository navigation and test execution [3]. "
        "AutoCodeRover uses program-structure information, including AST-based search, to guide localization [4]. "
        "RepairAgent gives a language model tools for carrying out repair actions [6], while Agentless breaks the workflow into localization, repair and validation stages "
        "without requiring the model to plan every tool action [5]. ChatRepair explores iterative repair through conversation and test feedback [7]. "
        "Recent work continues to examine evidence and localization as distinct parts of the problem: EviACT uses evidence-oriented gates during repair [14], "
        "Loc2Repair studies how file-level localization affects downstream repair [15], and RepoAI investigates multi-agent RAG for repository-level refactoring [16]. "
        "DevMind is related to this body of work, but its experiments address a smaller question about deterministic issue features, retrieval choices and sandbox controls."
    )

    # Table 1
    add_caption_above(doc, "Table 1. Representative research relevant to DevMind (the listed results belong to the cited studies, not to the DevMind experiments).")
    rel_work = [
        ("SWE-bench [2]", "Real GitHub issue-to-patch benchmark", "Provides the benchmark family from which the five development instances were drawn."),
        ("SWE-agent [3]", "Agent-computer interface for repository navigation and tests", "Motivates tool-mediated repository inspection."),
        ("AutoCodeRover [4]", "AST-aware code search and fault localization", "Shows the value of program-structure-aware localization."),
        ("Agentless [5]", "Staged localization, repair and validation", "Supports bounded, explicit pipeline stages."),
        ("BRaIn / IQLoc [9,11]", "LLM-guided relevance feedback and query reformulation", "Demonstrates that query formulation is already an active research direction."),
        ("SpIDER [13]", "Dense retrieval with repository-graph exploration", "Highlights structural context beyond flat retrieval."),
        ("EviACT / Loc2Repair [14,15]", "Evidence gates and controlled localization analysis", "Motivates separating evidence, patch validity and repair outcomes."),
        ("RepoAI [16]", "Multi-agent RAG for repository refactoring", "Adjacent work on multi-agent repository-level workflows.")
    ]
    t1 = doc.add_table(rows=len(rel_work) + 1, cols=3)
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    
    t1.rows[0].cells[0].paragraphs[0].add_run("Work").font.bold = True
    t1.rows[0].cells[1].paragraphs[0].add_run("Approach").font.bold = True
    t1.rows[0].cells[2].paragraphs[0].add_run("Relevance to DevMind").font.bold = True
    for j in range(3):
        set_cell_background(t1.rows[0].cells[j], "F1F5F9")
        t1.rows[0].cells[j].paragraphs[0].runs[0].font.size = Pt(9.0)
        
    for i, r_data in enumerate(rel_work):
        row = t1.rows[i + 1]
        for c_idx in range(3):
            row.cells[c_idx].paragraphs[0].add_run(r_data[c_idx]).font.size = Pt(8.5)
            if c_idx == 0:
                row.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        if i % 2 == 1:
            for c_idx in range(3):
                set_cell_background(row.cells[c_idx], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    h24 = doc.add_heading("2.4. Research gap and positioning", level=2)
    h24.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The studies above rule out an overly broad novelty claim. Text preprocessing, query reformulation, retrieval grounding and test-guided repair "
        "have all been examined in prior work. The narrower question explored here is whether a transparent, rule-based issue-analysis stage can improve "
        "file retrieval in a local-first toolchain, and how different retrieval choices behave under the same small set of repository snapshots. "
        "On the systems side, DevMind brings static indexing, retrieval, diff checks and isolated test execution into one inspectable workflow. "
        "The empirical findings remain preliminary: only five issues were evaluated, and relevance was represented by an unreviewed changed-file proxy "
        "rather than independently annotated fault locations."
    )

    # 3. System Architecture and Methodology
    h3 = doc.add_heading("3. System Architecture and Methodology", level=1)
    h3.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "The implementation is organized as a sequence of connected stages: issue intake, text analysis, static code indexing, retrieval, "
        "optional patch generation, diff validation, sandbox testing and evidence reporting. The distinction between deterministic and model-dependent steps is important. "
        "Text processing and patch checks follow explicit rules, whereas patch synthesis depends on the configured language model and its response. "
        "As a result, retrieval can be evaluated on its own, even when a live model does not return a usable patch."
    )
    
    # EMBED FIGURE 1
    add_figure_with_caption(
        doc, "fig1_overall_architecture.png",
        "Fig. 1. Overall architecture showing issue intake, task analysis, static indexing, retrieval, optional LLM patch generation, diff validation, Docker sandbox and report generation."
    )

    # 3.1 Deterministic text analytics
    h31 = doc.add_heading("3.1. Deterministic text analytics", level=2)
    h31.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The task analyzer (`src/devmind/task_analyzer.py`) converts the submitted report into searchable features using fixed rules. "
        "It begins with Unicode NFKC normalization and whitespace cleanup. It then separates compound names such as camelCase and snake_case identifiers, "
        "as well as kebab-case and dotted paths, so that code tokens can match ordinary words in a report. A project-specific stop-word list removes frequent conversational terms; "
        "a frequency count ranks the remaining terms. The analyzer also looks for file extensions, directory paths and identifiers enclosed in backticks. "
        "Finally, keyword rules assign a provisional category, such as a type or attribute error, syntax problem, performance issue or regression. "
        "This category is a heuristic label produced by rules, not the output of a trained classifier."
    )
    doc.add_paragraph(
        "For the devmind-query-v1 experiment, the analyzer supplied four query forms to the retrievers: the original report; a normalized version; "
        "a version enriched with extracted identifiers and high-frequency terms; and a structured form containing the category and component hints alongside the normalized text. "
        "Using the same issue under each condition made it possible to observe whether the transformations changed retrieval order, rather than attributing all differences to a change in the underlying report."
    )

    # EMBED FIGURE 2
    add_figure_with_caption(
        doc, "fig2_text_analytics.png",
        "Fig. 2. Deterministic query processing from raw report text through normalization, identifier splitting, stop-word filtering, term ranking and issue classification."
    )

    # 3.2 Static repository indexing
    h32 = doc.add_heading("3.2. Static repository indexing", level=2)
    h32.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The repository indexer (`src/devmind/indexer.py`) turns source files into searchable code units and attaches their path, symbol and line range. "
        "For Python, it uses the built-in AST parser to identify functions, classes and asynchronous definitions. "
        "For JavaScript, TypeScript, Java, C++, Go, Rust, C#, Ruby, PHP, Kotlin, Swift and embedded HTML script content, extraction relies on lexical scope rules, "
        "including brace-depth tracking where appropriate. The target repository is not executed to build the index. The resulting units provide a practical search representation, "
        "although lexical extraction should not be mistaken for a full compiler front end: language edge cases and complex syntax can still be missed."
    )

    # EMBED FIGURE 3
    add_figure_with_caption(
        doc, "fig3_indexing_retrieval.png",
        "Fig. 3. Repository files are dispatched to language-aware parsers and transformed into metadata-bearing code units for sparse and dense indexing."
    )

    # 3.3 Retrieval methods
    h33 = doc.add_heading("3.3. Retrieval methods", level=2)
    h33.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The TF-IDF retriever assigns a weight to each term in the issue query and each indexed code unit. A candidate is ranked by the cosine similarity between the corresponding weighted vectors:"
    )
    p_eq1 = doc.add_paragraph()
    p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p_eq1.add_run("cos(q, d) = (v_q · v_d) / ( ||v_q|| · ||v_d|| )")
    r1.font.bold = True
    
    doc.add_paragraph(
        "BM25 is a second sparse method. In addition to term frequency, it accounts for how long a code unit is relative to the average document length. "
        "DevMind uses k₁ = 1.5 and b = 0.75. Its score follows the standard form:"
    )
    p_eq2 = doc.add_paragraph()
    p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p_eq2.add_run("score(q, d) = Σ_{t ∈ q} IDF(t) · [ f(t, d) · (k₁ + 1) ] / [ f(t, d) + k₁ · (1 - b + b · |d| / avgdl) ]")
    r2.font.bold = True
    
    doc.add_paragraph(
        "This makes repeated query terms useful without allowing their contribution to grow without bound. "
        "For dense retrieval, the query and each code unit are encoded with sentence-transformers/all-MiniLM-L6-v2, producing 384-dimensional vectors that are ranked by cosine similarity. "
        "DevMind also implements Reciprocal Rank Fusion, which combines the position of an item in each ranked list:"
    )
    p_eq3 = doc.add_paragraph()
    p_eq3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p_eq3.add_run("RRF(d) = Σ_{i} 1 / ( k + rank_i(d) ),   with k = 60.")
    r3.font.bold = True
    
    doc.add_paragraph(
        "Two forms of fusion were evaluated: one combining TF-IDF with BM25, and another combining lexical rankings with dense rankings. "
        "In the reported pilot, the lexical-only combination performed better than the lexical-semantic combination. This observation is specific to the tested repositories, model and query set."
    )

    # 3.4 Patch generation and deterministic validation
    h34 = doc.add_heading("3.4. Patch generation and deterministic validation", level=2)
    h34.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "When a model provider is configured, the orchestrator sends the issue summary and selected source excerpts to the model and asks it to return a unified diff. "
        "Before any candidate is run, `src/devmind/code_agent.py` checks the diff headers, verifies that edited paths remain inside the repository, "
        "rejects empty or no-op changes and can recalculate hunk line counts. The orchestrator also supports a bounded retry process in which a concise account "
        "of a failed test can be included in a later request. Passing the diff checks only means that the patch is suitable for the next stage; "
        "it is not evidence that the edit fixes the underlying defect."
    )

    # EMBED FIGURE 4
    add_figure_with_caption(
        doc, "fig4_patch_validation.png",
        "Fig. 4. Evidence is supplied to the configured model; the proposed unified diff is checked for path containment, header validity, hunk consistency and non-empty edits."
    )

    # 3.5 Isolated execution and reporting
    h35 = doc.add_heading("3.5. Isolated execution and reporting", level=2)
    h35.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The sandbox module prepares a temporary working copy and runs the selected test command inside a Docker container. "
        "The supplied smoke records show execution as UID/GID 10001:10001, with networking disabled, Linux capabilities dropped, "
        "a read-only root filesystem and temporary writable storage. Output is limited to the latest 4,000 characters to keep logs bounded. "
        "These controls reduce the amount of access available to repository code during testing, but they should not be described as a formal guarantee against every container escape. "
        "Test status and supporting details are saved in a run report. Even when a candidate passes, the workflow retains a human-review step rather than authorizing an automatic merge."
    )

    # EMBED FIGURE 5
    add_figure_with_caption(
        doc, "fig5_sandboxed_verification.png",
        "Fig. 5. Patch validation precedes execution in a disposable non-root container; test outputs are bounded and the result is passed to the evidence report."
    )

    doc.add_paragraph(
        "The project also includes a Streamlit interface organized around repair and pipeline inspection, performance/history, and parameter guidance. "
        "A Manifest V3 extension can pass GitHub repository context from a browser tab, and the report generator prepares Markdown pull-request drafts with evidence references. "
        "These features make the workflow easier to inspect and use. Their presence, however, should not be confused with a measured improvement in repair accuracy."
    )

    # 4. Experimental Setup and Evaluation
    h4 = doc.add_heading("4. Experimental Setup and Evaluation", level=1)
    h4.style.font.color.rgb = RGBColor(15, 23, 42)
    
    h41 = doc.add_heading("4.1. Dataset and repository snapshots", level=2)
    h41.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The retrieval evaluation drew five development instances from SWE-bench Lite at dataset revision `b0dde1093fe417d83b7184254edf8199c1f0dff5`. "
        "Each repository was imported at a fixed base commit, and the imported snapshot was checked using SHA-256. A sixth candidate, `pyvista/pyvista`, "
        "was not included because its archive exceeded the configured 100 MiB import limit. For each selected issue, the evaluation used one file changed by the corresponding fix as a relevance proxy. "
        "These labels were not independently adjudicated and identify files, not the exact functions responsible for a defect."
    )

    # Table 2
    add_caption_above(doc, "Table 2. Five pinned repositories used in the DevMind retrieval pilot.")
    repos_data = [
        ("marshmallow-code/marshmallow", "2be2d83a", "1,455", "src/marshmallow/schema.py"),
        ("pvlib/pvlib-python", "04a523fa", "1,233", "pvlib/temperature.py"),
        ("pydicom/pydicom", "b9fb05c1", "2,156", "pydicom/valuerep.py"),
        ("pylint-dev/astroid", "39c2a980", "3,162", "astroid/nodes/node_classes.py"),
        ("sqlfluff/sqlfluff", "304a1978", "1,618", "src/sqlfluff/core/parser/helpers.py")
    ]
    t2 = doc.add_table(rows=len(repos_data) + 1, cols=4)
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)
    
    t2.rows[0].cells[0].paragraphs[0].add_run("Repository").font.bold = True
    t2.rows[0].cells[1].paragraphs[0].add_run("Base commit").font.bold = True
    t2.rows[0].cells[2].paragraphs[0].add_run("Indexed units").font.bold = True
    t2.rows[0].cells[3].paragraphs[0].add_run("Changed-file proxy").font.bold = True
    for j in range(4):
        set_cell_background(t2.rows[0].cells[j], "F1F5F9")
        t2.rows[0].cells[j].paragraphs[0].runs[0].font.size = Pt(9.0)
        
    for i, r_data in enumerate(repos_data):
        row = t2.rows[i + 1]
        for c_idx in range(4):
            row.cells[c_idx].paragraphs[0].add_run(r_data[c_idx]).font.size = Pt(8.5)
            if c_idx == 0:
                row.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        if i % 2 == 1:
            for c_idx in range(4):
                set_cell_background(row.cells[c_idx], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    doc.add_paragraph(
        "Across the five issues, four query forms and five retrieval strategies produced 100 completed ranking runs. Search was performed on the pinned base snapshots. "
        "The evaluator compared the ranked file paths with the separate changed-file proxy labels; the run manifest indicates that the fixing patches themselves were not supplied as retrieval input. "
        "This reduces one obvious form of information leakage, but it does not turn the proxy labels into verified fault locations or make a five-issue pilot representative of the full benchmark."
    )

    # 4.2 Retrieval results
    h42 = doc.add_heading("4.2. Retrieval results", level=2)
    h42.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "Table 3 summarizes the mean scores for the original report text. Precision@K is the share of the first K retrieved files that match the relevance label. "
        "Recall@K measures how many of the labelled relevant files appear within those K results. Mean reciprocal rank (MRR) rewards methods that place the first relevant file near the top, "
        "while nDCG@5 takes the rank of each relevant result into account with greater weight assigned to earlier positions."
    )

    # Table 3
    add_caption_above(doc, "Table 3. Mean retrieval performance on the raw-query condition (five issue instances).")
    raw_results = [
        ("TF-IDF cosine", "0.400", "0.160", "0.800", "0.550", "0.612"),
        ("BM25", "0.400", "0.160", "0.800", "0.517", "0.586"),
        ("Hybrid lexical RRF", "0.600", "0.160", "0.800", "0.667", "0.700"),
        ("Dense cosine", "0.400", "0.080", "0.400", "0.400", "0.400"),
        ("Lexical-semantic RRF", "0.400", "0.120", "0.600", "0.440", "0.477")
    ]
    t3 = doc.add_table(rows=len(raw_results) + 1, cols=6)
    t3.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t3)
    
    headers_t3 = ["Method", "P@1", "P@5", "R@5", "MRR", "nDCG@5"]
    for j, h in enumerate(headers_t3):
        t3.rows[0].cells[j].paragraphs[0].add_run(h).font.bold = True
        set_cell_background(t3.rows[0].cells[j], "F1F5F9")
        t3.rows[0].cells[j].paragraphs[0].runs[0].font.size = Pt(9.0)
        
    for i, r_data in enumerate(raw_results):
        row = t3.rows[i + 1]
        for c_idx in range(6):
            row.cells[c_idx].paragraphs[0].add_run(r_data[c_idx]).font.size = Pt(8.5)
            if c_idx == 0:
                row.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        if i % 2 == 1:
            for c_idx in range(6):
                set_cell_background(row.cells[c_idx], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    doc.add_paragraph(
        "For four of the five issue instances, both TF-IDF and BM25 placed the changed-file proxy somewhere in the top five, giving each a mean Recall@5 of 0.800. "
        "Dense cosine retrieval did so for two instances, corresponding to 0.400. The TF-IDF/BM25 fusion did not increase Recall@5, but it moved the relevant file to rank one more often: "
        "P@1 was 0.600, MRR was 0.667 and nDCG@5 was 0.700. The lexical-semantic fusion scored below the lexical-only combination in this pilot. "
        "With only five observations and proxy labels, these values are useful for comparing the tested configurations, not for claiming that lexical retrieval is universally superior for source code."
    )

    # Table 4
    add_caption_above(doc, "Table 4. TF-IDF ranking metrics across the four query variants.")
    q_results = [
        ("Raw", "0.400", "0.160", "0.800", "0.550", "0.612"),
        ("Normalized", "0.400", "0.160", "0.800", "0.550", "0.612"),
        ("Keywords/identifiers", "0.400", "0.160", "0.800", "0.567", "0.626"),
        ("Structured", "0.400", "0.160", "0.800", "0.567", "0.626")
    ]
    t4 = doc.add_table(rows=len(q_results) + 1, cols=6)
    t4.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t4)
    
    headers_t4 = ["Query condition", "P@1", "P@5", "R@5", "MRR", "nDCG@5"]
    for j, h in enumerate(headers_t4):
        t4.rows[0].cells[j].paragraphs[0].add_run(h).font.bold = True
        set_cell_background(t4.rows[0].cells[j], "F1F5F9")
        t4.rows[0].cells[j].paragraphs[0].runs[0].font.size = Pt(9.0)
        
    for i, r_data in enumerate(q_results):
        row = t4.rows[i + 1]
        for c_idx in range(6):
            row.cells[c_idx].paragraphs[0].add_run(r_data[c_idx]).font.size = Pt(8.5)
            if c_idx == 0:
                row.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        if i % 2 == 1:
            for c_idx in range(6):
                set_cell_background(row.cells[c_idx], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    doc.add_paragraph(
        "The normalized-query condition produced the same aggregate TF-IDF scores as the raw text. When identifiers and ranked terms were added, "
        "MRR rose from 0.550 to 0.567 and nDCG@5 from 0.612 to 0.626. The other reported measures—P@1, P@5 and Recall@5—did not change. "
        "The difference is small, and the study did not include confidence intervals or a significance test. "
        "It is therefore reasonable to describe identifier-aware enrichment as a promising signal in this pilot, but not as a proven improvement."
    )

    # 4.3 Indexing cost and latency
    h43 = doc.add_heading("4.3. Indexing cost and latency", level=2)
    h43.style.font.color.rgb = RGBColor(30, 41, 59)

    # Table 5
    add_caption_above(doc, "Table 5. Retrieval index construction and query-time measurements.")
    cost_data = [
        ("Index construction", "1.199 s", "594.737 s", "Dense includes document encoding and vector preparation; about 496× longer."),
        ("Mean query latency", "0.0362 s", "0.0622 s", "Dense includes query embedding and ranking."),
        ("Sampled peak process-tree RSS", "Not reported as matched", "932.89 MiB", "Dense run; sampled every 25 ms."),
        ("Hybrid lexical-semantic query latency", "—", "0.1738 s", "Mean for the combined dense/sparse retrieval path.")
    ]
    t5 = doc.add_table(rows=len(cost_data) + 1, cols=4)
    t5.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t5)
    
    headers_t5 = ["Measurement", "TF-IDF", "Dense embeddings", "Notes"]
    for j, h in enumerate(headers_t5):
        t5.rows[0].cells[j].paragraphs[0].add_run(h).font.bold = True
        set_cell_background(t5.rows[0].cells[j], "F1F5F9")
        t5.rows[0].cells[j].paragraphs[0].runs[0].font.size = Pt(9.0)
        
    for i, r_data in enumerate(cost_data):
        row = t5.rows[i + 1]
        for c_idx in range(4):
            row.cells[c_idx].paragraphs[0].add_run(r_data[c_idx]).font.size = Pt(8.5)
            if c_idx == 0:
                row.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        if i % 2 == 1:
            for c_idx in range(4):
                set_cell_background(row.cells[c_idx], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    doc.add_paragraph(
        "These measurements were collected on a CPU system using the pinned all-MiniLM-L6-v2 revision, Sentence Transformers 5.7.0, "
        "Transformers 4.57.6 and PyTorch 2.13.0+cpu. In this run, TF-IDF index construction completed in 1.199 s, while dense embedding and index preparation took 594.737 s. "
        "The resulting ratio is approximately 496 to 1. It is a comparison of elapsed time in this environment, not a direct measure of energy use. "
        "Different hardware, model versions, batching or cache conditions could change the result, and dense retrieval may perform differently on other datasets."
    )

    # EMBED FIGURE 6
    add_figure_with_caption(
        doc, "fig6_evaluation_protocol.png",
        "Fig. 6. Paired retrieval protocol across five pinned repositories, four query conditions and five ranking strategies using file-level proxy labels."
    )

    # 5. Code Repair and Verification Evidence
    h5 = doc.add_heading("5. Code Repair and Verification Evidence", level=1)
    h5.style.font.color.rgb = RGBColor(15, 23, 42)
    
    h51 = doc.add_heading("5.1. Live model generation result", level=2)
    h51.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The live-model audit sent a repair request to the local Ollama endpoint using qwen3:1.7b and the Cricket Scorer Pro buggy fixture. "
        "The recorded response time was approximately 120.51 s. The model identified the relevant addRun logic and suggested a replacement, "
        "but its response did not contain a valid unified-diff removal/addition pair. The parser consequently produced no applicable candidate, "
        "and the validator stopped the process as a no-op before Docker execution. This is evidence that the configured model was called "
        "and that malformed output was safely blocked. It is not evidence of a successful model-generated repair."
    )

    h52 = doc.add_heading("5.2. Separate candidate-patch sandbox verification", level=2)
    h52.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The raw Cricket Scorer repair-analysis JSON is marked repair_blocked_insufficient_evidence; its test_result.executed field is false. "
        "The available artifact therefore does not show that a Cricket patch was applied or that its tests passed. "
        "Although a project summary describes a separate Cricket candidate-patch check, that outcome is not corroborated by the uploaded raw repair record. "
        "The report consequently excludes Cricket from the set of verified repairs. This conservative treatment keeps localization, patch generation and successful test execution as separate claims."
    )

    h53 = doc.add_heading("5.3. QuickCart retry fixture and sandbox hardening", level=2)
    h53.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "The QuickCart retry record describes a controlled cart-persistence fixture. It explicitly identifies its provider as a deterministic two-response fixture "
        "and states that no LLM call was made. The first candidate failed the reload-persistence test; the retry stage performed additional retrieval, "
        "and the second candidate passed the targeted test. The final status remained tests_passed_review_required. "
        "The separate Docker smoke evidence records baseline failures followed by passing candidate tests for controlled fixtures. "
        "Together, these results demonstrate aspects of retry handling and isolated test execution, but they do not establish a live-model repair rate for real projects."
    )

    # EMBED FIGURE 7
    add_figure_with_caption(
        doc, "fig7_repair_review_gate.png",
        "Fig. 7. Four verification stages: diff validity, sandboxed test execution, mandatory human review and separate benchmark-scale evaluation."
    )

    # 6. Software Quality and Implementation
    h6 = doc.add_heading("6. Software Quality and Implementation", level=1)
    h6.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "The latest supplied pytest record is dated 18 November 2026 and reports 179 passing tests, three skips and an elapsed time of 4.93 s. "
        "The skipped cases require Unix-specific symlink permissions that were unavailable on the Windows host. "
        "The suites cover the task analyzer, multi-language indexer, retrieval methods, embedding adapter, diff validator, sandbox, orchestrator, "
        "statistics, pull-request generator, parameter guide and GitHub import. The browser extension has a separate Node.js service-worker suite "
        "with three additional passing tests. The subsystem counts listed in the handoff do not add up to the aggregate pytest total, "
        "so this paper reports the recorded aggregate rather than implying that the listed rows form a complete breakdown."
    )
    doc.add_paragraph(
        "The repository documentation also describes Streamlit, command-line and API entry points, immutable public-GitHub archive import, "
        "Markdown pull-request drafts and a browser extension. The GitHub import smoke record provides evidence that a public repository snapshot can be fetched and analyzed. "
        "These integration checks show that the tested paths work under the recorded conditions; they should not be read as proof that every feature behaves correctly for every repository or deployment environment."
    )

    # Table 6
    add_caption_above(doc, "Table 6. Verification evidence and its correct interpretation.")
    ver_data = [
        ("Pytest run (18 Nov 2026)", "179 passed; 3 skipped", "Automated tests passed in recorded environment; skipped symlink cases unexecuted."),
        ("Qwen live generation audit", "Model called; diff rejected as no-op", "LLM invocation and safe rejection; no successful LLM patch application."),
        ("Cricket repair-analysis artifact", "repair_blocked_insufficient_evidence; test not executed", "Uploaded raw artifact does not establish successful Cricket patch or test."),
        ("QuickCart deterministic retry", "Attempt 1 failed; attempt 2 passed", "Retry/sandbox mechanics with deterministic fixture; not a live LLM result."),
        ("Docker non-root smoke", "UID 10001; network disabled; candidates passed", "Configured sandbox controls and test execution for the recorded fixtures."),
        ("Extension tests", "3 Node tests passed", "Service-worker URL and message-handling behaviours covered by those tests.")
    ]
    t6 = doc.add_table(rows=len(ver_data) + 1, cols=3)
    t6.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t6)
    
    headers_t6 = ["Evidence artifact", "Observed result", "What it establishes"]
    for j, h in enumerate(headers_t6):
        t6.rows[0].cells[j].paragraphs[0].add_run(h).font.bold = True
        set_cell_background(t6.rows[0].cells[j], "F1F5F9")
        t6.rows[0].cells[j].paragraphs[0].runs[0].font.size = Pt(9.0)
        
    for i, r_data in enumerate(ver_data):
        row = t6.rows[i + 1]
        for c_idx in range(3):
            row.cells[c_idx].paragraphs[0].add_run(r_data[c_idx]).font.size = Pt(8.5)
            if c_idx == 0:
                row.cells[c_idx].paragraphs[0].runs[0].font.bold = True
        if i % 2 == 1:
            for c_idx in range(3):
                set_cell_background(row.cells[c_idx], "F8FAFC")
                
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # 7. Discussion, Limitations and Research Governance
    h7 = doc.add_heading("7. Discussion, Limitations and Research Governance", level=1)
    h7.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "The results point to three practical observations. First, exact code identifiers appear to be useful retrieval cues: "
        "in this small sample, TF-IDF and BM25 found the changed-file proxy more often in their top five than the tested dense encoder. "
        "Combining the two lexical rankings improved the placement of the first relevant file. Second, query cleanup by itself did not move the aggregate scores, "
        "while adding identifier and term-frequency information led to a small increase in TF-IDF MRR and nDCG. Third, diff validation and the Docker boundary provide useful safeguards, "
        "but neither should be treated as proof that an automated repair has succeeded. The live Qwen output was rejected before execution; "
        "the passing sandbox records came from controlled candidate fixtures, including one driven by a deterministic provider."
    )

    h71 = doc.add_heading("7.1. Limitations", level=2)
    h71.style.font.color.rgb = RGBColor(30, 41, 59)
    lims = [
        "The retrieval pilot covers five SWE-bench Lite development issues. Each issue has one unreviewed changed-file proxy; the evaluation contains no blind multi-reviewer annotations, confidence ratings or function-level fault locations.",
        "The reported scores are descriptive averages from a very small sample. No confidence intervals, statistical significance tests or effect-size estimates were calculated, so the results cannot establish general superiority of one retrieval family across repositories.",
        "Build-time and memory measurements were taken on one CPU-based setup. The observed 496-fold timing difference is not an energy-consumption measurement and should not be assumed to hold on other hardware, model versions or cache states.",
        "For languages other than Python, the indexer relies on lexical scope extraction rather than a complete language parser. Macros, generated sources, unusual syntax and deeply nested constructs may therefore be represented incompletely.",
        "The live Qwen response for Cricket Scorer did not pass diff parsing. The raw analysis record says repair_blocked_insufficient_evidence and shows that no test was run. The successful smoke fixtures cover QuickCart and safe-divide; the QuickCart retry specifically used a deterministic provider, not a live LLM.",
        "The Docker configuration limits privileges and network access, but container hardening is not an absolute security guarantee. Because logs retain only the most recent 4,000 characters, early diagnostics may be lost in verbose test runs."
    ]
    for lim in lims:
        p_b = doc.add_paragraph(style='List Bullet')
        p_b.add_run(lim)

    h72 = doc.add_heading("7.2. Research and operational governance", level=2)
    h72.style.font.color.rgb = RGBColor(30, 41, 59)
    doc.add_paragraph(
        "DevMind should be viewed as a research prototype that assists developers with code search and evidence inspection. "
        "The current evidence is not sufficient to recommend unattended use on production repositories. Any suggested change still needs review by a developer, "
        "execution of the relevant project test suite and the normal release checks for that codebase. The evidence labels show which source spans were retrieved; "
        "they do not prove that those spans caused the reported behaviour. In the same way, a passing targeted test supports a proposed fix "
        "but cannot rule out regressions elsewhere in the application."
    )

    # 8. Conclusion and Future Work
    h8 = doc.add_heading("8. Conclusion and Future Work", level=1)
    h8.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "This study described DevMind, a local-first framework that uses deterministic text analysis to organize bug reports, "
        "indexes source code for retrieval, and places explicit checks around candidate patch execution. In the five-repository SWE-bench Lite development pilot, "
        "TF-IDF and BM25 each achieved Recall@5 of 0.800, compared with 0.400 for dense cosine retrieval. Combining the two lexical rankings gave "
        "P@1 = 0.600, MRR = 0.667 and nDCG@5 = 0.700. Adding identifiers to the query yielded a small increase in TF-IDF MRR and nDCG, "
        "while dense indexing took much longer and used more sampled memory in the measured CPU environment. The recorded Python test run completed with 179 passes and three environment-dependent skips."
    )
    doc.add_paragraph(
        "The repair findings need a separate interpretation. The live Qwen request was completed, but the proposed diff was rejected before it could be tested. "
        "Other controlled candidate fixtures passed targeted tests inside the sandbox; they demonstrate that the validation and execution path can be exercised, "
        "not that the system reliably repairs real issues through live model generation. The next evaluation should use a larger and more diverse issue set, "
        "independently reviewed function-level annotations, controlled ablations and statistical analysis. It should also test more parser and retrieval configurations "
        "and measure complete model-generated repair attempts from initial localization through regression testing."
    )

    # Acknowledgements
    h_ack = doc.add_heading("Acknowledgements", level=1)
    h_ack.style.font.color.rgb = RGBColor(15, 23, 42)
    doc.add_paragraph(
        "The authors thank the Department of Computer Science and Engineering, Amrita School of Computing, Amrita Vishwa Vidyapeetham, for its academic support. "
        "The wording of this acknowledgement should be confirmed with the project team and faculty before submission."
    )

    # References
    h_ref = doc.add_heading("References", level=1)
    h_ref.style.font.color.rgb = RGBColor(15, 23, 42)
    refs = [
        "[1] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, et al., 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,' in Advances in Neural Information Processing Systems, vol. 33, pp. 9459–9474, 2020. https://proceedings.neurips.cc/paper/2020/hash/6b493230205f780e1bc26945df7481e5-Abstract.html",
        "[2] C. E. Jimenez, J. Yang, A. Wettig, S. Yao, K. Pei, O. Press, and K. Narasimhan, 'SWE-bench: Can Language Models Resolve Real-World GitHub Issues?,' in Proc. International Conference on Learning Representations (ICLR), 2024. https://openreview.net/forum?id=VTColl7jqz",
        "[3] J. Yang, C. E. Jimenez, A. Wettig, K. Lieret, S. Yao, K. Narasimhan, and O. Press, 'SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering,' in Advances in Neural Information Processing Systems, vol. 37, 2024. doi: 10.52202/079017-1601.",
        "[4] Y. Zhang, H. Ruan, Z. Fan, and A. Roychoudhury, 'AutoCodeRover: Autonomous Program Improvement,' in Proc. 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA), pp. 1592–1604, 2024. doi: 10.1145/3650212.3680384.",
        "[5] C. S. Xia, Y. Deng, S. Dunn, and L. Zhang, 'Demystifying LLM-Based Software Engineering Agents,' Proc. ACM on Software Engineering, vol. 2, no. FSE, Art. FSE037, 2025. doi: 10.1145/3715754.",
        "[6] I. Bouzenia, P. Devanbu, and M. Pradel, 'RepairAgent: An Autonomous, LLM-Based Agent for Program Repair,' in Proc. IEEE/ACM 47th International Conference on Software Engineering (ICSE), pp. 2188–2200, 2025. doi: 10.1109/ICSE55347.2025.00157.",
        "[7] C. S. Xia and L. Zhang, 'Automated Program Repair via Conversation: Fixing 162 out of 337 Bugs for $0.42 Each using ChatGPT,' in Proc. 33rd ACM SIGSOFT International Symposium on Software Testing and Analysis (ISSTA), pp. 819–831, 2024. doi: 10.1145/3650212.3680323.",
        "[8] G. Long, J. Gong, H. Fang, and T. Chen, 'Learning Software Bug Reports: A Systematic Literature Review,' ACM Transactions on Software Engineering and Methodology, 2025. doi: 10.1145/3750040.",
        "[9] A. M. Samir and M. M. Rahman, 'Improved IR-Based Bug Localization with Intelligent Relevance Feedback (BRaIn),' in Proc. 33rd IEEE/ACM International Conference on Program Comprehension (ICPC), 2025. doi: 10.1109/ICPC66645.2025.00065. Preprint: arXiv:2501.10542.",
        "[10] G. Caumartin and G. Melo, 'Reformulate, Retrieve, Localize: Agents for Repository-Level Bug Localization,' presented at the ICSE 2026 Workshop on Bots and Agents in Software Engineering (BotSE), 2026. Preprint: arXiv:2512.07022.",
        "[11] A. M. Samir and M. M. Rahman, 'Improving IR-based Bug Localization with Semantics-Driven Query Reduction,' Journal of Systems and Software, vol. 237, Art. 112860, July 2026. doi: 10.1016/j.jss.2026.112860.",
        "[12] R. Andrade, C. Teixeira, N. Laranjeiro, and M. Vieira, 'An Empirical Study on the Classification of Bug Reports With Machine Learning,' IEEE Open Journal of the Computer Society, vol. 7, pp. 1213–1224, 2026. doi: 10.1109/OJCS.2026.3692087.",
        "[13] S. S. Chaudhari, R. T. Jacob, J. Cao, M. S. Rashid, M. Goswami, and C. Bock, 'SpIDER: Spatially Informed Dense Embedding Retrieval for Software Issue Localization,' in Proc. 2026 Conference on Empirical Methods in Natural Language Processing (EMNLP), pp. 44096–44131, 2026. https://aclanthology.org/2026.emnlp-main.1938/",
        "[14] Q. Meng, X. Zhang, Z. Ren, and J. Visser, 'EviACT: An Evidence-to-Action Framework for Agentic Program Repair,' arXiv preprint arXiv:2605.27238, version 2, 2026. https://arxiv.org/abs/2605.27238",
        "[15] M. N. Al Awad and S. Ivanov, 'Loc2Repair: A Framework for Evaluating the Impact of File-Level Issue Localization in Repo-Level LLM Repair,' arXiv preprint arXiv:2606.30963, 2026. https://arxiv.org/abs/2606.30963",
        "[16] N. Chondamrongkul, M. P. P. Kyaw, S. M. Ko, P. P. Paing, M. K. T. Swe, and T. Hongthong, 'RepoAI: Automated Code Refactoring Through Multi-Agent LLM Orchestration and Retrieval-Augmented Generation,' Science of Computer Programming, vol. 253, Art. 103477, 2026. doi: 10.1016/j.scico.2026.103477.",
        "[17] S. Robertson and H. Zaragoza, 'The Probabilistic Relevance Framework: BM25 and Beyond,' Foundations and Trends in Information Retrieval, vol. 3, no. 4, pp. 333–389, 2009. doi: 10.1561/1500000019.",
        "[18] G. V. Cormack, C. L. A. Clarke, and S. Buettcher, 'Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,' in Proc. 32nd ACM SIGIR Conference on Research and Development in Information Retrieval, pp. 758–759, 2009. doi: 10.1145/1571941.1572114.",
        "[19] N. Reimers and I. Gurevych, 'Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,' in Proc. 2019 Conference on Empirical Methods in Natural Language Processing and 9th International Joint Conference on Natural Language Processing (EMNLP-IJCNLP), pp. 3982–3992, 2019. doi: 10.18653/v1/D19-1410."
    ]
    for ref in refs:
        p_r = doc.add_paragraph()
        p_r.paragraph_format.left_indent = Inches(0.4)
        p_r.paragraph_format.first_line_indent = Inches(-0.4)
        run_ref = p_r.add_run(ref)
        run_ref.font.size = Pt(8.5)

    out_file = "DevMind_Term_Project_Report.docx"
    doc.save(out_file)
    print(f"Successfully generated {out_file} with {len(doc.paragraphs)} paragraphs and all 7 figures embedded!")

if __name__ == '__main__':
    build_report()
