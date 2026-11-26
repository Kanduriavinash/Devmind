"""
Generate all 7 publication-quality diagrams for the DevMind research paper.
Output: PNG files in reports/devmind-report-draft/figures/ at 300 DPI.
"""
import os
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_DIR = Path("reports/devmind-report-draft/figures")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Academic Color Palette
COLOR_EDGE = "#2B3A4A"
COLOR_FILL_MAIN = "#EEF4F8"
COLOR_FILL_OPT = "#FFF8E7"
COLOR_EDGE_OPT = "#8C6D1F"
COLOR_ARROW = "#485A6C"
COLOR_TEXT_MAIN = "#152232"
COLOR_TEXT_MUTED = "#3D4F63"
COLOR_ACCENT = "#1D6F8A"

def add_box(ax, xy, size, title, detail, *, optional=False, accent=False, fontsize_t=9.2, fontsize_d=7.6):
    x, y = xy
    w, h = size
    face = "#E0F2FE" if accent else (COLOR_FILL_OPT if optional else COLOR_FILL_MAIN)
    edge = COLOR_ACCENT if accent else (COLOR_EDGE_OPT if optional else COLOR_EDGE)
    ls = "--" if optional else "-"
    
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.015,rounding_size=0.03",
        linewidth=1.3,
        edgecolor=edge,
        facecolor=face,
        linestyle=ls,
    )
    ax.add_patch(box)
    
    # Text
    if detail:
        ax.text(x + w / 2, y + h * 0.65, title, ha="center", va="center",
                fontsize=fontsize_t, weight="bold", color=COLOR_TEXT_MAIN, wrap=True)
        ax.text(x + w / 2, y + h * 0.30, detail, ha="center", va="center",
                fontsize=fontsize_d, color=COLOR_TEXT_MUTED, wrap=True)
    else:
        ax.text(x + w / 2, y + h * 0.50, title, ha="center", va="center",
                fontsize=fontsize_t, weight="bold", color=COLOR_TEXT_MAIN, wrap=True)

def add_arrow(ax, start, end, *, dashed=False, rad=0, label=""):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12, linewidth=1.2,
        color=COLOR_ARROW, linestyle="--" if dashed else "-",
        connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1,
    ))
    if label:
        mx = (start[0] + end[0]) / 2
        my = (start[1] + end[1]) / 2 + 0.03
        ax.text(mx, my, label, ha="center", va="center", fontsize=7.2, color=COLOR_TEXT_MUTED, weight="bold")

# ==============================================================================
# FIG 1: Overall DevMind Architecture
# ==============================================================================
def make_fig1():
    fig, ax = plt.subplots(figsize=(11, 4.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    ax.text(0.5, 0.94, "DevMind Overall System Architecture",
            ha="center", va="center", fontsize=12.5, weight="bold", color=COLOR_TEXT_MAIN)
    
    add_box(ax, (0.02, 0.48), (0.13, 0.26), "Input Artifacts", "Bug report text +\nRepository snapshot")
    add_box(ax, (0.18, 0.65), (0.15, 0.21), "Task Analyzer", "NFKC, tokenize, camel/snake\nsplit, rule categories")
    add_box(ax, (0.18, 0.32), (0.15, 0.21), "Static Indexer", "Python AST + Lexical\nbrace scope parsing")
    add_box(ax, (0.36, 0.48), (0.15, 0.26), "Hybrid Retrieval", "TF-IDF / BM25 +\nSentence-MiniLM RRF")
    add_box(ax, (0.54, 0.48), (0.14, 0.26), "Patch Proposal", "Local open-weights LLM\n(Ollama / Qwen)", optional=True)
    add_box(ax, (0.71, 0.48), (0.13, 0.26), "Diff Validator", "Header check, line offset\nrecalc, path traversal check")
    add_box(ax, (0.87, 0.48), (0.11, 0.26), "Docker Sandbox", "Non-root UID 10001,\n--network none, tmpfs", optional=True)
    
    # Arrows
    add_arrow(ax, (0.15, 0.62), (0.18, 0.74))
    add_arrow(ax, (0.15, 0.58), (0.18, 0.44))
    add_arrow(ax, (0.33, 0.74), (0.36, 0.64))
    add_arrow(ax, (0.33, 0.44), (0.36, 0.58))
    add_arrow(ax, (0.51, 0.61), (0.54, 0.61))
    add_arrow(ax, (0.68, 0.61), (0.71, 0.61))
    add_arrow(ax, (0.84, 0.61), (0.87, 0.61))
    
    # Report box
    add_box(ax, (0.30, 0.10), (0.42, 0.18), "Evidence-Grounded Inspection & Report",
            "Retrieved locations • Candidate diff • Sandbox logs • PR draft export", accent=True)
    add_arrow(ax, (0.435, 0.48), (0.435, 0.28))
    add_arrow(ax, (0.925, 0.48), (0.72, 0.24), rad=-0.08)
    
    fig.savefig(OUT_DIR / "fig1_overall_architecture.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created fig1_overall_architecture.png")

# ==============================================================================
# FIG 2: Text Analytics Pipeline
# ==============================================================================
def make_fig2():
    fig, ax = plt.subplots(figsize=(10.5, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    ax.text(0.5, 0.93, "Deterministic Text Analytics & Query Enrichment Pipeline",
            ha="center", va="center", fontsize=12, weight="bold", color=COLOR_TEXT_MAIN)
            
    steps = [
        (0.02, "Raw Bug Report", "User symptom text\nor error trace"),
        (0.18, "Unicode NFKC Clean", "Normalize quotes,\nhyphens, spaces"),
        (0.34, "Identifier Splitting", "camelCase -> ['camel', 'Case']\nsnake_case -> ['snake', 'case']"),
        (0.50, "Stop-Word Prune", "Remove conversational\nfiller & query noise"),
        (0.66, "Frequency & Hints", "Rank Top-10 terms;\nfile/extension regex"),
        (0.82, "Rule-Based Triage", "Assign category:\nType, Syntax, Regression")
    ]
    w, h, y = 0.14, 0.40, 0.38
    for x, t, d in steps:
        add_box(ax, (x, y), (w, h), t, d, fontsize_t=8.6, fontsize_d=7.0)
    for i in range(len(steps) - 1):
        add_arrow(ax, (steps[i][0] + w, y + h / 2), (steps[i + 1][0], y + h / 2))
        
    add_box(ax, (0.28, 0.08), (0.44, 0.18), "Enriched Structured Query q*",
            "[Category] + [Component Hints] + [Extracted Tokens] + [Clean Text]", accent=True)
    add_arrow(ax, (0.89, 0.38), (0.72, 0.22), rad=-0.05)
    
    fig.savefig(OUT_DIR / "fig2_text_analytics.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created fig2_text_analytics.png")

# ==============================================================================
# FIG 3: Repository Indexing and Retrieval
# ==============================================================================
def make_fig3():
    fig, ax = plt.subplots(figsize=(10.8, 4.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    ax.text(0.5, 0.94, "Repository Indexing and Two-Stage Hybrid Retrieval",
            ha="center", va="center", fontsize=12, weight="bold", color=COLOR_TEXT_MAIN)
            
    add_box(ax, (0.02, 0.46), (0.14, 0.30), "Repository Files", "11+ Languages (Python,\nJS/TS, Java, C++, Go, etc.)")
    add_box(ax, (0.19, 0.65), (0.16, 0.22), "Python AST Parser", "ast.parse: functions,\nclasses, async methods")
    add_box(ax, (0.19, 0.33), (0.16, 0.22), "Lexical Scope Parser", "Brace depth tracking;\nHTML inline <script>")
    
    add_arrow(ax, (0.16, 0.63), (0.19, 0.74))
    add_arrow(ax, (0.16, 0.55), (0.19, 0.45))
    
    add_box(ax, (0.38, 0.46), (0.15, 0.30), "Metadata Chunks", "file_path, symbol,\nstart_line, end_line, char_count")
    add_arrow(ax, (0.35, 0.74), (0.38, 0.64))
    add_arrow(ax, (0.35, 0.45), (0.38, 0.56))
    
    # Dual Indexing
    add_box(ax, (0.56, 0.65), (0.18, 0.22), "Sparse TF-IDF / BM25", "Exact identifier match;\nInverted index (1.199s build)")
    add_box(ax, (0.56, 0.33), (0.18, 0.22), "Dense all-MiniLM-L6-v2", "384-d semantic vectors;\nCosine space (594.73s build)")
    add_arrow(ax, (0.53, 0.63), (0.56, 0.74))
    add_arrow(ax, (0.53, 0.55), (0.56, 0.45))
    
    add_box(ax, (0.78, 0.46), (0.20, 0.30), "Reciprocal Rank Fusion", "RRF(d) = sum 1/(60 + rank)\nTop-5 Evidence Spans [E1..E5]", accent=True)
    add_arrow(ax, (0.74, 0.74), (0.78, 0.64))
    add_arrow(ax, (0.74, 0.45), (0.78, 0.56))
    
    fig.savefig(OUT_DIR / "fig3_indexing_retrieval.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created fig3_indexing_retrieval.png")

# ==============================================================================
# FIG 4: Patch Generation and Validation
# ==============================================================================
def make_fig4():
    fig, ax = plt.subplots(figsize=(10.5, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    ax.text(0.5, 0.93, "Patch Generation, Diff Validation, and Security Filtering",
            ha="center", va="center", fontsize=12, weight="bold", color=COLOR_TEXT_MAIN)
            
    nodes = [
        (0.02, "Evidence Clues", "Ranked source spans\n[E1] to [E5] + Issue text"),
        (0.20, "Model Synthesis", "Local Qwen / DeepSeek;\nRequests unified diff"),
        (0.38, "Path Containment", "Rejects absolute paths\n& directory traversal (../)"),
        (0.56, "Header Syntax", "Checks '--- a/' & '+++ b/'\nformat integrity"),
        (0.74, "Hunk Recalculation", "_normalize_hunk_counts:\nRecalculates + and - lines"),
    ]
    w, h, y = 0.15, 0.38, 0.38
    for x, t, d in nodes:
        add_box(ax, (x, y), (w, h), t, d, fontsize_t=8.6, fontsize_d=7.0)
    for i in range(len(nodes) - 1):
        add_arrow(ax, (nodes[i][0] + w, y + h / 2), (nodes[i + 1][0], y + h / 2))
        
    add_box(ax, (0.74, 0.08), (0.24, 0.19), "Empty Patch Rejection", "Discards no-ops before Docker launch", optional=True)
    add_arrow(ax, (0.815, 0.38), (0.815, 0.27))
    
    fig.savefig(OUT_DIR / "fig4_patch_validation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created fig4_patch_validation.png")

# ==============================================================================
# FIG 5: Sandboxed Test Verification
# ==============================================================================
def make_fig5():
    fig, ax = plt.subplots(figsize=(10.8, 4.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    ax.text(0.5, 0.94, "Disposable Non-Root Sandboxed Test Execution",
            ha="center", va="center", fontsize=12, weight="bold", color=COLOR_TEXT_MAIN)
            
    add_box(ax, (0.02, 0.48), (0.16, 0.26), "Validated Patch", "Checked unified diff\noutside source repo")
    add_box(ax, (0.22, 0.45), (0.26, 0.32), "Docker Hardened Container",
            "• Non-root UID/GID: 10001:10001\n• --network none (air-gapped)\n• --cap-drop ALL (no privileges)\n• Read-only root + writable tmpfs",
            optional=True)
    add_arrow(ax, (0.18, 0.61), (0.22, 0.61))
    
    add_box(ax, (0.52, 0.48), (0.18, 0.26), "Targeted Test Execution", "Multi-runner: pytest, node,\nmvn, cargo; 60s timeout")
    add_arrow(ax, (0.48, 0.61), (0.52, 0.61))
    
    add_box(ax, (0.74, 0.48), (0.23, 0.26), "Bounded Streaming Buffer", "Tail-capped to 4,000 chars\nPrevents buffer exhaustion")
    add_arrow(ax, (0.70, 0.61), (0.74, 0.61))
    
    # Retry loop
    add_box(ax, (0.34, 0.10), (0.32, 0.18), "Bounded Retry Orchestrator",
            "Max 3 attempts; feeds sanitized fail log back to LLM", accent=True)
    add_arrow(ax, (0.85, 0.48), (0.66, 0.20), rad=-0.08, label="Fail")
    add_arrow(ax, (0.34, 0.20), (0.10, 0.48), rad=-0.08, label="Retry")
    
    fig.savefig(OUT_DIR / "fig5_sandboxed_verification.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created fig5_sandboxed_verification.png")

# ==============================================================================
# FIG 6: Experimental Evaluation Protocol
# ==============================================================================
def make_fig6():
    fig, ax = plt.subplots(figsize=(10.8, 4.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    ax.text(0.5, 0.93, "Paired Retrieval Evaluation Experimental Protocol",
            ha="center", va="center", fontsize=12, weight="bold", color=COLOR_TEXT_MAIN)
            
    add_box(ax, (0.02, 0.48), (0.18, 0.26), "5 SWE-bench Repos", "marshmallow, pvlib, pydicom,\nastroid, sqlfluff (Pinned SHAs)")
    add_box(ax, (0.24, 0.48), (0.18, 0.26), "4 Query Formulations", "Raw, Normalized,\nKeywords/IDs, Structured")
    add_arrow(ax, (0.20, 0.61), (0.24, 0.61))
    
    add_box(ax, (0.46, 0.48), (0.22, 0.26), "5 Retrieval Methods", "TF-IDF, BM25, Lexical RRF,\nDense MiniLM, Lexical-Semantic")
    add_arrow(ax, (0.42, 0.61), (0.46, 0.61))
    
    add_box(ax, (0.72, 0.48), (0.25, 0.26), "100 Completed Runs", "Top-K=5 evaluation against\nchanged-file proxy labels")
    add_arrow(ax, (0.68, 0.61), (0.72, 0.61))
    
    add_box(ax, (0.24, 0.10), (0.52, 0.18), "Measured Metrics per Run",
            "Precision@1/5 • Recall@5 • MRR • nDCG@5 • Indexing Latency • Memory RSS", accent=True)
    add_arrow(ax, (0.84, 0.48), (0.76, 0.24), rad=-0.05)
    
    fig.savefig(OUT_DIR / "fig6_evaluation_protocol.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created fig6_evaluation_protocol.png")

# ==============================================================================
# FIG 7: Repair Verification and Review Gate
# ==============================================================================
def make_fig7():
    fig, ax = plt.subplots(figsize=(10.5, 3.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    
    ax.text(0.5, 0.93, "Four-Stage Verification and Review Gate Pipeline",
            ha="center", va="center", fontsize=12, weight="bold", color=COLOR_TEXT_MAIN)
            
    gates = [
        (0.02, "Stage 1: Syntactic Validity", "Checks diff header, unified\nformat, line hunk counters"),
        (0.26, "Stage 2: Sandbox Testing", "Executes test runner inside\nephemeral non-root Docker"),
        (0.50, "Stage 3: Review Gate", "Status: tests_passed_\nreview_required (Mandatory)"),
        (0.74, "Stage 4: Benchmark Scale", "Full SWE-bench harness\n(Demarcated as future work)")
    ]
    w, h, y = 0.21, 0.42, 0.36
    for x, t, d in gates:
        add_box(ax, (x, y), (w, h), t, d, fontsize_t=8.8, fontsize_d=7.4, accent=(t.startswith("Stage 3")))
    for i in range(len(gates) - 1):
        add_arrow(ax, (gates[i][0] + w, y + h / 2), (gates[i + 1][0], y + h / 2))
        
    ax.text(0.5, 0.15, "Passing a targeted test is supporting evidence; human developer review remains mandatory.",
            ha="center", va="center", fontsize=8.2, style="italic", color=COLOR_TEXT_MUTED)
            
    fig.savefig(OUT_DIR / "fig7_repair_review_gate.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("Created fig7_repair_review_gate.png")

if __name__ == '__main__':
    make_fig1()
    make_fig2()
    make_fig3()
    make_fig4()
    make_fig5()
    make_fig6()
    make_fig7()
    print("All 7 figures generated successfully!")
