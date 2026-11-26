import json
from pathlib import Path
import pytest

from devmind.stats import load_report_history, compute_dashboard_stats


def test_load_report_history_empty_on_missing_dir(tmp_path):
    assert load_report_history(tmp_path / "non_existent") == []


def test_load_report_history_skips_invalid_json_and_loads_valid(tmp_path):
    (tmp_path / "bad.json").write_text("not json", encoding="utf-8")
    (tmp_path / "not_dict.json").write_text("[1, 2, 3]", encoding="utf-8")
    
    valid_report = {
        "status": "tests_passed_review_required",
        "issue": "safe_divide crashes on zero",
        "candidate_patch": "diff --git a/calc.py...",
        "test_result": {"executed": True, "passed": True},
        "repair_attempts": [{"attempt": 1}],
        "evidence": [{"path": "calculator.py"}],
    }
    (tmp_path / "good.json").write_text(json.dumps(valid_report), encoding="utf-8")

    records = load_report_history(tmp_path)
    assert len(records) == 1
    record = records[0]
    assert record["filename"] == "good.json"
    assert record["status"] == "tests_passed_review_required"
    assert record["is_test_passed_candidate"] is True
    assert record["project"] == "Calculator Project (Python)"
    assert record["patch_generated"] is True
    assert record["repair_attempts"] == 1


def test_compute_dashboard_stats_aggregates_correctly():
    records = [
        {
            "filename": "1.json",
            "project": "Cricket Scorer Pro (JavaScript)",
            "status": "tests_passed_review_required",
            "is_test_passed_candidate": True,
            "patch_generated": True,
            "test_executed": True,
            "test_passed": True,
        },
        {
            "filename": "2.json",
            "project": "Cricket Scorer Pro (JavaScript)",
            "status": "repair_blocked_insufficient_evidence",
            "is_test_passed_candidate": False,
            "patch_generated": False,
            "test_executed": False,
            "test_passed": False,
        },
        {
            "filename": "3.json",
            "project": "Calculator Project (Python)",
            "status": "tests_passed_review_required",
            "is_test_passed_candidate": True,
            "patch_generated": True,
            "test_executed": True,
            "test_passed": True,
        },
    ]

    stats = compute_dashboard_stats(records)
    assert stats["total_runs"] == 3
    assert stats["test_passed_candidates"] == 2
    assert stats["unique_projects"] == 2
    assert stats["test_pass_rate"] == 100.0  # 2 of 2 executed tests passed
    assert stats["patches_generated"] == 2
    assert stats["projects"]["Cricket Scorer Pro (JavaScript)"]["total_runs"] == 2
    assert stats["projects"]["Cricket Scorer Pro (JavaScript)"]["test_passed_candidates"] == 1
    assert stats["projects"]["Calculator Project (Python)"]["test_passed_candidates"] == 1


def test_compute_dashboard_stats_empty():
    stats = compute_dashboard_stats([])
    assert stats["total_runs"] == 0
    assert stats["test_passed_candidates"] == 0
    assert stats["test_pass_rate"] is None
    assert stats["unique_projects"] == 0
