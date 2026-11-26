from devmind.pr_generator import generate_pr_draft


def test_generate_pr_draft_creates_complete_markdown():
    report = {
        "issue": "safe_divide raises ZeroDivisionError when denominator is zero",
        "status": "tests_passed_review_required",
        "candidate_patch": "diff --git a/calc.py b/calc.py\n--- a/calc.py\n+++ b/calc.py\n@@ -1 +1 @@\n-return a / b\n+return None if b == 0 else a / b\n",
        "analysis": {"issue_type": "exception", "keywords": ["safe_divide", "zerodivisionerror"]},
        "evidence": [
            {"path": "calc.py", "start_line": 10, "end_line": 15, "name": "safe_divide", "score": 0.4567}
        ],
        "investigation": {
            "hypotheses": ["[E1] safe_divide may raise ZeroDivisionError"]
        },
        "test_result": {
            "executed": True,
            "passed": True,
            "exit_code": 0,
            "runner": "pytest",
        },
        "review": {
            "verdict": "tests_passed_review_required",
            "reason": "Isolated pytest tests passed.",
        },
    }

    draft = generate_pr_draft(report)
    assert "# fix(calc.py): resolve bug in `safe_divide`" in draft
    assert "safe_divide raises ZeroDivisionError" in draft
    assert "[E1]" in draft
    assert "calc.py:10-15" in draft
    assert "0.4567" in draft
    assert "TESTS PASSED (ISOLATED DOCKER SANDBOX)" in draft
    assert "diff --git a/calc.py" in draft
    assert "git apply devmind-candidate.patch" in draft


def test_generate_pr_draft_handles_empty_fields_gracefully():
    empty_report = {}
    draft = generate_pr_draft(empty_report)
    assert "# fix(repository): resolve bug" in draft
    assert "No issue description provided." in draft
    assert "TESTS NOT EXECUTED" in draft
