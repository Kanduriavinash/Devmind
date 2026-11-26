import json

from devmind import evaluation_runner
from devmind.providers import ChatProvider

VALID_DIFF = "diff --git a/sample.py b/sample.py\n--- a/sample.py\n+++ b/sample.py\n@@ -1 +1 @@\n-def f(): pass\n+def f(): return 1\n"


class Provider(ChatProvider):
    model = "test-model"

    def complete(self, prompt):
        return VALID_DIFF


def test_comparison_runs_all_methods_and_separates_labels(tmp_path, monkeypatch):
    from devmind.models import RunReport

    evidence = [{"path": "sample.py", "start_line": 1, "end_line": 2, "content": "def f(): pass"}]
    report = RunReport("patch_proposed_unverified", "bug", {}, [], evidence, {})
    def fake_analysis(*args, **kwargs):
        if kwargs.get("generate_patch"):
            kwargs["provider"].complete("one-shot RAG prompt")
            report.candidate_patch = VALID_DIFF
        return report

    def fake_repair(*args, **kwargs):
        kwargs["provider"].complete("agentic prompt")
        return {
            "status": "tests_passed_review_required", "candidate_patch": VALID_DIFF,
            "test_result": {"executed": True, "passed": True, "mode": "candidate_patch"},
            "attempts": [{"attempt_id": "demo-1-attempt-01", "model_request": True, "sandbox_call": True}], "attempt_count": 1,
        }

    sandbox_calls = []
    def fake_tests(repository, *, candidate_patch=None, **kwargs):
        sandbox_calls.append(candidate_patch)
        mode = "candidate_patch" if candidate_patch is not None else "baseline_repository"
        return {"executed": True, "passed": True, "mode": mode, "runner": "pytest"}

    monkeypatch.setattr(evaluation_runner, "run_analysis", fake_analysis)
    monkeypatch.setattr(evaluation_runner, "run_repair", fake_repair)
    monkeypatch.setattr(evaluation_runner, "run_tests", fake_tests)
    output_file = tmp_path / "raw" / "runs.jsonl"
    result = evaluation_runner.run_comparison([{
        "issue_id": "demo-1", "bug_report": "f returns an incorrect value", "repository": tmp_path,
    }], provider=Provider(), output_path=output_file)
    records = result["run_records"]
    assert [record["method"] for record in records] == ["llm_only", "rag_only", "agentic_rag"]
    assert records[2]["ground_truth"]["issue_resolved"] is None
    assert records[2]["prediction"]["issue_resolved"] is None
    assert records[0]["prediction"]["tests_passed"] is True
    assert records[0]["prediction"]["status"] == "tests_passed_review_required"
    assert records[1]["prediction"]["tests_passed"] is True
    assert records[2]["prediction"]["tests_passed"] is True
    assert records[2]["repair_attempts"][0]["attempt_id"] == "demo-1-attempt-01"
    assert records[2]["configuration"]["model"] == "test-model"
    assert [record["measurements"]["model_requests"] for record in records] == [1, 1, 1]
    assert [record["measurements"]["sandbox_calls"] for record in records] == [1, 1, 1]
    assert [record["measurements"]["external_tool_calls"] for record in records] == [3, 3, 3]
    assert all(record["baseline_test_result"]["mode"] == "baseline_repository" for record in records)
    assert all(record["measurements"]["shared_baseline_sandbox_calls"] == 1 for record in records)
    assert len(sandbox_calls) == 3
    assert len(output_file.read_text(encoding="utf-8").splitlines()) == 3
    assert result["metrics"]["methods"]["agentic_rag"]["test_pass_rate"] == 1.0
    assert result["metrics"]["methods"]["agentic_rag"]["resolution_accuracy"] is None


def test_one_shot_candidate_without_docker_is_not_reported_as_passing(tmp_path, monkeypatch):
    from devmind.models import RunReport
    from devmind.sandbox import SandboxUnavailable

    report = RunReport("patch_proposed_unverified", "bug", {}, [], [], {}, candidate_patch=VALID_DIFF)
    monkeypatch.setattr(evaluation_runner, "run_analysis", lambda *args, **kwargs: report)
    monkeypatch.setattr(
        evaluation_runner,
        "run_repair",
        lambda *args, **kwargs: {
            "status": "repair_blocked_sandbox_unavailable",
            "candidate_patch": VALID_DIFF,
            "test_result": {"executed": False, "passed": False, "reason": "Docker unavailable"},
            "attempts": [{"model_request": True, "sandbox_call": True}],
            "attempt_count": 1,
        },
    )

    def missing_docker(*args, **kwargs):
        raise SandboxUnavailable("Docker is not available; tests were not run.")

    monkeypatch.setattr(evaluation_runner, "run_tests", missing_docker)
    result = evaluation_runner.run_comparison(
        [{"issue_id": "blocked", "bug_report": "f is wrong", "repository": tmp_path}],
        provider=Provider(),
    )
    llm, rag, agentic = result["run_records"]

    assert llm["prediction"]["status"] == "candidate_test_blocked"
    assert rag["prediction"]["status"] == "candidate_test_blocked"
    assert llm["prediction"]["tests_passed"] is None
    assert rag["prediction"]["tests_passed"] is None
    assert llm["test_result"]["executed"] is False
    assert llm["baseline_test_result"]["executed"] is False
    assert agentic["prediction"]["tests_passed"] is None


def test_comparison_rejects_duplicate_issue_ids(tmp_path):
    issues = [
        {"issue_id": "x", "bug_report": "failure", "repository": tmp_path},
        {"issue_id": "x", "bug_report": "failure", "repository": tmp_path},
    ]
    try:
        evaluation_runner.run_comparison(issues, provider=Provider())
    except ValueError as error:
        assert "unique" in str(error)
    else:
        raise AssertionError("Duplicate benchmark issue IDs must be rejected.")

