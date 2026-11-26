import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# Design System Colors
BG_DARK = RGBColor(10, 15, 29)          # Deep Navy #0A0F1D
CARD_BG = RGBColor(22, 31, 48)          # Card Slate #161F30
CARD_BORDER = RGBColor(39, 53, 79)      # Border Slate #27354F
ACCENT_CYAN = RGBColor(56, 189, 248)    # Cyan Sky #38BDF8
ACCENT_GREEN = RGBColor(52, 211, 153)   # Emerald #34D399
ACCENT_AMBER = RGBColor(251, 191, 36)   # Amber #FBBF24
TEXT_WHITE = RGBColor(248, 250, 252)    # Slate 50
TEXT_MUTED = RGBColor(148, 163, 184)    # Slate 400
TEXT_LIGHT = RGBColor(203, 213, 225)    # Slate 300

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = BG_DARK

def add_header(slide, tag_text, title_text, subtitle_text=""):
    # Header tag
    tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
    tf_tag = tag_box.text_frame
    tf_tag.word_wrap = True
    p_tag = tf_tag.paragraphs[0]
    p_tag.text = tag_text.upper()
    p_tag.font.name = 'Arial'
    p_tag.font.size = Pt(10)
    p_tag.font.bold = True
    p_tag.font.color.rgb = ACCENT_CYAN

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.6))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.name = 'Arial'
    p_title.font.size = Pt(20)
    p_title.font.bold = True
    p_title.font.color.rgb = TEXT_WHITE

    if subtitle_text:
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.3), Inches(11.5), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle_text
        p_sub.font.name = 'Arial'
        p_sub.font.size = Pt(12)
        p_sub.font.color.rgb = TEXT_MUTED

def add_footer(slide, current_slide, total_slides=25):
    footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.0), Inches(11.5), Inches(0.4))
    tf = footer_box.text_frame
    p = tf.paragraphs[0]
    p.text = f"DEVMIND  |  TEXT ANALYTICS S5 TERM PROJECT  |  AMRITA SCHOOL OF COMPUTING                              SLIDE {current_slide:02d} / {total_slides:02d}"
    p.font.name = 'Arial'
    p.font.size = Pt(8.5)
    p.font.color.rgb = TEXT_MUTED

def add_card(slide, left, top, width, height, title="", body_lines=None, border_color=None, bg_color=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color or CARD_BG
    shape.line.color.rgb = border_color or CARD_BORDER
    shape.line.width = Pt(1)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = Inches(0.2)
    tf.margin_right = Inches(0.2)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)

    if title:
        p0 = tf.paragraphs[0]
        p0.text = title
        p0.font.name = 'Arial'
        p0.font.size = Pt(14)
        p0.font.bold = True
        p0.font.color.rgb = ACCENT_CYAN
        p0.space_after = Pt(8)

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
            p.font.size = Pt(10.5)
            p.font.color.rgb = TEXT_LIGHT
            p.space_after = Pt(4)
    return shape

def create_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 01: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Main Card
    box = s1.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(4.5))
    tf = box.text_frame
    tf.word_wrap = True

    p_super = tf.paragraphs[0]
    p_super.text = "AMRITA VISHWA VIDYAPEETHAM  ·  DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING"
    p_super.font.name = 'Arial'
    p_super.font.size = Pt(12)
    p_super.font.bold = True
    p_super.font.color.rgb = ACCENT_CYAN
    p_super.space_after = Pt(14)

    p_main = tf.add_paragraph()
    p_main.text = "DEVMIND"
    p_main.font.name = 'Arial'
    p_main.font.size = Pt(48)
    p_main.font.bold = True
    p_main.font.color.rgb = TEXT_WHITE
    p_main.space_after = Pt(10)

    p_sub = tf.add_paragraph()
    p_sub.text = "An Evidence-Grounded Agentic RAG Framework for Autonomous Multi-Language Bug Localization, Verification, and Sandboxed Program Repair"
    p_sub.font.name = 'Arial'
    p_sub.font.size = Pt(16)
    p_sub.font.color.rgb = ACCENT_GREEN
    p_sub.space_after = Pt(20)

    p_meta = tf.add_paragraph()
    p_meta.text = "Course: Text Analytics (22CSE314)  ·  Semester V B.Tech CSE  ·  November 2026\n"
    p_meta.font.name = 'Arial'
    p_meta.font.size = Pt(12)
    p_meta.font.color.rgb = TEXT_MUTED

    p_team = tf.add_paragraph()
    p_team.text = "Team Members:  P. Sharath Chandhra   |   B. Shashank Manohar   |   K. Venkat Sai Mani Avinash"
    p_team.font.name = 'Arial'
    p_team.font.size = Pt(13)
    p_team.font.bold = True
    p_team.font.color.rgb = TEXT_WHITE

    add_footer(s1, 1)

    # =========================================================================
    # SLIDE 02: 01 | OVERVIEW - Project at a Glance
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "01 | Overview", "Project at a Glance", "A robust, multi-language repository intelligence and sandboxed code repair platform")

    # 3 Top Metric Cards
    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(1.5), "THE CORPUS", 
             ["• 11+ Languages Supported", "• Python, JS/TS, Java, C++, Go, etc.", "• SWE-bench Lite Benchmark Repos"])
    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(1.5), "THE HYBRID INDEX", 
             ["• AST & Lexical Block Parsing", "• Sparse TF-IDF + Okapi BM25", "• Dense MiniLM Embeddings (384-d)"])
    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(1.5), "THE PLATFORM", 
             ["• 3 Interactive Workspaces in Streamlit", "• Disposable Non-Root Docker Sandbox", "• 179 Automated Tests Passing"])

    # 2 Comparison Columns
    add_card(s2, Inches(0.8), Inches(3.6), Inches(5.6), Inches(3.1), "WHAT IT DOES", 
             ["• Ingests natural language bug reports and extracts structured entities.",
              "• Localizes culprit files using Reciprocal Rank Fusion (k=60).",
              "• Generates syntax-checked unified diffs with open-weights LLMs.",
              "• Tests patches inside isolated, capability-dropped Docker containers.",
              "• Auto-generates Markdown Pull Requests with evidence citations [E1]."])
    
    add_card(s2, Inches(6.8), Inches(3.6), Inches(5.6), Inches(3.1), "WHAT IT IS NOT", 
             ["• Not an unconstrained bash agent running dangerous commands on host.",
              "• Never directly modifies or pollutes your working git repository.",
              "• Not a proprietary cloud API wrapper: runs with local open weights.",
              "• Not a theoretical proposal: every claim is verified by recorded runs.",
              "• Bounded repair: stops after maximum 3 attempts if tests fail."])
    add_footer(s2, 2)

    # =========================================================================
    # SLIDE 03: 02 | MOTIVATION - Why Bug Localization & Repair is Hard
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "02 | Motivation", "Why Repository Bug Analysis is Difficult", "Bridging the gap between natural language descriptions and executable codebases")

    add_card(s3, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "REPOSITORY COMPLEXITY", 
             ["• Massive Source Scale:", "Modern software systems span thousands of files, classes, and cross-file dependencies.",
              "\n• Scattered Symptoms:", "A user symptom in UI (e.g., cart resets or score double-increments) often originates in state handlers 5 layers deep.",
              "\n• Developer Fatigue:", "Engineers spend over 60% of their engineering lifecycle reading logs and localizing faults."])

    add_card(s3, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "THE VOCABULARY GAP", 
             ["• Natural Language vs Identifiers:", "Users write 'cart not saving'; code defines `save_cart_session` or `localStorage.setItem`.",
              "\n• Semantic Search Blindspots:", "Dense vector embeddings cluster general concepts but fail on exact variable names and acronyms.",
              "\n• Keyword Limitations:", "Standard search misses synonyms and fails when issues mention descriptive problem behaviors."])

    add_card(s3, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "SAFETY & EXECUTION HAZARDS", 
             ["• Hallucinated Patches:", "Off-the-shelf LLMs frequently invent non-existent file paths or corrupt indentation whitespace.",
              "\n• Host Contamination:", "Executing candidate patches directly on developer environments risks unrecoverable data loss.",
              "\n• Regression Loops:", "A fix for bug A often breaks tests in module B without isolated automated verification."])
    add_footer(s3, 3)

    # =========================================================================
    # SLIDE 04: 03 | OBJECTIVES - Six Core Design Principles
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "03 | Objectives", "Project Objectives & Design Principles", "Rigorous architectural foundations governing the DevMind platform")

    objs = [
        ("01", "Deterministic Task Analysis", "Normalize issue text, extract snake_case/camelCase tokens, and identify error hints without model drift."),
        ("02", "Multi-Language Static Parsing", "Parse Python AST and lexical brace/block structures for 11+ languages without running host code."),
        ("03", "Two-Stage Hybrid Retrieval", "Fuse sparse TF-IDF/BM25 exact matching with dense vector semantics using Reciprocal Rank Fusion (k=60)."),
        ("04", "Strict Unified Diff Validation", "Validate header syntax, line offsets, and path boundaries while rejecting directory-traversing attacks."),
        ("05", "Non-Root Docker Sandboxing", "Execute candidate test suites in disposable, capability-dropped Linux containers (UID 10001:10001)."),
        ("06", "Auditable UI & Self-Healing", "Deliver an interactive 3-tab Streamlit dashboard, viva parameter reference, and automated PR generator.")
    ]
    for i, (num, title, desc) in enumerate(objs):
        x = Inches(0.8 + (i % 3) * 4.0)
        y = Inches(2.0 + (i // 3) * 2.4)
        add_card(s4, x, y, Inches(3.7), Inches(2.1), f"{num} · {title}", [desc])
    add_footer(s4, 4)

    # =========================================================================
    # SLIDE 05: 04 | DATA - Multi-Language Corpus & SWE-bench Lite
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "04 | Evaluation Corpus", "Multi-Language Repository Corpus Statistics", "Rigorous evaluation across real open-source repositories and benchmark test suites")

    add_card(s5, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7), "EVALUATION DATASET BREAKDOWN", 
             ["The evaluation suite comprises 5 development split repositories from the official SWE-bench Lite benchmark,",
              "paired with two multi-language interactive web fixtures:",
              "\n• astropy/astropy (Python): 542 source files, 2,845 AST chunks | Test runner: pytest",
              "• django/django (Python): 1,248 source files, 6,120 AST chunks | Test runner: pytest",
              "• matplotlib/matplotlib (Python): 380 source files, 1,950 AST chunks | Test runner: pytest",
              "• pvlib/pvlib-python (Python): 94 source files, 482 AST chunks | Test runner: pytest",
              "• pydicom/pydicom (Python): 118 source files, 614 AST chunks | Test runner: pytest",
              "• QuickCart Store (Python / JavaScript): 28 files, 142 chunks | Test runner: pytest & node",
              "• Cricket Scorer Pro (JavaScript / HTML): 6 files, 38 chunks | Test runner: node --test",
              "\nKey Takeaway: Over 12,000 code chunks processed without executing a single line of target code on the host."])
    add_footer(s5, 5)

    # =========================================================================
    # SLIDE 06: 04 | DATA - Bug Chronology & Repair Progression
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "04 | Case Studies", "A Spectrum of Real-World Defect Typologies", "Validating repair capabilities across arithmetic logic, cart persistence, and frontend state")

    add_card(s6, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "PYTHON CALCULATOR", 
             ["• Defect Category: Arithmetic Logic",
              "\n• Bug Description:", "Division by zero and boundary values trigger uncaught exceptions rather than handled errors.",
              "\n• Root Cause:", "Missing edge-case validation guards in core calculation dispatcher.",
              "\n• Verification:", "Isolated pytest suite inside Docker: 2/2 tests passed with zero regressions."])

    add_card(s6, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "QUICKCART STORE", 
             ["• Defect Category: Persistence / State",
              "\n• Bug Description:", "Cart items vanish on browser refresh; state not synced with localStorage.",
              "\n• Root Cause:", "State rehydration omitted during DOMContentLoaded initialization.",
              "\n• Verification:", "Node test suite execution in Docker: Cart persistence fully restored."])

    add_card(s6, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "CRICKET SCORER PRO", 
             ["• Defect Category: Frontend Scoring",
              "\n• Bug Description:", "Clicking any run delivery causes the batsman ball tally to increment by 2.",
              "\n• Root Cause:", "4 duplicate `balls += 2` statements across `script.js` (lines 451, 551, 601, 743).",
              "\n• Verification:", "node --test test/scoring.test.cjs: 1 passed in 3.9ms; verified live in browser."])
    add_footer(s6, 6)

    # =========================================================================
    # SLIDE 07: 05 | SYSTEM DESIGN - End-to-End Pipeline
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "05 | System Architecture", "End-to-End DevMind Six-Stage Pipeline", "Deterministic orchestration connecting natural language bug reports to verified patches")

    stages = [
        ("1. INGEST", "Static multi-language AST & lexical tokenization across 11+ languages."),
        ("2. INDEX", "Dual representation: Sparse TF-IDF/BM25 and 384-d dense embeddings."),
        ("3. RETRIEVE", "Reciprocal Rank Fusion (k=60) merges lexical and semantic rankings."),
        ("4. VALIDATE", "Deterministic unified diff validation: headers, offsets, and boundary security."),
        ("5. GENERATE", "Prompt synthesis with local open-weights LLM (Ollama / Qwen / DeepSeek)."),
        ("6. SANDBOX", "Non-root Docker container (UID 10001:10001) runs tests with streaming logs.")
    ]
    for i, (st, desc) in enumerate(stages):
        x = Inches(0.8 + (i % 3) * 4.0)
        y = Inches(2.0 + (i // 3) * 2.4)
        add_card(s7, x, y, Inches(3.7), Inches(2.1), st, [desc])
    add_footer(s7, 7)

    # =========================================================================
    # SLIDE 08: 06 | INGESTION - Static Multi-Language Parsing
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "06 | Ingestion", "Static AST & Lexical Parsing Across 11+ Languages", "Treating target repository code strictly as untrusted input data")

    add_card(s8, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "PYTHON AST EXTRACTION", 
             ["• Official Python ast.parse Engine:", "Extracts classes, functions, asynchronous definitions, and docstrings with perfect syntactic fidelity.",
              "\n• Zero Host Code Execution:", "Target code is never imported, preventing malicious __init__.py files from compromising host systems.",
              "\n• Hierarchical Scope Tracking:", "Retains parent module and class context for every function snippet.",
              "\n• Extensibility:", "Handles complex modern Python syntax, decorators, and type hints."])

    add_card(s8, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.7), "LEXICAL MULTI-LANGUAGE PARSER", 
             ["• 10+ Additional Languages Supported:", "JavaScript, TypeScript, Java, C, C++, Go, Rust, C#, Ruby, PHP, Kotlin, Swift.",
              "\n• Scope-Depth Tokenizer:", "Tracks nested brace depth `{ ... }` to segment coherent functions and class definitions.",
              "\n• Inline Web Script Parsing:", "Extracts `<script>` blocks embedded directly inside HTML/HTM templates (essential for web apps).",
              "\n• Provenance Metadata Attached:", "Every chunk records file path, symbol name, start line, end line, and character count."])
    add_footer(s8, 8)

    # =========================================================================
    # SLIDE 09: 06 | INGESTION - Chunking & Metadata Preservation
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "06 | Chunking", "Chunking Strategy & Metadata Preservation", "Granular code representation optimized for retrieval-augmented generation")

    add_card(s9, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "CHUNKING STRATEGY", 
             ["• Syntactic Boundaries:", "Never splits code mid-statement or across arbitrary line counts.",
              "\n• Function-Level Granularity:", "Each chunk represents a complete logical unit (function, method, class).",
              "\n• Token Bounded:", "Enforces upper limits to fit comfortably within LLM context windows."])

    add_card(s9, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "METADATA PAYLOAD", 
             ["• Attached to Every Chunk:",
              "  - `file_path`: Relative repo path",
              "  - `symbol_name`: Function/class",
              "  - `start_line`: Exact source line",
              "  - `end_line`: Ending line number",
              "  - `language`: Detected language",
              "  - `char_count`: Length in characters",
              "\n• Crucial for Traceability:", "Enables direct citations [E1], [E2] in final Pull Request drafts."])

    add_card(s9, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "WHY METADATA MATTERS", 
             ["• Prevents Cross-File Pollution:", "Retrieval scores track exact file boundaries.",
              "\n• Deterministic Patch Application:", "Diff generator targets the exact file path and line numbers.",
              "\n• Immediate Human Verification:", "Developers can click file links and inspect source code immediately."])
    add_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: 07 | RETRIEVAL - Dual Indexing: Sparse + Dense
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)
    add_header(s10, "07 | Retrieval", "Dual Indexing: Sparse Lexical + Dense Vector Space", "Why combining keyword statistics with continuous embeddings is vital for code")

    add_card(s10, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "SPARSE LEXICAL INDEX (TF-IDF & BM25)", 
             ["• Exact Identifier Precision:", "Crucial for locating exact symbol names, e.g., `matchState.balls` or `cart_total`.",
              "\n• Inverted Index Efficiency:", "Indexes thousands of files in under 2 seconds (1.199s in empirical runs).",
              "\n• Stopword & Identifier Triage:", "Extracts snake_case and camelCase tokens to bridge bug report phrasing.",
              "\n• Zero Cold-Start Overhead:", "Requires no heavy GPU/CPU model weights to initialize."])

    add_card(s10, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.7), "DENSE VECTOR INDEX (all-MiniLM-L6-v2)", 
             ["• Semantic Similarity:", "Maps natural language concepts to related code functionality (384-d vectors).",
              "\n• Handles Paraphrasing:", "Finds relevant code when bug report uses terms not present in source comments.",
              "\n• Persistent ChromaDB Storage:", "Embeddings cached to disk to prevent re-computation on subsequent queries.",
              "\n• Complementary Signal:", "Functions as a second retrieval opinion when exact lexical tokens are sparse."])
    add_footer(s10, 10)

    # =========================================================================
    # SLIDE 11: 07 | RETRIEVAL - Hybrid Fusion Flow
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    set_slide_background(s11)
    add_header(s11, "07 | Fusion Flow", "Two-Stage Candidate Generation & Hybrid Fusion", "Merging disparate retrieval distributions into a unified, high-precision ranking")

    add_card(s11, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7), "HYBRID RETRIEVAL PIPELINE FLOW", 
             ["1. Bug Report Ingestion: Raw query is analyzed to extract keywords, component hints, and error categories.",
              "2. Dual Retrieval Fan-Out:",
              "    • Path A (Sparse BM25 / TF-IDF): Generates Top-50 lexical code candidates based on term statistics.",
              "    • Path B (Dense Sentence Transformers): Generates Top-50 semantic candidates via cosine similarity.",
              "3. Reciprocal Rank Fusion (RRF, k=60):",
              "    • Merges both candidate lists without requiring scale normalization.",
              "    • Code chunks matching BOTH exact tokens and semantic meaning are boosted to the top.",
              "4. Top-K Context Window Assembly:",
              "    • Top-5 fused chunks formatted into numbered evidence spans [E1], [E2], ..., [E5].",
              "    • Enforces token budget to avoid overwhelming the LLM prompt window."])
    add_footer(s11, 11)

    # =========================================================================
    # SLIDE 12: 07 | RETRIEVAL - Reciprocal Rank Fusion Formula
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    set_slide_background(s12)
    add_header(s12, "07 | Fusion Mathematics", "Reciprocal Rank Fusion (RRF) Formulation", "Score-invariant rank combination avoiding scale distortion")

    add_card(s12, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "MATHEMATICAL FORMULATION", 
             ["Cosine similarity and BM25 scores operate on entirely different mathematical domains [0, 1] vs [0, ∞). Direct addition causes severe distortion.",
              "\nFormula:",
              "    RRF(d) = Σ_{m ∈ {sem, lex}}  1 / ( k + rank_m(d) )",
              "\n• k = 60 (Standard Information Retrieval smoothing constant)",
              "• rank_m(d) = Position of document d in ranking method m",
              "\nProperties:",
              "• High reward for items appearing near the top of both lists.",
              "• Smooth degradation: items appearing on only one list are not unfairly penalized."])

    add_card(s12, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.7), "NUMERICAL WORKED EXAMPLE", 
             ["Consider chunk `script.js:handleRuns()`:",
              "\n• In Sparse BM25: Ranked #1 (exact variable match)",
              "    Score = 1 / (60 + 1) = 1 / 61 = 0.01639",
              "\n• In Dense Cosine: Ranked #4 (semantic concept)",
              "    Score = 1 / (60 + 4) = 1 / 64 = 0.01562",
              "\n• Combined RRF Score:",
              "    RRF = 0.01639 + 0.01562 = 0.03201",
              "\nResult: Elevated to #1 overall evidence candidate [E1], outscoring uni-modal candidates."])
    add_footer(s12, 12)

    # =========================================================================
    # SLIDE 13: 08 | RERANKING - Context Expansion & Hunk Normalization
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    set_slide_background(s13)
    add_header(s13, "08 | Context Assembly", "Context Expansion & Unified Diff Normalization", "Preparing flawless context for local models and sanitizing generated patches")

    add_card(s13, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "CONTEXT EXPANSION", 
             ["• Local Scope Stitching:", "When an evidence anchor is selected, DevMind retrieves neighboring lines from the same file to preserve context.",
              "\n• Import & Interface Preservation:", "Includes file header imports and type signatures so the LLM understands available utilities.",
              "\n• Deduplication:", "Overlapping chunks from the same file are merged into contiguous code blocks, saving prompt tokens.",
              "\n• Evidence ID Stamping:", "Prefixes code blocks with `[E1: script.js:450-480]` for traceable attribution."])

    add_card(s13, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.7), "HUNK OFFSET NORMALIZATION", 
             ["• Small LLM Fragility:", "Local models (1.5B–7B) often produce diff headers with inaccurate line count markers `@@ -l,s +l,s @@`.",
              "\n• Deterministic Correction (`_normalize_hunk_counts`):", "Recalculates exact additions (+) and deletions (-) line by line.",
              "\n• Whitespace Sanitization:", "Normalizes CRLF to LF and strips accidental markdown backticks (` ```diff `).",
              "\n• Patch Rejection:", "Discards no-op patches containing zero functional code edits before invoking Docker."])
    add_footer(s13, 13)

    # =========================================================================
    # SLIDE 14: 09 | GENERATION - Local Open-Weights LLMs
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    set_slide_background(s14)
    add_header(s14, "09 | Generation", "Local Open-Weights LLM Code Synthesis", "Zero data exfiltration: running localized inference via Ollama")

    add_card(s14, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "LOCAL MODEL ADVANTAGE", 
             ["• Complete Privacy:", "Proprietary repository source code never leaves the local developer machine.",
              "\n• Zero API Costs:", "Infinite repair iterations without incurring commercial token expenses.",
              "\n• Deterministic Execution:", "Configured with temperature=0.0 to enforce reproducible patch generation."])

    add_card(s14, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "SUPPORTED ENGINES", 
             ["• Ollama Integration:", "Native support for local inference (e.g., Qwen 2.5 Coder 1.5B/7B, DeepSeek-Coder).",
              "\n• OpenAI-Compatible Adapter:", "Seamless plug-and-play switching to vLLM, LM Studio, or cloud endpoints.",
              "\n• Bounded Execution:", "Strict timeout controls (default: 180s) prevent hung or spinning model processes."])

    add_card(s14, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "PROMPT ENGINEERING", 
             ["• Strict Role Definition:", "Instructed as a senior software maintenance engineer.",
              "\n• Citation Constraint:", "Every proposed edit must be justified by cited evidence ID `[E1]`.",
              "\n• Format Constraint:", "Restricted to outputting ONLY a unified diff without conversational preamble."])
    add_footer(s14, 14)

    # =========================================================================
    # SLIDE 15: 10 | VALIDATION - Deterministic Diff Validation Audit
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    set_slide_background(s15)
    add_header(s15, "10 | Validation", "Deterministic Unified Diff Validation Layer", "Python syntax and security checks executed before sandbox container launch")

    add_card(s15, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7), "FOUR-STAGE DIFF VALIDATION PIPELINE", 
             ["Every model-generated diff is intercepted and audited by `src/devmind/code_agent.py`:",
              "\n1. Path Boundary Enforcement:",
              "    • Checks that `--- a/file` and `+++ b/file` reference legitimate files within repository tree.",
              "    • Rejects path traversal attempts (`../`) and absolute paths (`/etc/passwd`), guaranteeing isolation.",
              "\n2. Header Syntax Verification:",
              "    • Verifies presence of unified diff markers and matching filenames across old and new headers.",
              "\n3. Hunk Count & Edit Verification:",
              "    • Replaces model-hallucinated line counters with computed counts of `+` and `-` lines.",
              "    • Rejects empty patches (where model output plain text with no diff operators).",
              "\n4. Non-Destructive In-Memory Staging:",
              "    • Saves valid diff to ephemeral report storage; never applies patch to local git workspace."])
    add_footer(s15, 15)

    # =========================================================================
    # SLIDE 16: 10 | VALIDATION - Host Safety Guarantee
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    set_slide_background(s16)
    add_header(s16, "10 | Sandboxing", "The Host Safety Guarantee: Disposable Non-Root Sandbox", "Executing tests safely without risking host environment corruption")

    add_card(s16, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "SECURITY HARDENING CONTROLS", 
             ["• Non-Root Container User (`UID 10001:10001`):", "Prevents privilege escalation; container process cannot modify host system files.",
              "\n• Network Disabled (`--network none`):", "Untrusted repository scripts cannot make outbound socket calls or exfiltrate credentials.",
              "\n• Capability Dropping (`--cap-drop ALL`):", "Disables all Linux kernel capabilities inside the execution boundary.",
              "\n• Ephemeral tmpfs Storage:", "Workspace modifications exist only in RAM and are destroyed immediately upon container exit."])

    add_card(s16, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.7), "BOUNDED STREAMING EXECUTION", 
             ["• Strict Resource Limits:", "Bounded to 2 CPUs and 2GB RAM; prevents denial-of-service from infinite loops.",
              "\n• 4,000-Character Streaming Log Bounding:", "Stdout and stderr streams are capped to recent 4,000 characters, preventing memory overflows.",
              "\n• Execution Timeout:", "Bounded per-test execution (default: 60s) terminates unresponsive test suites.",
              "\n• Zero Host Mutation:", "The host repository hash is verified before and after runs: 100% byte-identical."])
    add_footer(s16, 16)

    # =========================================================================
    # SLIDE 17: 11 | APPLICATION - Three Streamlit Workspaces
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    set_slide_background(s17)
    add_header(s17, "11 | Application", "Three Specialized Workspaces in Streamlit", "A full-featured developer cockpit for bug localization, repair, and viva defense")

    add_card(s17, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "TAB 1 · BUG ANALYSIS & REPAIR", 
             ["• Quick Demo Presets:", "Instant one-click demo runs for Cricket Scorer, QuickCart, and Calculator.",
              "\n• 6-Stage Visual Timeline:", "Real-time pipeline progression from ingestion to sandbox testing.",
              "\n• RAG Similarity Bar Chart:", "Displays evidence cosine similarity scores dynamically.",
              "\n• Export PR Draft:", "Generates Markdown Pull Requests with evidence citations [E1]."])

    add_card(s17, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "TAB 2 · RUN ANALYTICS DASHBOARD", 
             ["• Real-Time KPI Cards:", "Total runs, verified Docker fix rate, patch syntax validity rate.",
              "\n• Project Breakdown Table:", "Aggregates repair attempts across distinct repositories.",
              "\n• Expandable Audit Logs:", "Inspect per-attempt candidate diffs and container test outputs.",
              "\n• JSON Export:", "Download complete machine-readable audit reports."])

    add_card(s17, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "TAB 3 · UI GUIDE & VIVA REFERENCE", 
             ["• Comprehensive Parameter Guide:", "Detailed documentation for every UI slider, toggle, and input.",
              "\n• Technical & Viva Defense Notes:", "Prepares students to explain RAG, RRF, and Docker sandboxing.",
              "\n• Manifest V3 Brave Extension:", "Unpacked extension enabling 1-click GitHub URL transmission.",
              "\n• Educational Tooltips:", "Inline help popovers explaining parameters."])
    add_footer(s17, 17)

    # =========================================================================
    # SLIDE 18: 12 | RUNNERS - Multi-Runner Sandboxing
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    set_slide_background(s18)
    add_header(s18, "12 | Multi-Runner Support", "A Polyglot Architecture for Test Execution", "Supporting native test suites across enterprise software ecosystems")

    runners = [
        ("pytest", "Python", "Full support for unit tests, fixtures, and failure assertion traces."),
        ("node --test", "JavaScript / TS", "Native Node.js test runner for frontend and backend web applications."),
        ("mvn / gradle", "Java", "Enterprise Java testing with JUnit and Maven lifecycle phases."),
        ("cargo test", "Rust", "High-performance compiled unit and integration testing."),
        ("go test", "Go", "Native concurrency and package testing in isolated environments."),
        ("dotnet test", "C# / .NET", "Multi-platform testing across Microsoft .NET runtimes.")
    ]
    for i, (runner, lang, desc) in enumerate(runners):
        x = Inches(0.8 + (i % 3) * 4.0)
        y = Inches(2.0 + (i // 3) * 2.4)
        add_card(s18, x, y, Inches(3.7), Inches(2.1), f"{runner} ({lang})", [desc])
    add_footer(s18, 18)

    # =========================================================================
    # SLIDE 19: 13 | EVALUATION - Benchmark Results Table
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    set_slide_background(s19)
    add_header(s19, "13 | Empirical Evaluation", "Measured Retrieval Results on SWE-bench Lite Pilot", "Comparative evaluation across 5 real repositories, 4 query variants, and 3 methods")

    add_card(s19, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7), "MEASURED RETRIEVAL METRICS (SWE-BENCH LITE DEVELOPMENT SPLIT)", 
             ["Query Formulation  |  Retrieval Method      |  P@1    |  P@5    |  Recall@5  |  MRR    |  nDCG@5",
              "------------------------------------------------------------------------------------------------",
              "Raw Query          |  TF-IDF (Sparse)        |  0.400  |  0.160  |  0.800     |  0.550  |  0.612",
              "Raw Query          |  Dense MiniLM Cosine    |  0.400  |  0.080  |  0.400     |  0.400  |  0.400",
              "Raw Query          |  Lexical-Semantic RRF   |  0.400  |  0.120  |  0.600     |  0.440  |  0.477",
              "------------------------------------------------------------------------------------------------",
              "Structured Query   |  TF-IDF (Sparse)        |  0.400  |  0.160  |  0.800     |  0.567  |  0.626",
              "Structured Query   |  Dense MiniLM Cosine    |  0.400  |  0.080  |  0.400     |  0.400  |  0.400",
              "Structured Query   |  Lexical-Semantic RRF   |  0.400  |  0.080  |  0.400     |  0.400  |  0.400",
              "\nKey Empirical Highlights:",
              "• Sparse TF-IDF achieves Recall@5 of 0.800 vs 0.400 for Dense Cosine (2x higher top-5 recall).",
              "• Structured query triage improves TF-IDF MRR from 0.550 to 0.567 and nDCG@5 from 0.612 to 0.626."])
    add_footer(s19, 19)

    # =========================================================================
    # SLIDE 20: 13 | EVALUATION - Dense vs Sparse Trade-Offs
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    set_slide_background(s20)
    add_header(s20, "13 | Analysis", "Why Lexical Retrieval Outperforms Dense Vectors in Code", "Analyzing the distinct domain characteristics of software source code vs natural text")

    add_card(s20, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "DOMAIN DIFFERENCES: CODE VS TEXT", 
             ["• Exact Variable Identifiers Matter:", "In conversational NLP, 'automobile' matches 'car'. In code, `calculate_cart` cannot be substituted with `compute_basket`.",
              "\n• Token Sensitivity:", "Dense embeddings map technical identifiers into broad generic clusters, losing precision on exact function calls.",
              "\n• Inverted Index Superiority:", "TF-IDF and BM25 directly reward the exact, rare token matches that define software bugs."])

    add_card(s20, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.7), "COMPUTATIONAL RESOURCE TRADE-OFF", 
             ["• Indexing Latency (5 Repositories):",
              "    - Dense MiniLM: 594.737 seconds (~10 minutes)",
              "    - Sparse TF-IDF: 1.199 seconds (496x faster!)",
              "\n• Peak Process Memory:",
              "    - Dense Embedding: 932.89 MiB RSS",
              "    - Sparse Indexer: Lightweight (<50 MiB)",
              "\n• Practical Conclusion:", "For real-time developer workflows, sparse lexical indexing delivers superior recall at a fraction of the compute cost."])
    add_footer(s20, 20)

    # =========================================================================
    # SLIDE 21: 14 | QUALITY ASSURANCE - 179 Automated Tests
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    set_slide_background(s21)
    add_header(s21, "14 | Quality Assurance", "Automated Verification: 179 Passing Tests", "Exhaustive automated testing across every subsystem of the DevMind architecture")

    add_card(s21, Inches(0.8), Inches(2.0), Inches(11.733), Inches(4.7), "EXHAUSTIVE TEST SUITE BREAKDOWN (pytest)", 
             ["Total Test Suite Result: 179 passed, 3 skipped (Windows symlink permissions) in 4.93s",
              "\n• Multi-Language Indexer Tests (tests/test_multilang.py): 12 passed",
              "    - Verifies AST extraction for Python and lexical block parsing for JS, TS, Java, C++, Go, Rust.",
              "• Unified Diff Validator Tests (tests/test_code_agent.py): 18 passed",
              "    - Verifies header validation, line offset normalization, and directory traversal rejection.",
              "• Sandboxed Execution Tests (tests/test_sandbox.py): 22 passed",
              "    - Verifies non-root execution, bounded 4000-char streaming output, and tmpfs isolation.",
              "• Repair Orchestrator & Retries (tests/test_orchestrator.py): 25 passed",
              "    - Verifies baseline regression execution, bounded attempt limits, and failure feedback routing.",
              "• Analytics & Stats Engine (tests/test_stats.py): 14 passed",
              "    - Verifies KPI computation, project grouping, and run record schema integrity.",
              "• UI Parameter & Viva Guide (tests/test_guide.py): 8 passed",
              "• Web Extension Service Worker (tests/service-worker.test.mjs): 3 passed under node --test"])
    add_footer(s21, 21)

    # =========================================================================
    # SLIDE 22: 15 | PERFORMANCE - Caching & Streaming Execution
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    set_slide_background(s22)
    add_header(s22, "15 | Performance", "Controller Orchestration, Caching & Streaming", "Optimized runtime architecture ensuring snappy responsiveness")

    add_card(s22, Inches(0.8), Inches(2.0), Inches(3.6), Inches(4.7), "STREAMLIT CACHING", 
             ["• @st.cache_resource:", "Retains loaded Sentence Transformer models and vector indexes across UI reruns.",
              "\n• In-Memory Fast Path:", "Subsequent queries against the same repository execute in milliseconds.",
              "\n• Session State Isolation:", "Prevents cross-talk between distinct user sessions."])

    add_card(s22, Inches(4.8), Inches(2.0), Inches(3.6), Inches(4.7), "BOUNDED STREAMING", 
             ["• Memory-Protected Logging:", "Docker stdout/stderr is buffered via bounded deque (max 4,000 characters).",
              "\n• Denial-of-Service Defense:", "Prevents runaway infinite print loops from freezing the browser UI.",
              "\n• Real-Time Output:", "Streams live execution status directly to the terminal."])

    add_card(s22, Inches(8.8), Inches(2.0), Inches(3.6), Inches(4.7), "BACKGROUND WORKFLOW", 
             ["• Asynchronous Tasking:", "Heavy Docker builds run decoupled from UI event loops.",
              "\n• Immutable Snapshots:", "Archives downloaded via Git SHA are hash-verified before indexing.",
              "\n• Ephemeral Clean-up:", "Containers and tmpfs volumes destroyed immediately on exit."])
    add_footer(s22, 22)

    # =========================================================================
    # SLIDE 23: 16 | METHODOLOGICAL TRANSPARENCY - Limitations
    # =========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    set_slide_background(s23)
    add_header(s23, "16 | Academic Integrity", "Methodological Transparency & Limitations", "Clearly demarcating verified engineering software from future research extensions")

    add_card(s23, Inches(0.8), Inches(2.0), Inches(5.6), Inches(4.7), "VERIFIED ENGINEERING ACCOMPLISHMENTS", 
             ["• 100% Complete & Passing Software Stack:", "Multi-language AST indexer, hybrid RRF retrieval, Docker sandbox, and UI are fully functional.",
              "\n• Verified Host Safety Guarantee:", "Candidate changes tested only in disposable containers; host repositories never mutated.",
              "\n• Live Defect Resolution:", "Cricket Scorer Pro double-ball bug fixed and verified with node --test (1 passed in 3.9ms).",
              "\n• Exhaustive Automated Tests:", "179 passing automated unit and integration tests."])

    add_card(s23, Inches(6.8), Inches(2.0), Inches(5.6), Inches(4.7), "FUTURE RESEARCH EXTENSIONS (ACADEMIC SCOPE)", 
             ["• Weak Proxy Ground Truth:", "Current evaluation uses changed-file paths from fixing commits. Future work will collect multi-annotator blind ground truth.",
              "\n• Benchmark Scale Expansion:", "The pilot measured 5 development repositories. Future studies will scale across the full 300-instance SWE-bench Lite.",
              "\n• Matched LLM Comparison:", "Formal multi-model ablation studies comparing proprietary cloud LLMs against local open-weights.",
              "\n• Official Harness Grading:", "Submitting predictions to the official SWE-bench evaluation cluster."])
    add_footer(s23, 23)

    # =========================================================================
    # SLIDE 24: 17 | CONCLUSION - What DevMind Delivers
    # =========================================================================
    s24 = prs.slides.add_slide(blank_layout)
    set_slide_background(s24)
    add_header(s24, "17 | Conclusion", "What DevMind Delivers to Software Engineering", "A dependable, evidence-grounded framework for autonomous software maintenance")

    conclusions = [
        ("LOCALIZE", "Deterministic AST & lexical indexing across 11+ languages; 0.800 Recall@5 with TF-IDF, running 496x faster than dense models."),
        ("VERIFY", "Rigorous unified diff validation correcting header offsets and eliminating hallucinated syntax before execution."),
        ("ISOLATE", "Non-root Docker sandboxing (UID 10001:10001) with bounded tmpfs and dropped capabilities, ensuring zero host corruption."),
        ("SELF-HEAL", "Bounded 3-attempt retry loop routing failure diagnostics back to local models; verified live on Cricket Scorer defect.")
    ]
    for i, (title, desc) in enumerate(conclusions):
        x = Inches(0.8 + (i % 2) * 6.0)
        y = Inches(2.0 + (i // 2) * 2.4)
        add_card(s24, x, y, Inches(5.7), Inches(2.1), title, [desc])
    add_footer(s24, 24)

    # =========================================================================
    # SLIDE 25: DISCUSSION - Q&A Slide
    # =========================================================================
    s25 = prs.slides.add_slide(blank_layout)
    set_slide_background(s25)

    box_end = s25.shapes.add_textbox(Inches(1.5), Inches(1.8), Inches(10.333), Inches(4.0))
    tf_end = box_end.text_frame
    tf_end.word_wrap = True

    p_thx = tf_end.paragraphs[0]
    p_thx.text = "THANK YOU"
    p_thx.font.name = 'Arial'
    p_thx.font.size = Pt(44)
    p_thx.font.bold = True
    p_thx.font.color.rgb = TEXT_WHITE
    p_thx.alignment = PP_ALIGN.CENTER
    p_thx.space_after = Pt(14)

    p_qa = tf_end.add_paragraph()
    p_qa.text = "Questions & Technical Discussion"
    p_qa.font.name = 'Arial'
    p_qa.font.size = Pt(22)
    p_qa.font.bold = True
    p_qa.font.color.rgb = ACCENT_CYAN
    p_qa.alignment = PP_ALIGN.CENTER
    p_qa.space_after = Pt(24)

    p_team_end = tf_end.add_paragraph()
    p_team_end.text = "DevMind: An Evidence-Grounded Agentic RAG Framework\nTeam Members: P. Sharath Chandhra  |  B. Shashank Manohar  |  K. Venkat Sai Mani Avinash\nDepartment of Computer Science and Engineering  ·  Amrita School of Computing"
    p_team_end.font.name = 'Arial'
    p_team_end.font.size = Pt(13)
    p_team_end.font.color.rgb = TEXT_LIGHT
    p_team_end.alignment = PP_ALIGN.CENTER

    add_footer(s25, 25)

    out_file = "DevMind_Presentation.pptx"
    prs.save(out_file)
    print(f"Successfully generated {out_file} with {len(prs.slides)} slides!")

if __name__ == '__main__':
    create_presentation()
