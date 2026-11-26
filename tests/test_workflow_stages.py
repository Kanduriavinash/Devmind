import pytest

from devmind.analyzer import analyze_issue
from devmind.planner import create_plan
from devmind.reviewer import review_candidate


def test_planner_is_bounded_and_uses_component_hints():
    analysis = analyze_issue("parser.py parse_value raises on empty input")
    plan = create_plan(analysis, max_steps=3)
    assert len(plan) == 3
    assert any("parser.py" in step for step in plan)


def test_planner_rejects_nonpositive_bound():
    with pytest.raises(ValueError):
        create_plan(analyze_issue("something fails"), max_steps=0)


def test_reviewer_never_approves_unexecuted_or_baseline_tests():
    patch = "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a\n+b\n"
    assert review_candidate(patch, None)["verdict"] == "unverified"
    baseline = {"executed": True, "passed": True, "exit_code": 0, "mode": "baseline_repository"}
    assert review_candidate(patch, baseline)["verdict"] == "unverified"


def test_reviewer_keeps_human_review_for_passing_patch():
    result = {"executed": True, "passed": True, "exit_code": 0, "mode": "candidate_patch", "timed_out": False}
    patch = "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a\n+b\n"
    assert review_candidate(patch, result)["verdict"] == "tests_passed_review_required"

