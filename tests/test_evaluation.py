import pytest

from devmind.evaluation import summarize_runs


def test_metrics_exclude_missing_labels_and_report_denominators():
    result = summarize_runs([
        {"method": "agentic_rag", "issue_id": "A", "prediction": {"status": "tests_passed_review_required", "tests_passed": True, "issue_resolved": True}, "ground_truth": {"issue_resolved": True}, "baseline_test_result": {"executed": True, "passed": False}, "measurements": {"iterations": 1, "latency_seconds": 2.0, "model_requests": 1, "sandbox_calls": 1}},
        {"method": "agentic_rag", "issue_id": "B", "prediction": {"status": "repair_attempt_limit_reached", "tests_passed": None, "issue_resolved": False}, "ground_truth": {"issue_resolved": True}, "baseline_test_result": {"executed": False, "passed": False}, "measurements": {"iterations": 3, "latency_seconds": 4.0, "model_requests": 1, "sandbox_calls": 1}},
    ])
    metric = result["methods"]["agentic_rag"]
    assert metric["run_count"] == 2
    assert metric["test_pass_rate"] == 1.0
    assert metric["test_observed_count"] == 1
    assert metric["baseline_test_pass_rate"] == 0.0
    assert metric["baseline_test_observed_count"] == 1
    assert metric["baseline_test_blocked_count"] == 1
    assert metric["resolution_accuracy"] == 0.5
    assert metric["mean_iterations"] == 2.0
    assert metric["mean_latency_seconds"] == 3.0
    assert metric["run_failure_rate"] == 0.5
    assert result["methods"]["llm_only"]["test_pass_rate"] is None
    assert result["methods"]["llm_only"]["baseline_test_observed_count"] == 0


def test_metrics_reject_unknown_methods_and_malformed_labels():
    with pytest.raises(ValueError):
        summarize_runs([{"method": "other", "issue_id": "A"}])
    with pytest.raises(ValueError):
        summarize_runs([{"method": "rag_only", "issue_id": "A", "prediction": {"tests_passed": "yes"}}])
    with pytest.raises(ValueError):
        summarize_runs([{"method": "rag_only", "issue_id": "A", "prediction": {"tests_passed": 1}}])

