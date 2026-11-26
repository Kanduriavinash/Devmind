from devmind import orchestrator
from devmind.models import CodeChunk
from devmind.providers import ProviderUnavailable


EVIDENCE = [{"path": "calc.py", "start_line": 1, "end_line": 2, "content": "def calculate(): return 1"}]
VALID_DIFF = "diff --git a/calc.py b/calc.py\n--- a/calc.py\n+++ b/calc.py\n@@ -1 +1 @@\n-def calculate(): return 1\n+def calculate(): return 2\n"


class SequenceProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.prompts = []

    def complete(self, prompt):
        self.prompts.append(prompt)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def test_repair_stops_when_candidate_tests_pass(tmp_path, monkeypatch):
    patch = VALID_DIFF
    provider = SequenceProvider([patch])
    monkeypatch.setattr(orchestrator, "run_tests", lambda *args, **kwargs: {
        "executed": True, "passed": True, "timed_out": False, "exit_code": 0, "mode": "candidate_patch", "stdout": "2 passed", "stderr": "",
    })
    events = []
    result = orchestrator.run_repair("calculate is wrong", EVIDENCE, tmp_path, provider=provider, max_attempts=3, on_event=events.append)
    assert result["status"] == "tests_passed_review_required"
    assert result["attempt_count"] == 1
    assert result["review"]["verdict"] == "tests_passed_review_required"
    assert [event["stage"] for event in events] == ["model_request", "sandbox", "complete"]


def test_repair_feeds_failure_back_and_respects_attempt_limit(tmp_path, monkeypatch):
    patch = VALID_DIFF
    provider = SequenceProvider([patch, patch, patch])
    outputs = iter([
        {"executed": True, "passed": False, "timed_out": False, "exit_code": 1, "mode": "baseline_repository", "stdout": "baseline failed", "stderr": ""},
        {"executed": True, "passed": False, "timed_out": False, "exit_code": 1, "mode": "candidate_patch", "stdout": "assertion failed", "stderr": ""},
        {"executed": True, "passed": False, "timed_out": False, "exit_code": 1, "mode": "candidate_patch", "stdout": "still failing", "stderr": ""},
    ])
    monkeypatch.setattr(orchestrator, "run_tests", lambda *args, **kwargs: next(outputs))
    result = orchestrator.run_repair("calculate is wrong", EVIDENCE, tmp_path, provider=provider, max_attempts=2)
    assert result["status"] == "repair_attempt_limit_reached"
    assert result["attempt_count"] == 2
    assert "Previous isolated test result" in provider.prompts[1]


def test_failed_tests_retrieve_new_evidence_and_keep_attempt_audit(tmp_path, monkeypatch):
    cart_patch = (
        "diff --git a/cart.js b/cart.js\n"
        "--- a/cart.js\n"
        "+++ b/cart.js\n"
        "@@ -1 +1 @@\n"
        "-function restoreCart() { return []; }\n"
        "+function restoreCart() { return JSON.parse(localStorage.getItem('cart') || '[]'); }\n"
    )
    provider = SequenceProvider([VALID_DIFF, cart_patch])
    test_results = iter([
        {
            "executed": True,
            "passed": False,
            "timed_out": False,
            "exit_code": 1,
            "mode": "baseline_repository",
            "runner": "node",
            "test_command": "node --test",
            "timeout_seconds": 120,
            "stdout": "baseline fail",
            "stderr": "",
        },
        {
            "executed": True,
            "passed": False,
            "timed_out": False,
            "exit_code": 1,
            "mode": "candidate_patch",
            "runner": "node",
            "test_command": "node --test",
            "timeout_seconds": 120,
            "stdout": "not ok 1 - cart reload restores saved items",
            "stderr": "    at restoreCart (/workspace/cart.js:18:7)\nAssertionError: SECRET_TOKEN=do-not-send",
        },
        {
            "executed": True,
            "passed": True,
            "timed_out": False,
            "exit_code": 0,
            "mode": "candidate_patch",
            "runner": "node",
            "test_command": "node --test",
            "timeout_seconds": 120,
            "stdout": "1 test passed",
            "stderr": "",
        },
    ])
    monkeypatch.setattr(orchestrator, "run_tests", lambda *args, **kwargs: next(test_results))
    monkeypatch.setattr(
        orchestrator,
        "index_repository",
        lambda root: [CodeChunk(
            "cart.js", "restoreCart", "Function", 18, 20,
            "function restoreCart() { return localStorage.getItem('cart'); }",
        )],
    )

    result = orchestrator.run_repair(
        "cart reload loses saved items",
        EVIDENCE,
        tmp_path,
        provider=provider,
        max_attempts=2,
        issue_id="quickcart-1",
        repository_metadata={"base_commit": "base-commit"},
    )

    assert result["status"] == "tests_passed_review_required"
    assert result["attempt_count"] == 2
    first, second = result["attempts"]
    assert first["attempt_id"] == "quickcart-1-attempt-01"
    assert first["patch_validation"] == {"valid": True, "changed_paths": ["calc.py"]}
    assert first["patch_sha256"]
    assert first["test_command"] == "node --test"
    assert first["test_timeout_seconds"] == 120
    assert first["failure_analysis"]["failed_tests"] == ["cart reload restores saved items"]
    assert first["next_retrieval"]["method"] == "tfidf_cosine"
    assert first["next_retrieval"]["new_evidence_paths"] == ["cart.js"]
    assert len(first["next_retrieval"]["new_evidence_paths"]) == len(set(first["next_retrieval"]["new_evidence_paths"]))
    assert "restoreCart" in first["next_retrieval"]["query"]
    assert second["evidence_selection"]["method"] == "failure_informed_tfidf_cosine"
    assert "cart.js" in [item["path"] for item in second["evidence"]]
    assert second["feedback_sent_to_model"]["failure_analysis"]["failed_tests"]
    assert "do-not-send" not in provider.prompts[1]
    assert "SECRET_TOKEN" not in provider.prompts[1]
    assert "do-not-send" in first["test_result"]["stderr"]
    assert first["candidate_patch"] == VALID_DIFF.strip("\r\n")
    assert second["candidate_patch"] == cart_patch.strip("\r\n")


def test_repair_stops_when_provider_is_unavailable(tmp_path, monkeypatch):
    provider = SequenceProvider([ProviderUnavailable("offline")])
    monkeypatch.setattr(orchestrator, "run_tests", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("must not run")))
    baseline = {"executed": True, "passed": False, "mode": "baseline_repository"}
    result = orchestrator.run_repair("calculate is wrong", EVIDENCE, tmp_path, provider=provider, baseline_test_result=baseline)
    assert result["status"] == "repair_blocked_provider_unavailable"
    assert result["attempt_count"] == 1


def test_repair_records_docker_execution_errors_as_blocked(tmp_path, monkeypatch):
    provider = SequenceProvider([VALID_DIFF])

    def docker_permission_error(*args, **kwargs):
        raise PermissionError("Docker could not be launched.")

    monkeypatch.setattr(orchestrator, "run_tests", docker_permission_error)
    result = orchestrator.run_repair("calculate is wrong", EVIDENCE, tmp_path, provider=provider)

    assert result["status"] == "repair_blocked_sandbox_unavailable"
    assert result["test_result"]["executed"] is False
    assert "Docker could not be launched" in result["test_result"]["reason"]


def test_repair_rejects_unbounded_attempt_count(tmp_path):
    try:
        orchestrator.run_repair("issue", EVIDENCE, tmp_path, provider=SequenceProvider([]), max_attempts=99)
    except ValueError as error:
        assert "between 1 and 3" in str(error)
    else:
        raise AssertionError("Attempt count must be bounded.")

