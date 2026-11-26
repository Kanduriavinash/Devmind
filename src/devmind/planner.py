"""Create a small, deterministic investigation plan from analyzed issue text."""

from devmind.models import IssueAnalysis


def create_plan(analysis: IssueAnalysis, *, max_steps: int = 5) -> list[str]:
    """Return a bounded plan; this planner proposes steps and does not execute them."""
    if max_steps < 1:
        raise ValueError("max_steps must be positive.")
    steps = [
        "Inspect the bug report and its extracted issue features.",
        "Index supported source functions and classes without executing repository files.",
        "Retrieve source evidence matching the issue terms and component hints.",
        "Compare candidate source behavior with the reported symptom and identify tests.",
        "Propose a minimal diff only when evidence is sufficient, then verify it in isolation.",
    ]
    if analysis.component_hints:
        steps.insert(1, "Prioritize the reported component hint(s): " + ", ".join(analysis.component_hints[:3]))
    return steps[:max_steps]

