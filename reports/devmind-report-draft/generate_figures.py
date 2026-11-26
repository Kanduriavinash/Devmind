"""Create the original, vector diagrams embedded in the report draft."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


OUT = Path(__file__).parent / "figures"
OUT.mkdir(exist_ok=True)


def node(ax, xy, size, title, detail, *, optional=False):
    x, y = xy
    w, h = size
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.018,rounding_size=0.035",
        linewidth=1.2,
        edgecolor="#45556b" if not optional else "#806629",
        facecolor="#eef3f8" if not optional else "#fff7df",
        linestyle="--" if optional else "-",
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
            fontsize=9.2, weight="bold", color="#172538", wrap=True)
    ax.text(x + w / 2, y + h * 0.31, detail, ha="center", va="center",
            fontsize=7.5, color="#35445a", wrap=True)


def arrow(ax, start, end, *, dashed=False, rad=0):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=12, linewidth=1.25,
        color="#5d6d80", linestyle="--" if dashed else "-",
        connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1,
    ))


def architecture():
    fig, ax = plt.subplots(figsize=(10.8, 4.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(.5, .94, "DevMind local analysis and candidate verification path",
            ha="center", va="center", fontsize=13, weight="bold", color="#172538")
    node(ax, (.025, .49), (.15, .24), "Inputs", "bug report +\nrepository snapshot")
    node(ax, (.235, .67), (.17, .20), "Text analysis", "normalized terms, hints,\nrule-based labels")
    node(ax, (.235, .35), (.17, .20), "Static indexing", "source chunks with\nfile and line spans")
    node(ax, (.475, .51), (.17, .24), "TF--IDF retrieval", "ranked lexical evidence\nfrom issue + code")
    node(ax, (.715, .51), (.13, .24), "Patch proposal", "optional model diff\nwith validation", optional=True)
    node(ax, (.88, .51), (.105, .24), "Docker tests", "disposable copy;\nnetwork off", optional=True)
    arrow(ax, (.175, .63), (.235, .75))
    arrow(ax, (.175, .58), (.235, .46))
    arrow(ax, (.405, .75), (.475, .66))
    arrow(ax, (.405, .45), (.475, .59))
    arrow(ax, (.645, .63), (.715, .63))
    arrow(ax, (.845, .63), (.88, .63))
    node(ax, (.31, .13), (.38, .19), "Evidence-linked run report",
         "retrieved locations • candidate diff • test outcome • review status")
    arrow(ax, (.56, .51), (.56, .32))
    arrow(ax, (.94, .51), (.68, .32), rad=-.08)
    ax.text(.5, .055,
            "The source checkout is not patched. Optional model and Docker stages require local configuration.",
            ha="center", va="center", fontsize=8, color="#49586a")
    fig.savefig(OUT / "devmind-architecture.pdf", bbox_inches="tight")
    plt.close(fig)


def repair_loop():
    fig, ax = plt.subplots(figsize=(10.4, 3.7))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(.5, .94, "Bounded candidate repair and review",
            ha="center", va="center", fontsize=13, weight="bold", color="#172538")
    items = [
        (.04, "Retrieve", "rank code evidence"),
        (.23, "Propose", "optional model diff"),
        (.42, "Validate", "diff and path checks"),
        (.61, "Test", "Docker disposable copy"),
        (.80, "Report", "result + human review"),
    ]
    w, h, y = .155, .24, .54
    for x, title, detail in items:
        node(ax, (x, y), (w, h), title, detail,
             optional=title in {"Propose", "Test"})
    for i in range(len(items) - 1):
        arrow(ax, (items[i][0] + w, y + h / 2), (items[i + 1][0], y + h / 2))
    ax.plot([.685, .685, .31], [.54, .28, .28], color="#806629",
            linewidth=1.2, linestyle="--")
    arrow(ax, (.31, .28), (.31, .54), dashed=True)
    ax.text(.50, .38, "bounded retry on failure, when configured",
            ha="center", va="center", fontsize=8, color="#5a4a22")
    ax.text(.5, .14,
            "A passing selected test suite is evidence for that run; it does not auto-approve or merge a patch.",
            ha="center", va="center", fontsize=8, color="#49586a")
    fig.savefig(OUT / "devmind-repair-workflow.pdf", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    architecture()
    repair_loop()
