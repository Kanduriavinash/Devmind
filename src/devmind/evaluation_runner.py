"""Run the three DevMind research strategies on the same issue set."""

from __future__ import annotations

import time
import uuid
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from devmind.evaluation import summarize_runs, write_run_records
from devmind.code_agent import InvalidCandidatePatch, validate_unified_diff
from devmind.pipeline import run_analysis
from devmind.providers import ChatProvider, OpenAICompatibleProvider, ProviderUnavailable
from devmind.orchestrator import run_repair
from devmind.sandbox import SandboxUnavailable, run_tests


class _CountingProvider(ChatProvider):
    """Count actual provider calls for one strategy without changing its behavior."""

    def __init__(self, provider: ChatProvider):
        self._provider = provider
        self.calls = 0
        self.prompt_characters = 0
        self.prompt_whitespace_token_estimate = 0

    @property
    def model(self) -> str | None:
        return getattr(self._provider, "model", None)

    def complete(self, prompt: str) -> str:
        self.calls += 1
        self.prompt_characters += len(prompt)
        self.prompt_whitespace_token_estimate += len(prompt.split())
        return self._provider.complete(prompt)

def run_comparison(
    issues: list[dict[str, Any]],
    *,
    provider: ChatProvider | None = None,
    max_attempts: int = 2,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    """Execute all three strategies for each issue and optionally append raw JSONL.

    Each issue mapping needs ``issue_id``, ``bug_report``, and ``repository``.
    The runner does not infer ground truth or issue-resolution predictions from
    patch generation/test outcomes; those boolean labels remain null pending
    independent human adjudication.
    """
    if not issues:
        raise ValueError("At least one evaluation issue is required.")
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3.")
    seen: set[str] = set()
    for issue in issues:
        if not isinstance(issue, dict):
            raise ValueError("Each evaluation issue must be a JSON object.")
        issue_id = issue.get("issue_id")
        if not isinstance(issue_id, str) or not issue_id.strip() or issue_id in seen:
            raise ValueError("Evaluation issues need unique, non-empty issue_id values.")
        seen.add(issue_id)
        if not isinstance(issue.get("bug_report"), str) or not issue["bug_report"].strip():
            raise ValueError(f"Issue {issue_id!r} needs a non-empty bug_report.")
        if not isinstance(issue.get("repository"), (str, Path)) or not Path(issue["repository"]).is_dir():
            raise ValueError(f"Issue {issue_id!r} needs an existing repository directory.")

    active_provider = provider or OpenAICompatibleProvider()
    records: list[dict[str, Any]] = []
    for issue in issues:
        baseline_started = time.perf_counter()
        baseline_test_result = _test_baseline_repository(issue["repository"])
        baseline_test_latency = round(time.perf_counter() - baseline_started, 6)
        issue_records = [
            _run_llm_only(issue, _CountingProvider(active_provider), max_attempts),
            _run_rag_only(issue, _CountingProvider(active_provider), max_attempts),
            _run_agentic(issue, _CountingProvider(active_provider), max_attempts),
        ]
        for record in issue_records:
            record["baseline_test_result"] = baseline_test_result
            record["measurements"]["shared_baseline_sandbox_calls"] = 1
            record["measurements"]["baseline_test_latency_seconds"] = baseline_test_latency
            record["measurements"]["external_tool_calls"] += 1
            records.append(record)

    if output_path is not None:
        write_run_records(output_path, records)
    return {"run_records": records, "metrics": summarize_runs(records), "metrics_note": "Issue-resolution accuracy remains null until predictions and human ground-truth labels are separately provided."}


def _run_llm_only(issue: dict[str, Any], provider: _CountingProvider, max_attempts: int) -> dict[str, Any]:
    started = time.perf_counter()
    patch = None
    status = "patch_blocked_provider_unavailable"
    error = None
    try:
        response = provider.complete(
            "Propose a minimal unified diff for this software bug report. You have no repository retrieval context. "
            "Return a unified diff only; do not claim tests passed.\n\nBug report:\n" + issue["bug_report"]
        ).strip()
        try:
            validate_unified_diff(response)
            patch, status = response, "patch_proposed_unverified"
        except InvalidCandidatePatch:
            status = "patch_blocked_invalid_diff"
    except ProviderUnavailable as exc:
        error = str(exc)
    test_result = _test_one_shot_candidate(issue["repository"], patch)
    status = _status_after_test(status, test_result)
    return _record(
        issue, "llm_only", status, patch, test_result, max_attempts, provider.calls,
        int(test_result is not None), time.perf_counter() - started,
        _test_error(test_result) or error, tests_passed=_observed_test_result(test_result),
        model_name=provider.model, prompt_characters=provider.prompt_characters,
        prompt_whitespace_token_estimate=provider.prompt_whitespace_token_estimate,
    )


def _run_rag_only(issue: dict[str, Any], provider: _CountingProvider, max_attempts: int) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        report = run_analysis(issue["bug_report"], issue["repository"], provider=provider, generate_patch=True)
        test_result = _test_one_shot_candidate(issue["repository"], report.candidate_patch)
        status = _status_after_test(report.status, test_result)
        return _record(
            issue, "rag_only", status, report.candidate_patch, test_result, max_attempts,
            provider.calls, int(test_result is not None), time.perf_counter() - started,
            _test_error(test_result), report.evidence,
            tests_passed=_observed_test_result(test_result), model_name=provider.model,
            prompt_characters=provider.prompt_characters,
            prompt_whitespace_token_estimate=provider.prompt_whitespace_token_estimate,
        )
    except (OSError, ValueError, ProviderUnavailable) as exc:
        return _record(issue, "rag_only", "run_blocked_or_failed", None, None, max_attempts, provider.calls, 0, time.perf_counter() - started, f"{type(exc).__name__}: {exc}", model_name=provider.model)


def _run_agentic(issue: dict[str, Any], provider: _CountingProvider, max_attempts: int) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        report = run_analysis(issue["bug_report"], issue["repository"])
        repair = run_repair(
            issue["bug_report"],
            report.evidence,
            issue["repository"],
            provider=provider,
            max_attempts=max_attempts,
            issue_id=str(issue["issue_id"]),
            investigation=report.investigation.get("hypotheses", []),
            repository_metadata={
                "root_name": Path(issue["repository"]).name,
                "language": "Python, JavaScript, or TypeScript",
                "base_commit": issue.get("base_commit"),
            },
        )
        sandbox_calls = sum(bool(attempt.get("sandbox_call")) for attempt in repair["attempts"])
        test_result = repair["test_result"]
        tests_passed = test_result.get("passed") if test_result.get("executed") else None
        return _record(
            issue, "agentic_rag", repair["status"], repair["candidate_patch"],
            test_result if test_result else None, max_attempts,
            provider.calls, sandbox_calls, time.perf_counter() - started, None,
            report.evidence, repair["attempt_count"], tests_passed, provider.model,
            provider.prompt_characters, provider.prompt_whitespace_token_estimate,
            repair_attempts=repair.get("attempts", []),
        )
    except (OSError, ValueError, ProviderUnavailable) as exc:
        return _record(issue, "agentic_rag", "run_blocked_or_failed", None, None, max_attempts, provider.calls, 0, time.perf_counter() - started, f"{type(exc).__name__}: {exc}", model_name=provider.model)


def _test_one_shot_candidate(repository: str | Path, patch: str | None) -> dict[str, Any] | None:
    """Run a single-shot candidate in the same disposable Docker test protocol."""
    if patch is None:
        return None
    try:
        return run_tests(repository, candidate_patch=patch)
    except (SandboxUnavailable, OSError, ValueError) as exc:
        return {
            "executed": False,
            "passed": False,
            "mode": "candidate_patch",
            "blocked": True,
            "reason": f"{type(exc).__name__}: {exc}",
        }


def _test_baseline_repository(repository: str | Path) -> dict[str, Any]:
    """Run the unmodified test suite once before comparing candidate patches."""
    try:
        return run_tests(repository)
    except (SandboxUnavailable, OSError, ValueError) as exc:
        return {
            "executed": False,
            "passed": False,
            "mode": "baseline_repository",
            "blocked": True,
            "reason": f"{type(exc).__name__}: {exc}",
        }


def _observed_test_result(test_result: dict[str, Any] | None) -> bool | None:
    if test_result is None or not test_result.get("executed"):
        return None
    return test_result.get("passed") is True


def _status_after_test(status: str, test_result: dict[str, Any] | None) -> str:
    if test_result is None:
        return status
    if not test_result.get("executed"):
        return "candidate_test_blocked"
    if test_result.get("passed") is True:
        return "tests_passed_review_required"
    return "candidate_patch_tests_failed"


def _test_error(test_result: dict[str, Any] | None) -> str | None:
    if not test_result:
        return None
    reason = test_result.get("reason")
    return str(reason) if reason else None


def _record(
    issue: dict[str, Any], method: str, status: str, patch: str | None,
    test_result: dict[str, Any] | None, max_attempts: int, model_requests: int,
    sandbox_calls: int, latency: float, error: str | None,
    evidence: list[dict[str, Any]] | None = None, iterations: int = 1,
    tests_passed: bool | None = None, model_name: str | None = None,
    prompt_characters: int | None = None,
    prompt_whitespace_token_estimate: int | None = None,
    repair_attempts: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build one transparent raw run record with labels separated from outputs."""
    return {
        "run_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "issue_id": issue["issue_id"],
        "method": method,
        "input": {"bug_report": issue["bug_report"], "repository": str(issue["repository"])},
        "ground_truth": {"issue_resolved": None},
        "prediction": {"status": status, "candidate_patch": patch, "tests_passed": tests_passed, "issue_resolved": None},
        "configuration": {
            "model": model_name,
            "max_attempts": max_attempts,
            "test_runner": os.getenv("DEVMIND_TEST_RUNNER", "pytest").strip().lower(),
            "sandbox_timeout_seconds": os.getenv("DEVMIND_SANDBOX_TIMEOUT_SECONDS", "120"),
            "retrieval_top_k": 8,
            "patch_context_character_budget": 5000,
        },
        "evidence_locations": [{"path": item["path"], "start_line": item["start_line"], "end_line": item["end_line"]} for item in (evidence or [])],
        "repair_attempts": repair_attempts or [],
        "test_result": test_result,
        "measurements": {
            "iterations": iterations,
            "model_requests": model_requests,
            "sandbox_calls": sandbox_calls,
            "external_tool_calls": model_requests + sandbox_calls,
            "latency_seconds": round(latency, 6),
            "token_count": None,
            "estimated_cost_usd": None,
            "prompt_characters": prompt_characters,
            "prompt_whitespace_token_estimate": prompt_whitespace_token_estimate,
            "max_attempts": max_attempts,
        },
        "error": error,
    }

