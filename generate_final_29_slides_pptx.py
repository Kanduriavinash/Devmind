"""
Builds the complete 29-slide presentation deck (DevMind_Presentation.pptx)
matching the user's exact presentation script, incorporating cards, tables,
and embedded diagram figures where appropriate.
"""
import os
from pathlib import Path
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

FIG_DIR = Path("reports/devmind-report-draft/figures")

# Design Colors
BG_DARK = RGBColor(10, 15, 29)          # #0A0F1D Deep Navy
CARD_BG = RGBColor(22, 31, 48)          # #161F30 Card Slate
CARD_ALT_BG = RGBColor(26, 37, 58)      # #1A253A Slightly lighter slate
CARD_BORDER = RGBColor(39, 53, 79)      # #27354F Border Slate
ACCENT_CYAN = RGBColor(56, 189, 248)    # #38BDF8 Cyan Sky
ACCENT_GREEN = RGBColor(52, 211, 153)   # #34D399 Emerald
ACCENT_AMBER = RGBColor(251, 191, 36)   # #FBBF24 Amber
TEXT_WHITE = RGBColor(248, 250, 252)    # #F8FAFC
TEXT_MUTED = RGBColor(148, 163, 184)    # #94A3B8
TEXT_LIGHT = RGBColor(203, 213, 225)    # #CBD5E1

TOTAL_SLIDES = 29

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_DARK

def add_header(slide, tag_text, title_text, subtitle_text=""):
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.35))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = 'Arial'
    p_tag.font.size = Pt(9.5)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_CYAN

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.5), Inches(0.55))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = 'Arial'
    p_title.font.size = Pt(19)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.22), Inches(11.5), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = 'Arial'
        p_sub.font.size = Pt(11)
        p_sub.font.color.rgb = TEXT_MUTED

def add_footer(slide, current_slide):
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.02), Inches(11.733), Inches(0.35))
    tf = footer_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"DEVMIND  |  TEXT ANALYTICS TERM PROJECT  |  AMRITA SCHOOL OF COMPUTING                                                     SLIDE {current_slide:02d} / {TOTAL_SLIDES:02d}"
    p.font.name = 'Arial'
    p.font.size = Pt(8.0)
    p.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, title="", body_lines=None, border_color=None, bg_color=None, title_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color or CARD_BG
    shape.line.color.rgb = border_color or CARD_BORDER
    shape.line.width = Pt(1)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.18)
    tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.18)
    tf.margin_bottom = Inches(0.18)

    if title:
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = 'Arial'
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = title_color or ACCENT_CYAN
        p0.space_after = Pt(6)

    if body_lines:
        first = True if not title else False
        for line in body_lines:
            if first:
                p = tf.paragraphs[0]
                first = False
            else:
                p = tf.add_paragraph()
            p.text = line
            p.font.name = 'Arial'
            p.font.size = Pt(10)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(3)
    return shape

def add_table_shape(slide, left, top, width, height, headers, rows_data):
    num_rows = len(rows_data) + 1
    num_cols = len(headers)
    table_shape = slide.shapes.add_table(num_rows, num_cols, left, top, width, height)
    table = table_shape.table

    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = RGBColor(28, 41, 65)
        p = cell.text_frame.paragraphs[0]
        p.text = h
        p.font.name = 'Arial'
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = ACCENT_CYAN

    for i, row in enumerate(rows_data):
        bg = CARD_ALT_BG if i % 2 == 1 else CARD_BG
        for j, val in enumerate(row):
            cell = table.cell(i + 1, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg
            p = cell.text_frame.paragraphs[0]
            p.text = str(val)
            p.font.name = 'Arial'
            p.font.size = Pt(9.0)
            p.font.color.rgb = TEXT_LIGHT
            if j == 0:
                p.font.bold = True
    return table_shape

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 01: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)
    
    box = s1.shapes.add_textbox(Inches(1.0), Inches(1.1), Inches(11.333), Inches(5.0))
    tf = box.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "TEXT ANALYTICS  |  SEMESTER V  |  B.TECH CSE"
    p0.font.name = 'Arial'
    p0.font.size = Pt(11)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_CYAN
    p0.space_after = Pt(12)

    p1 = tf.add_paragraph()
    p1.text = "DEVMIND"
    p1.font.name = 'Arial'
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_WHITE
    p1.space_after = Pt(6)

    p2 = tf.add_paragraph()
    p2.text = "Evidence-Grounded Bug Analysis, Repository Localization & Sandboxed Repair"
    p2.font.name = 'Arial'
    p2.font.size = Pt(17)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_GREEN
    p2.space_after = Pt(8)

    p3 = tf.add_paragraph()
    p3.text = "A local-first text analytics and software maintenance framework"
    p3.font.name = 'Arial'
    p3.font.size = Pt(12)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_after = Pt(22)

    p4 = tf.add_paragraph()
    p4.text = "Project Team:  P. Sharath Chandhra   ·   B. Shashank Manohar   ·   K. Venkat Sai Mani Avinash"
    p4.font.name = 'Arial'
    p4.font.size = Pt(13)
    p4.font.bold = True
    p4.font.color.rgb = TEXT_WHITE
    p4.space_after = Pt(4)

    p5 = tf.add_paragraph()
    p5.text = "Amrita School of Computing  ·  Amrita Vishwa Vidyapeetham  ·  Amritapuri Campus"
    p5.font.name = 'Arial'
    p5.font.size = Pt(11)
    p5.font.color.rgb = TEXT_LIGHT

    add_footer(s1, 1)

    # =========================================================================
    # SLIDE 02: 01 | OVERVIEW (DevMind at a glance)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "01 | Overview", "DevMind at a Glance", "A research prototype connecting natural-language bug reports with repository evidence, patch checks and isolated test execution.")
    
    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(1.4), "5 REPOSITORIES", 
             ["SWE-bench Lite development instances in the pinned evaluation pilot."])
    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(1.4), "100 RETRIEVAL RUNS", 
             ["5 methods × 4 query variants × 5 issue instances evaluated."])
    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(1.4), "179 TESTS PASSED", 
             ["Automated pytest suite + 3 platform tests in Node.js (100% pass)."])

    add_card(s2, Inches(0.8), Inches(3.4), Inches(5.6), Inches(3.3), "WHAT THE SYSTEM DOES",
             ["• Understands issues: Normalizes reports and extracts technical tokens.",
              "• Finds code: Indexes program symbols and ranks candidate locations.",
              "• Checks changes: Validates diffs and tests candidate patches in Docker.",
              "• Reports evidence: Records source spans, test outcomes and review status."])

    add_card(s2, Inches(6.8), Inches(3.4), Inches(5.6), Inches(3.3), "HOW TO READ THIS PROJECT",
             ["• Research focus: Text analytics and retrieval quality for code artifacts.",
              "• Engineering focus: Patch validation and non-root sandbox controls.",
              "• Evaluation scope: An exploratory 5-repo pilot, not a full SWE-bench score.",
              "• Honest boundary: Live LLM-generated repair is not yet verified end-to-end."])
    add_footer(s2, 2)

    # =========================================================================
    # SLIDE 03: 02 | MOTIVATION (Why bug analysis is difficult)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "02 | Motivation", "Why Bug Analysis is Difficult", "A user describes what went wrong; the repository expresses how the software is implemented.")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "HUMAN LANGUAGE ISSUE",
             ["• Example:", "“The cart disappears after refresh.”",
              "\n• Challenge:", "Reports often omit function names, file paths, or class boundaries.",
              "\n• Noise & Ambiguity:", "Conversational filler, partial stack traces, and subjective descriptions.",
              "\n• Need:", "Extract the most informative terms before executing repository search."])

    add_card(s3, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9), "STRUCTURED CODEBASE",
             ["• Compound Identifiers:", "camelCase, snake_case, and dotted module paths.",
              "\n• Hierarchical Structure:", "Code is divided across files, classes, methods, and nested blocks.",
              "\n• Scale:", "Relevant logic is distributed across many interconnected modules.",
              "\n• Need:", "Localize evidence at file, symbol, and line-span granularity."])

    add_card(s3, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.9), "TRUST & SAFE REPAIR",
             ["• Generation Risk:", "LLMs return malformed syntax, wrong hunks, or hallucinated paths.",
              "\n• Execution Risk:", "Repository code must NEVER run freely on the host machine.",
              "\n• Verification:", "Tests need to run in an isolated candidate container copy.",
              "\n• Need:", "Preserve full traceability and enforce mandatory human review."])
    add_footer(s3, 3)

    # =========================================================================
    # SLIDE 04: 03 | PROBLEM FORMULATION
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "03 | Problem Formulation", "From a Bug Report to Candidate Code Locations", "Bridging natural language symptoms and executable program structures.")

    add_card(s4, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "INPUT: BUG REPORT  q",
             ["• Natural-language symptom description.",
              "• Observed incorrect behavior.",
              "• Partial stack traces or logs.",
              "• Mentioned identifiers or component hints.",
              "\nPaired with:",
              "• Fixed repository snapshot R = {f1, f2, ..., fn}."])

    add_card(s4, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9), "DEVMIND TRANSFORMATION",
             ["• Task Analysis:", "q  -->  q* (structured features)",
              "\n• Static Multi-Language Indexing:", "Extracts code units without executing code.",
              "\n• Hybrid Retrieval & RRF:", "Ranks candidate code locations C = {c1, ..., ck}.",
              "\n• Guarded Patch Proposal:", "Diff validation & sandbox execution."])

    add_card(s4, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.9), "OUTPUT: EVIDENCE  C",
             ["• Ranked candidate files and functions.",
              "• Exact line spans and character counts.",
              "• Proposed unified diff (if model active).",
              "• Bounded sandbox test evidence.",
              "\nCore Principle:",
              "Zero alteration of the host repository."])
    add_footer(s4, 4)

    # =========================================================================
    # SLIDE 05: 04 | OBJECTIVES
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "04 | Objectives", "Six Engineering Objectives", "Translating the research problem into testable, modular subsystems.")

    objs = [
        ("01", "Deterministic Issue Triage", "Clean bug reports; split identifiers; extract keywords and component hints without model drift."),
        ("02", "Static Multi-Language Indexing", "Map repository files to classes, functions and line spans without host code execution."),
        ("03", "Retrieval Comparison", "Evaluate TF-IDF, BM25, dense embeddings and rank fusion under consistent conditions."),
        ("04", "Patch Integrity Checks", "Reject unsafe paths, malformed headers, no-op edits and invalid hunk line counts."),
        ("05", "Disposable Test Execution", "Run candidate patches as a non-root user (UID 10001) in restricted Docker containers."),
        ("06", "Auditable Developer Output", "Expose evidence spans [E1..En], run history, test logs and pull-request drafts for review.")
    ]
    for i, (num, title, desc) in enumerate(objs):
        x = Inches(0.8 + (i % 3) * 4.0)
        y = Inches(1.8 + (i // 3) * 2.5)
        add_card(s5, x, y, Inches(3.7), Inches(2.2), f"{num} · {title}", [desc])
    add_footer(s5, 5)

    # =========================================================================
    # SLIDE 06: 05 | RELATED WORK
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "05 | Related Work", "Evolution of Repository-Level Program Repair", "DevMind is positioned alongside established benchmarks, retrieval systems and agents.")

    works = [
        ("SWE-bench  |  ICLR 2024", "Benchmark of real GitHub issues paired with repository snapshots and tests. [1]"),
        ("SWE-agent  |  NeurIPS 2024", "Shows how an agent-computer interface supports repository navigation and tool use. [2]"),
        ("AutoCodeRover  |  ISSTA 2024", "Uses program structure and AST code search to retrieve issue-relevant context. [3]"),
        ("Agentless  |  FSE 2025", "Studies a structured localization-repair-validation process without complex tool-using agents. [4]"),
        ("RepairAgent  |  ICSE 2025", "Explores an LLM agent that plans and invokes repair-specific tools via an FSM. [5]"),
        ("2026 Retrieval Research", "SpIDER (EMNLP 2026) studies graph-aware dense retrieval; SWERank studies reranked localization. [6,7]")
    ]
    for i, (title, desc) in enumerate(works):
        x = Inches(0.8 + (i % 3) * 4.0)
        y = Inches(1.8 + (i // 3) * 2.5)
        add_card(s6, x, y, Inches(3.7), Inches(2.2), title, [desc])
    add_footer(s6, 6)

    # =========================================================================
    # SLIDE 07: 06 | RESEARCH POSITIONING
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "06 | Research Positioning", "Research Gaps and Formal Questions", "The project tests specific engineering choices rather than claiming a universal repair solution.")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "GAP 1: ISSUE INTAKE",
             ["• Research Question:", "How much can deterministic text analytics—identifier splitting, stop-word filtering and component hints—improve issue-to-code retrieval?",
              "\n• Addressed by:", "RQ1: Query enrichment evaluation comparing raw, normalized, keyword, and structured forms."])

    add_card(s7, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9), "GAP 2: CODE RETRIEVAL",
             ["• Research Question:", "How do sparse, dense and fused retrieval methods trade off ranking quality, indexing latency and memory on code artifacts?",
              "\n• Addressed by:", "RQ2: Comparative evaluation of TF-IDF, BM25, all-MiniLM-L6-v2, and RRF rank fusion."])

    add_card(s7, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.9), "GAP 3: TRUST & SAFETY",
             ["• Research Question:", "How can generated changes be checked for diff integrity and tested in a restricted environment before developer review?",
              "\n• Addressed by:", "RQ3–RQ4: Deterministic diff validation, non-root Docker sandboxing, and host integrity checks."])
    add_footer(s7, 7)

    # =========================================================================
    # SLIDE 08: 07 | SYSTEM DESIGN
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "07 | System Design", "DevMind End-to-End Workflow Pipeline", "An auditable sequence connects report intake to evidence-backed output.")

    # Embed Fig 1 if exists, else cards
    fig1_path = FIG_DIR / "fig1_overall_architecture.png"
    if fig1_path.exists():
        img = s8.shapes.add_picture(str(fig1_path), Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.1))
        add_card(s8, Inches(0.8), Inches(6.0), Inches(11.733), Inches(0.9), "", 
                 ["Safety boundary: Repository snapshots are indexed statically; candidate execution is delegated to disposable containers."],
                 bg_color=CARD_ALT_BG)
    else:
        stages = [
            ("1. INTAKE", "Bug report + repo snapshot"),
            ("2. ANALYZE", "Normalize & extract features"),
            ("3. INDEX", "Static code symbols & spans"),
            ("4. RETRIEVE", "TF-IDF / BM25 / Dense RRF"),
            ("5. PROPOSE", "LLM candidate diff (optional)"),
            ("6. VERIFY", "Diff audit + Docker sandbox")
        ]
        for i, (st, desc) in enumerate(stages):
            x = Inches(0.8 + (i % 6) * 1.95)
            add_card(s8, x, Inches(2.2), Inches(1.85), Inches(3.5), st, [desc])
    add_footer(s8, 8)

    # =========================================================================
    # SLIDE 09: 08 | TEXT ANALYTICS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "08 | Text Analytics", "Turning a Bug Report into Structured Features", "The Task Analyzer is deterministic and rule-based; the same report produces identical features.")

    fig2_path = FIG_DIR / "fig2_text_analytics.png"
    if fig2_path.exists():
        s9.shapes.add_picture(str(fig2_path), Inches(0.8), Inches(1.8), Inches(6.2), Inches(4.9))
        add_card(s9, Inches(7.3), Inches(1.8), Inches(5.2), Inches(4.9), "WORKED EXAMPLE",
                 ["• Example Issue:", "“When I click 1, matchState.balls counts twice in script.js.”",
                  "\n• NFKC Cleanup:", "Standardizes Unicode quotes, dashes, and whitespace.",
                  "\n• Identifier Splitting:", "matchState.balls --> ['match', 'state', 'balls']",
                  "\n• Stop Words & Ranking:", "Filters conversational noise; ranks salient terms.",
                  "\n• Structured Output q*:", "TOKENS: match · state · balls\nFILE HINT: script.js\nISSUE TYPE: general logic defect\nSALIENT TERMS: click · count · twice"])
    else:
        add_card(s9, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.9), "TEXT ANALYTICS STAGES",
                 ["NFKC Normalization -> Identifier Splitting -> Stop-Word Pruning -> Term Ranking -> Rule Triage"])
    add_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: 09 | TEXT ANALYTICS EXPERIMENT
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "09 | Text Analytics Experiment", "Four Controlled Query Conditions (`devmind-query-v1`)", "Isolating how progressively enriched issue text affects retrieval.")

    q_cards = [
        ("01 · RAW QUERY", "Original bug report exactly as submitted by the user. Preserves verbatim phrasing and syntax."),
        ("02 · NORMALIZED", "NFKC normalization, lowercase conversion, and punctuation standardization. Reduces formatting variation."),
        ("03 · KEYWORDS + IDs", "Adds split camelCase/snake_case identifiers and top-frequency terms. Highlights code-like tokens."),
        ("04 · STRUCTURED", "Category + component hints + extracted identifiers + normalized text. Combines all extracted signals.")
    ]
    for i, (title, desc) in enumerate(q_cards):
        x = Inches(0.8 + (i % 2) * 6.0)
        y = Inches(1.8 + (i // 2) * 2.5)
        add_card(s10, x, y, Inches(5.7), Inches(2.2), title, [desc])
    add_footer(s10, 10)

    # =========================================================================
    # SLIDE 11: 10 | REPOSITORY INDEXING
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "10 | Repository Indexing", "Static Multi-Language Repository Indexing", "Extracting searchable code units and source provenance without executing target files on the host.")

    add_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), "PYTHON: AST-BASED EXTRACTION",
             ["• Parser: Built-in Python `ast.parse`.",
              "• Extracts: Functions, classes and asynchronous definitions.",
              "• Metadata: Relative file path, symbol name, line range, and character count.",
              "• Scope Integrity: Full fidelity to module and class boundaries.",
              "\n• Zero Host Code Execution:", "Target code is never imported; immune to malicious __init__.py scripts."])

    add_card(s11, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.9), "10+ LANGUAGES: LEXICAL SCOPE",
             ["• Approach: Brace-depth and lexical scope tracking.",
              "• Languages: JavaScript, TypeScript, Java, C/C++, Go, Rust, C#, Ruby, PHP, Kotlin, Swift.",
              "• Inline Web Scripts: Extracts `<script>` blocks embedded in HTML/HTM templates.",
              "• Granularity: Function and class-like chunks with start/end lines.",
              "\n• Known Boundary:", "Lexical parsing is not a full compiler front-end; edge cases can be missed."])
    add_footer(s11, 11)

    # =========================================================================
    # SLIDE 12: 11 | RETRIEVAL COMPARISON
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "11 | Retrieval Comparison", "Why Compare Sparse, Dense and Hybrid Retrieval?", "Source code contains exact identifiers as well as conceptual descriptions; no single signal dominates.")

    add_card(s12, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "TF-IDF / SPARSE COSINE",
             ["• Signal: Weighted lexical term overlap.",
              "• Strength: Exact identifiers and rare code tokens (e.g. `matchState.balls`).",
              "• Cost: Lightweight index construction and microsecond retrieval.",
              "• Role: Strong baseline with highest pilot recall."])

    add_card(s12, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9), "BM25 / LEXICAL RANKING",
             ["• Signal: Probabilistic term frequency, IDF, and document length normalization.",
              "• Strength: Exact words with term saturation (k1=1.5, b=0.75).",
              "• Cost: CPU-friendly sparse inverted index.",
              "• Role: Complements TF-IDF ranking."])

    add_card(s12, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.9), "DENSE / SEMANTIC COSINE",
             ["• Model: `all-MiniLM-L6-v2` (384 dimensions).",
              "• Signal: Semantic proximity in latent embedding space.",
              "• Strength: Captures related concepts despite vocabulary differences.",
              "• Cost: High embedding build time and RAM overhead."])
    add_footer(s12, 12)

    # =========================================================================
    # SLIDE 13: 12 | RANK FUSION (RRF)
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "12 | Rank Fusion", "Reciprocal Rank Fusion (RRF) Formulation", "Combining rankings without assuming BM25 scores and cosine similarities share the same numerical scale.")

    add_card(s13, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), "MATHEMATICAL FORMULATION",
             ["Formula:",
              "    RRF(d) = Σ_{m}  1 / ( k + rank_m(d) )",
              "\n• Project Setting: k = 60 (standard IR constant).",
              "• Inputs: Ranked candidate lists from two or more retrieval methods.",
              "• Fusion Logic: Higher-ranked appearances contribute more; avoids score distortion.",
              "• Output: Single unified candidate ordering for Top-5 context assembly."])

    add_card(s13, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.9), "ILLUSTRATIVE RANKING EXAMPLE",
             ["Candidate A:",
              "  • TF-IDF rank: 1  -->  1 / (60 + 1) = 0.01639",
              "  • BM25 rank: 3    -->  1 / (60 + 3) = 0.01587",
              "  • Combined RRF = 0.03226 (Ranks #1 overall)",
              "\nCandidate B:",
              "  • TF-IDF rank: 4  -->  1 / (60 + 4) = 0.01562",
              "  • BM25 rank: 1    -->  1 / (60 + 1) = 0.01639",
              "  • Combined RRF = 0.03201",
              "\nObservation: Rewards items ranking high across both signals."])
    add_footer(s13, 13)

    # =========================================================================
    # SLIDE 14: 13 | DATASET (SWE-bench Pilot)
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "13 | Evaluation Dataset", "Five Pinned SWE-bench Lite Development Instances", "Real GitHub repository snapshots; relevance represented by changed-file proxy labels.")

    headers_d = ["Repository", "Base Commit (SHA)", "Indexed Chunks", "Changed-File Proxy"]
    rows_d = [
        ["marshmallow-code/marshmallow", "2be2d83a", "1,455", "src/marshmallow/schema.py"],
        ["pvlib/pvlib-python", "04a523fa", "1,233", "pvlib/temperature.py"],
        ["pydicom/pydicom", "b9fb05c1", "2,156", "pydicom/valuerep.py"],
        ["pylint-dev/astroid", "39c2a980", "3,162", "astroid/nodes/node_classes.py"],
        ["sqlfluff/sqlfluff", "304a1978", "1,618", "src/sqlfluff/core/parser/helpers.py"]
    ]
    add_table_shape(s14, Inches(0.8), Inches(1.8), Inches(11.733), Inches(3.2), headers_d, rows_d)

    add_card(s14, Inches(0.8), Inches(5.2), Inches(5.6), Inches(1.6), "LABEL QUALITY",
             ["One changed-file proxy per issue; no independent human-reviewed fault locations. Excludes fixing patches from retrieval."])
    add_card(s14, Inches(6.8), Inches(5.2), Inches(5.6), Inches(1.6), "EXCLUSION RECORD",
             ["PyVista candidate was excluded before indexing because its pinned archive exceeded the 100 MiB intake limit."])
    add_footer(s14, 14)

    # =========================================================================
    # SLIDE 15: 14 | EXPERIMENTAL DESIGN
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "14 | Experimental Design", "Paired Retrieval Evaluation Protocol", "Five issues evaluated under 4 query conditions and 5 retrieval strategies with Top-5 ranking.")

    fig6_path = FIG_DIR / "fig6_evaluation_protocol.png"
    if fig6_path.exists():
        s15.shapes.add_picture(str(fig6_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))
        add_card(s15, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.9), "PROTOCOL SUMMARY",
                 ["• 5 Repositories / Instances",
                  "• 4 Query Variants:", "  Raw · Normalized · Keywords/IDs · Structured",
                  "• 5 Retrieval Methods:", "  TF-IDF · BM25 · Dense · 2 Fusion setups",
                  "• 100 Completed Records (5 × 4 × 5)",
                  "\n• Metrics Recorded:", "  Precision@1 / Precision@5\n  Recall@5\n  Mean Reciprocal Rank (MRR)\n  nDCG@5\n  Index build time · Latency · Memory",
                  "\n• Reproducibility:", "  Pinned SHAs & SHA-256 digests."])
    else:
        add_card(s15, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.9), "PROTOCOL", ["100 completed runs"])
    add_footer(s15, 15)

    # =========================================================================
    # SLIDE 16: 15 | RESULTS (Raw Query Retrieval)
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "15 | Results", "Retrieval Results on Raw Issue Queries", "Mean values over five evaluation instances; best overall row is Lexical TF-IDF + BM25 RRF.")

    headers_r = ["Retrieval Method", "P@1", "P@5", "R@5", "MRR", "nDCG@5"]
    rows_r = [
        ["TF-IDF cosine", "0.400", "0.160", "0.800", "0.550", "0.612"],
        ["BM25 Okapi", "0.400", "0.160", "0.800", "0.517", "0.586"],
        ["Hybrid lexical RRF", "0.600", "0.160", "0.800", "0.667", "0.700"],
        ["Dense cosine", "0.400", "0.080", "0.400", "0.400", "0.400"],
        ["Hybrid lexical-semantic RRF", "0.400", "0.120", "0.600", "0.440", "0.477"]
    ]
    add_table_shape(s16, Inches(0.8), Inches(1.8), Inches(11.733), Inches(3.2), headers_r, rows_r)

    add_card(s16, Inches(0.8), Inches(5.2), Inches(5.6), Inches(1.6), "BEST OVERALL RANKING",
             ["Lexical RRF (TF-IDF + BM25): P@1 0.600 · MRR 0.667 · nDCG@5 0.700. Moves the relevant file to rank 1 more frequently."])
    add_card(s16, Inches(6.8), Inches(5.2), Inches(5.6), Inches(1.6), "PILOT INTERPRETATION",
             ["Sparse retrieval beat dense cosine on this small proxy sample (Recall@5 = 0.800 vs 0.400) due to exact code token matches."])
    add_footer(s16, 16)

    # =========================================================================
    # SLIDE 17: 16 | RQ1: QUERY ENRICHMENT
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "16 | RQ1: Query Enrichment", "What Changed When Issue Text Was Enriched?", "Identifier extraction and structured hints produced a modest but measurable improvement for TF-IDF.")

    headers_q = ["Query Condition", "P@1", "P@5", "R@5", "MRR", "nDCG@5"]
    rows_q = [
        ["Raw Query", "0.400", "0.160", "0.800", "0.550", "0.612"],
        ["Normalized Query", "0.400", "0.160", "0.800", "0.550", "0.612"],
        ["Keywords / Identifiers", "0.400", "0.160", "0.800", "0.567", "0.626"],
        ["Structured Query", "0.400", "0.160", "0.800", "0.567", "0.626"]
    ]
    add_table_shape(s17, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.8), headers_q, rows_q)

    add_card(s17, Inches(0.8), Inches(4.8), Inches(11.733), Inches(2.0), "EMPIRICAL OBSERVATION",
             ["• Raw --> Keyword / Identifier Query:", "  MRR gained +0.017 (0.550 -> 0.567)  |  nDCG@5 gained +0.014 (0.612 -> 0.626).",
              "\n• Normalized Text Alone:", "  Produced identical aggregate scores as raw text; cleaning whitespace alone does not alter ranking.",
              "\n• Academic Framing:", "  The gain is modest; this pilot supports further research rather than a sweeping performance claim."])
    add_footer(s17, 17)

    # =========================================================================
    # SLIDE 18: 17 | COMPUTATIONAL COST
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18)
    add_header(s18, "17 | Computational Cost", "Retrieval Quality Must Be Read with Indexing Cost", "Dense embedding construction was substantially more expensive in the tested CPU environment.")

    add_card(s18, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "INDEX BUILD TIME",
             ["• Sparse TF-IDF:", "1.199 seconds total",
              "\n• Dense Embeddings:", "594.737 seconds (~10 min)",
              "\n• Speedup Factor:", "496x TF-IDF indexing speed advantage across 5 repositories.",
              "\n• Practical Impact:", "Instant startup for CLI/IDE developer workflows."])

    add_card(s18, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9), "PEAK MEMORY (RSS)",
             ["• Sampled Memory Profile:", "932.89 MiB peak process-tree RSS during dense encoding.",
              "\n• Sampling Rate:", "Sampled every 25 ms over 7,901 samples.",
              "\n• Sparse Footprint:", "Operates in lightweight memory (<50 MiB)."])

    add_card(s18, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.9), "QUERY LATENCY",
             ["• TF-IDF Cosine:", "Mean: 0.0362 s",
              "\n• Dense Cosine:", "Mean: 0.0622 s",
              "\n• Hybrid Semantic RRF:", "Mean: 0.1738 s",
              "\n• Takeaway:", "Measure runtime latency alongside retrieval quality."])
    add_footer(s18, 18)

    # =========================================================================
    # SLIDE 19: 18 | REPAIR AUDIT
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    set_slide_background(s19)
    add_header(s19, "18 | Repair Audit", "What Happened in the Live LLM Repair Attempt?", "The Qwen model localized the relevant logic, but its patch did not pass deterministic validation.")

    add_card(s19, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), "CRICKET SCORER PRO  |  AUDIT",
             ["• Target Defect:", "One legal delivery increments batsman ball counter twice (`balls += 2`).",
              "\n• Configured Model:", "`qwen3:1.7b` via local Ollama endpoint (response time: ~120.51s).",
              "\n• Model Behavior:", "Correctly identified `matchState.balls` and suggested changing `+2` to `+1`.",
              "\n• The Failure Mode:", "Output omitted standard diff edit markers (`+` or `-`), generating plain text.",
              "\n• System Action:", "Validator halted process as a no-op; container tests were NOT executed."])

    add_card(s19, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.9), "VERIFICATION STATUS: BLOCKED",
             ["• What It Establishes:", "Evidence that the model was invoked and that malformed output was safely blocked.",
              "\n• What It Does NOT Establish:", "It is NOT evidence of an end-to-end model-generated repair.",
              "\n• Defensible Positioning:", "The validator successfully prevented an invalid edit from reaching the sandbox.",
              "\n• Separate Disk Fix:", "All 4 double-increment sites were fixed on disk and verified with `node --test` (1 passed in 3.9ms)."])
    add_footer(s19, 19)

    # =========================================================================
    # SLIDE 20: 19 | PATCH INTEGRITY
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    set_slide_background(s20)
    add_header(s20, "19 | Patch Integrity", "A Deterministic Gate Checks Model-Generated Diffs", "The validator rejects unsafe or malformed changes before they reach the test environment.")

    fig4_path = FIG_DIR / "fig4_patch_validation.png"
    if fig4_path.exists():
        s20.shapes.add_picture(str(fig4_path), Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9))
        add_card(s20, Inches(8.6), Inches(1.8), Inches(3.9), Inches(4.9), "4 INTEGRITY GATES",
                 ["01 · PATH CONTAINMENT\nReject absolute paths and directory traversal (../)\n\n02 · DIFF STRUCTURE\nRequire standard --- a/ and +++ b/ headers\n\n03 · HUNK NORMALIZATION\nRecalculate line offsets and hunk counts\n\n04 · NO-OP REJECTION\nReject empty changes that alter zero source"])
    else:
        add_card(s20, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.9), "GATES", ["4 diff validation gates"])
    add_footer(s20, 20)

    # =========================================================================
    # SLIDE 21: 20 | SANDBOXED VERIFICATION
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    set_slide_background(s21)
    add_header(s21, "20 | Sandboxed Verification", "Test Candidate Patches Away from Host Workspace", "Docker smoke tests verified restricted execution and candidate-test mechanics on controlled fixtures.")

    add_card(s21, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "CONTAINER CONTROLS",
             ["• UID / GID: 10001 : 10001 (Non-root)",
              "• Network: None (Air-gapped)",
              "• Capabilities: All dropped (`--cap-drop ALL`)",
              "• Root Filesystem: Read-only",
              "• Temporary Storage: Ephemeral tmpfs",
              "• Log Window: Bounded 4,000 chars",
              "\n• Host Repo Hash:", "100% byte-identical before and after."])

    add_card(s21, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9), "CONTROLLED FIXTURES",
             ["• QuickCart Fixture:", "Baseline failed; candidate passed 1/1 Node tests. Synthetic fixture with deterministic provider.",
              "\n• Safe-Divide Fixture:", "Baseline failed on zero-division; candidate passed 2/2 pytest tests in Docker.",
              "\n• Cricket Scorer:", "Fixed on disk and verified with `node --test` (1 passed in 3.9ms)."])

    add_card(s21, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.9), "SAFETY BOUNDARY",
             ["• Strong Isolation:", "Container isolation protects developer machines from untrusted repository code.",
              "\n• Academic Rigor:", "These fixtures demonstrate sandbox mechanics; they must NOT be described as successful live-model repairs.",
              "\n• Human Gate:", "Mandatory developer review before any patch merge."])
    add_footer(s21, 21)

    # =========================================================================
    # SLIDE 22: 21 | DEVELOPER EXPERIENCE
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    set_slide_background(s22)
    add_header(s22, "21 | Developer Experience", "A Compact Interface for Inspecting a Repair Run", "Streamlit cockpit and browser extension make repository intake, execution status and evidence inspectable.")

    add_card(s22, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3), "LIVE REPAIR WORKSPACE",
             ["• Issue input & repository selection (local folder or GitHub URL).",
              "• Real-time 6-stage visual pipeline progress.",
              "• Evidence cards with cosine similarity bar chart.",
              "• Candidate diff viewer and test log inspector."])

    add_card(s22, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.3), "PERFORMANCE & HISTORY",
             ["• Aggregate KPIs across saved audit runs.",
              "• Project-by-project breakdown cards.",
              "• Pass rate tracking and execution timing.",
              "• Full JSON audit report download."])

    add_card(s22, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.4), "PARAMETER GUIDE & VIVA",
             ["• Card-by-card reference for every UI parameter.",
              "• Technical definitions and viva talking points.",
              "• Educates users on RAG, RRF, and Docker sandboxing."])

    add_card(s22, Inches(6.8), Inches(4.3), Inches(5.6), Inches(2.4), "MANIFEST V3 BRAVE EXTENSION",
             ["• Reads GitHub repository tab URL with 1 click.",
              "• Passes URL to DevMind via `?repo=` parameter.",
              "• 3 Node service-worker tests passed.",
              "• An intake aid; does not auto-merge code."])
    add_footer(s22, 22)

    # =========================================================================
    # SLIDE 23: 22 | SOFTWARE QUALITY
    # =========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    set_slide_background(s23)
    add_header(s23, "22 | Software Quality", "Automated Tests Cover All Engineering Subsystems", "The latest recorded Python test run completed on 18 November 2026.")

    add_card(s23, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "OVERALL TEST RESULTS",
             ["• 179 Pytest Passed (4.93s duration)",
              "• 3 Pytest Skipped (Windows symlink permissions)",
              "• 3 Node.js Tests Passed (Brave extension worker)",
              "\n• Execution Date:", "18 November 2026",
              "\n• Test Pass Rate:", "100% among runnable tests."])

    headers_t = ["Subsystem Suite", "Tests Passed", "Key Responsibility"]
    rows_t = [
        ["Task Analyzer", "16", "NFKC, tokenize, camel/snake split, triage"],
        ["Multilanguage Indexer", "12", "Python AST & lexical brace parsing"],
        ["Retriever & RRF", "18", "TF-IDF, BM25, and rank fusion k=60"],
        ["Dense Embeddings", "8", "MiniLM adapter and NumPy cosine space"],
        ["Diff Validator", "18", "Header, line offset recalculation, path guard"],
        ["Docker Sandbox", "22", "UID 10001, net none, tmpfs, 4000-char tail"],
        ["Orchestrator & Retries", "25", "Baseline tests, 3-attempt feedback loop"],
        ["Stats, PR & Guide", "44", "KPIs, Markdown PR drafts, parameter guide"],
        ["Extension Worker", "3", "GitHub tab URL extraction and prefill"]
    ]
    add_table_shape(s23, Inches(4.8), Inches(1.8), Inches(7.733), Inches(4.9), headers_t, rows_t)
    add_footer(s23, 23)

    # =========================================================================
    # SLIDE 24: 23 | DISCUSSION
    # =========================================================================
    s24 = prs.slides.add_slide(blank_layout)
    set_slide_background(s24)
    add_header(s24, "23 | Discussion", "What the Empirical Pilot Suggests", "Three findings connect the Text Analytics pipeline to practical repository search and repair.")

    add_card(s24, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.9), "1 · IDENTIFIERS MATTER",
             ["• Observation:", "TF-IDF and BM25 found proxy files more often than dense cosine.",
              "\n• Why It Happens:", "Source code relies heavily on exact identifier tokens (`matchState.balls`), which dense vectors blur into generic semantic clusters.",
              "\n• Caution:", "Five cases are not enough to generalize across all repositories."])

    add_card(s24, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.9), "2 · COST IS PART OF QUALITY",
             ["• Observation:", "Dense indexing took 594.737 s versus 1.199 s for TF-IDF.",
              "\n• Implication:", "Resource and energy cost matter for real-world local developer tools (496x speedup).",
              "\n• Caution:", "Difference is specific to this CPU setup and corpus."])

    add_card(s24, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.9), "3 · SAFE REFUSAL IS VITAL",
             ["• Observation:", "Live LLM attempt produced a malformed diff.",
              "\n• System Action:", "Validator rejected it before test execution.",
              "\n• Implication:", "Safe refusal and reporting are far better than applying a broken patch to user code.",
              "\n• Strongest Result:", "Retrieval and safety evaluation, not autonomous repair."])
    add_footer(s24, 24)

    # =========================================================================
    # SLIDE 25: 24 | LIMITATIONS
    # =========================================================================
    s25 = prs.slides.add_slide(blank_layout)
    set_slide_background(s25)
    add_header(s25, "24 | Limitations", "What the Current Evidence Does Not Establish", "Transparent boundaries for interpreting project results accurately.")

    add_card(s25, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3), "PILOT SCALE & PROXIES",
             ["• Only 5 SWE-bench Lite development issues were evaluated.",
              "• Changed-file proxies are not manually verified function-level fault locations."])

    add_card(s25, Inches(6.8), Inches(1.8), Inches(5.6), Inches(2.3), "LIVE LLM REPAIR BOUNDARY",
             ["• The audited Qwen patch was rejected due to missing diff markers.",
              "• Full live-model repair success is not yet demonstrated end-to-end."])

    add_card(s25, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.4), "SANDBOX SECURITY PROOF",
             ["• Docker restrictions reduce risk significantly (UID 10001, net off).",
              "• Does not constitute a formal cryptographic hypervisor security proof."])

    add_card(s25, Inches(6.8), Inches(4.3), Inches(5.6), Inches(2.4), "NO LEADERBOARD CLAIM",
             ["• No official full SWE-bench or SWE-bench Lite leaderboard score is claimed.",
              "• DevMind is an auditable local research prototype."])
    add_footer(s25, 25)

    # =========================================================================
    # SLIDE 26: 25 | CONCLUSION & NEXT STEPS
    # =========================================================================
    s26 = prs.slides.add_slide(blank_layout)
    set_slide_background(s26)
    add_header(s26, "25 | Conclusion & Next Steps", "A Grounded Foundation for Trustworthy Maintenance", "DevMind demonstrates a measured, auditable workflow and identifies clear next experiments.")

    add_card(s26, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), "WHAT THE PROJECT DELIVERS",
             ["• Text Analytics: Deterministic triage and query enrichment.",
              "• Code Retrieval: Static indexing across 11+ languages; sparse/dense comparison (0.800 Recall@5).",
              "• Patch Integrity: Deterministic diff validation and hunk recalculation.",
              "• Execution Safety: Restricted non-root Docker tests (UID 10001:10001).",
              "• Audit Trail: Evidence spans [E1..En], run history, and human-review status.",
              "\n• Core Takeaway: Value lies in measured retrieval, controlled validation and explicit evidence boundaries."])

    add_card(s26, Inches(6.8), Inches(1.8), Inches(5.6), Inches(4.9), "NEXT RESEARCH STEPS",
             ["• Scale Evaluation: Expand beyond 5 cases and report statistical significance.",
              "• Improve Ground Truth: Obtain blind, human-reviewed function-level fault annotations.",
              "• Strengthen Localization: Test AST call-graph chunking and repository structure.",
              "• Constrain Generation: Enforce grammar-constrained decoding for diff markers.",
              "• Cloud Benchmark: Grade predictions against official SWE-bench harness cluster."])
    add_footer(s26, 26)

    # =========================================================================
    # SLIDE 27: 26 | REFERENCES (Part 1)
    # =========================================================================
    s27 = prs.slides.add_slide(blank_layout)
    set_slide_background(s27)
    add_header(s27, "26 | References", "Selected Research Foundations", "Positioning DevMind within established work on retrieval, repository localization and automated repair.")

    refs1 = [
        "[1] C. E. Jimenez et al., “SWE-bench: Can Language Models Resolve Real-World GitHub Issues?,” ICLR, 2024.",
        "[2] J. Yang et al., “SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering,” NeurIPS, 2024. DOI: 10.52202/079017-1601.",
        "[3] Y. Zhang et al., “AutoCodeRover: Autonomous Program Improvement,” ISSTA, 2024. DOI: 10.1145/3650212.3680384.",
        "[4] C. S. Xia et al., “Demystifying LLM-Based Software Engineering Agents,” Proc. ACM Softw. Eng. (FSE), 2025. DOI: 10.1145/3715754.",
        "[5] I. Bouzenia, P. Devanbu and M. Pradel, “RepairAgent: An Autonomous, LLM-Based Agent for Program Repair,” ICSE, 2025. DOI: 10.1109/ICSE55347.2025.00157."
    ]
    add_card(s27, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.9), "FOUNDATIONAL REPOSITORY APR BENCHMARKS & AGENTS", refs1)
    add_footer(s27, 27)

    # =========================================================================
    # SLIDE 28: 27 | REFERENCES (Part 2)
    # =========================================================================
    s28 = prs.slides.add_slide(blank_layout)
    set_slide_background(s28)
    add_header(s28, "27 | References", "Recent Retrieval and Evidence-Grounded Repair Work", "2026 studies cited as relevant context; preprints explicitly labelled.")

    refs2 = [
        "[6] S. S. Chaudhari et al., “SpIDER: Spatially Informed Dense Embedding Retrieval for Software Issue Localization,” EMNLP, 2026.",
        "[7] R. Gangi Reddy et al., “SWERank: Software Issue Localization with Code Ranking,” ICLR, 2026.",
        "[8] Q. Meng et al., “EviACT: An Evidence-to-Action Framework for Agentic Program Repair,” arXiv:2605.27238, 2026 (preprint).",
        "[9] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” NeurIPS, 2020.",
        "[10] S. Robertson and H. Zaragoza, “The Probabilistic Relevance Framework: BM25 and Beyond,” Found. Trends Inf. Retr., 2009.",
        "[11] G. V. Cormack, C. L. A. Clarke and S. Buettcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” SIGIR, 2009."
    ]
    add_card(s28, Inches(0.8), Inches(1.8), Inches(11.733), Inches(4.9), "RETRIEVAL, RANK FUSION & EVIDENCE GATES", refs2)
    add_footer(s28, 28)

    # =========================================================================
    # SLIDE 29: DISCUSSION (Q&A)
    # =========================================================================
    s29 = prs.slides.add_slide(blank_layout)
    set_slide_background(s29)

    box_end = s29.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(4.2))
    tf_end = box_end.text_frame
    tf_end.word_wrap = True

    pe0 = tf_end.paragraphs[0]
    pe0.text = "THANK YOU"
    pe0.font.name = 'Arial'
    pe0.font.size = Pt(44)
    pe0.font.bold = True
    pe0.font.color.rgb = TEXT_WHITE
    pe0.alignment = PP_ALIGN.CENTER
    pe0.space_after = Pt(12)

    pe1 = tf_end.add_paragraph()
    pe1.text = "Questions & Discussion"
    pe1.font.name = 'Arial'
    pe1.font.size = Pt(22)
    pe1.font.bold = True
    pe1.font.color.rgb = ACCENT_CYAN
    pe1.alignment = PP_ALIGN.CENTER
    pe1.space_after = Pt(20)

    pe2 = tf_end.add_paragraph()
    pe2.text = "DevMind: Evidence-Grounded Bug Analysis, Repository Localization & Sandboxed Repair\n" \
               "Project Team: P. Sharath Chandhra  ·  B. Shashank Manohar  ·  K. Venkat Sai Mani Avinash\n" \
               "Department of Computer Science & Engineering  ·  Amrita Vishwa Vidyapeetham  ·  Amritapuri"
    pe2.font.name = 'Arial'
    pe2.font.size = Pt(12.5)
    pe2.font.color.rgb = TEXT_LIGHT
    pe2.alignment = PP_ALIGN.CENTER

    add_footer(s29, 29)

    out_file = "DevMind_Presentation.pptx"
    prs.save(out_file)
    print(f"Successfully generated {out_file} with {len(prs.slides)} slides!")

if __name__ == '__main__':
    build_presentation()
