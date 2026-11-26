"""Bounded patch-test feedback loop; all candidate execution stays in the sandbox."""

from __future__ import annotations

import os
import time
from collections.abc import Callable, Mapping
from hashlib import sha256
from pathlib import Path
from typing import Any

from devmind.code_agent import generate_candidate_patch, validate_unified_diff
from devmind.failure_analysis import (
    analyze_test_failure,
    build_failure_retrieval_query,
    provider_failure_feedback,
)
from devmind.indexer import index_repository
from devmind.providers import ChatProvider, OpenAICompatibleProvider, ProviderUnavailable
from devmind.reviewer import review_candidate
from devmind.retrieval import TfidfIndex
from devmind.sandbox import SandboxUnavailable, run_tests


def run_repair(
    issue: str,
    evidence: list[dict[str, Any]],
    repository: str | Path,
    *,
    provider: ChatProvider | None = None,
    max_attempts: int = 2,
    on_event: Callable[[dict[str, Any]], None] | None = None,
    investigation: list[str] | None = None,
    repository_metadata: dict[str, Any] | None = None,
    issue_id: str | None = None,
    retrieval_limit: int = 8,
    test_runner: str | None = None,
    docker_image: str | None = None,
    sandbox_timeout: int | None = None,
    baseline_test_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Propose, test, and revise a patch for a small bounded number of attempts.

    Stops when candidate tests pass, the provider/sandbox is unavailable, or the
    attempt limit is reached. The input repository is only read and copied by the
    sandbox runner; patches are never applied to it.
    """
    if not 1 <= max_attempts <= 3:
        raise ValueError("max_attempts must be between 1 and 3.")
    if retrieval_limit < 1:
        raise ValueError("retrieval_limit must be positive.")
    active_provider = provider or OpenAICompatibleProvider()
    active_test_runner = (test_runner or os.getenv("DEVMIND_TEST_RUNNER", "pytest")).strip().lower()
    if baseline_test_result is None:
        try:
            baseline_test_result = run_tests(
                repository,
                image=docker_image,
                timeout=sandbox_timeout,
                test_runner=active_test_runner,
            )
        except (SandboxUnavailable, OSError, ValueError) as exc:
            baseline_test_result = {
                "executed": False,
                "passed": False,
                "mode": "baseline_repository",
                "runner": active_test_runner,
                "reason": str(exc),
            }
    if not baseline_test_result.get("executed"):
        return {
            "status": "repair_blocked_sandbox_unavailable",
            "candidate_patch": None,
            "baseline_test_result": baseline_test_result,
            "test_result": baseline_test_result,
            "review": review_candidate(None, baseline_test_result),
            "attempts": [],
            "attempt_count": 0,
        }
    evidence_ids: dict[tuple[str, int, int, str, str], str] = {}
    active_evidence = _merge_evidence(evidence, [], evidence_ids)[0]
    attempts: list[dict[str, Any]] = []
    previous_test_feedback: dict[str, Any] | None = None
    evidence_selection: dict[str, Any] = {
        "method": "initial_issue_query",
        "reason": "Evidence was retrieved from the unchanged repository snapshot before repair.",
    }
    retry_index: TfidfIndex | None = None
    last_patch: str | None = None
    final_test: dict[str, Any] = {"executed": False, "passed": False, "reason": "No attempt has run."}
    status = "repair_attempt_limit_reached"

    for attempt_number in range(1, max_attempts + 1):
        attempt_id = f"{issue_id or 'run'}-attempt-{attempt_number:02d}"
        current_evidence = active_evidence[:8]
        attempt_record: dict[str, Any] = {
            "attempt_id": attempt_id,
            "issue_id": issue_id,
            "attempt": attempt_number,
            "status": "model_request_pending",
            "model_request": bool(current_evidence),
            "sandbox_call": False,
            "evidence_ids": [item["evidence_id"] for item in current_evidence],
            "evidence": [_audit_evidence(item) for item in current_evidence],
            "evidence_selection": evidence_selection,
            "feedback_sent_to_model": previous_test_feedback,
            "source_revision": (repository_metadata or {}).get("base_commit"),
            "test_runner": active_test_runner,
            "baseline_test_result": baseline_test_result,
        }
        _emit(on_event, attempt_number, "model_request", "Requesting a candidate diff from the configured provider.")
        try:
            generation_trace: dict[str, Any] = {}
            model_started = time.perf_counter()
            candidate = generate_candidate_patch(
                issue,
                current_evidence,
                active_provider,
                test_feedback=previous_test_feedback,
                investigation=investigation,
                repository_metadata=repository_metadata,
                baseline_test_result=baseline_test_result,
                generation_trace=generation_trace,
            )
            generation_trace["inference_elapsed_seconds"] = round(time.perf_counter() - model_started, 6)
            attempt_record["model_generation"] = generation_trace
        except ProviderUnavailable as exc:
            status = "repair_blocked_provider_unavailable"
            _emit(on_event, attempt_number, "blocked", "The model provider is unavailable.")
            attempt_record.update({"status": status, "reason": str(exc)})
            attempts.append(attempt_record)
            break
        if not candidate:
            validation = attempt_record.get("model_generation", {}).get("validation", {})
            status = "repair_blocked_invalid_patch" if validation.get("valid") is False else "repair_blocked_insufficient_evidence"
            reason = validation.get("reason", "The provider did not return a unified diff.")
            _emit(on_event, attempt_number, "blocked", "The model response did not produce a valid evidence-grounded diff.")
            attempt_record.update({
                "status": status,
                "patch_validation": {"valid": False, "reason": reason},
                "reason": reason,
            })
            attempts.append(attempt_record)
            break

        try:
            changed_paths = validate_unified_diff(
                candidate, allowed_paths={str(item["path"]) for item in current_evidence}
            )
        except ValueError as exc:
            status = "repair_blocked_invalid_patch"
            attempt_record.update({
                "status": status,
                "candidate_patch": candidate,
                "patch_validation": {"valid": False, "reason": str(exc)},
            })
            attempts.append(attempt_record)
            _emit(on_event, attempt_number, "blocked", "The candidate diff failed structural validation.")
            break

        last_patch = candidate
        attempt_record.update({
            "candidate_patch": candidate,
            "patch_sha256": sha256(candidate.encode("utf-8")).hexdigest(),
            "patch_validation": {"valid": True, "changed_paths": changed_paths},
        })
        _emit(on_event, attempt_number, "sandbox", "Testing the candidate in a disposable Docker copy.")
        attempt_record["sandbox_call"] = True
        try:
            final_test = run_tests(
                repository,
                candidate_patch=candidate,
                image=docker_image,
                timeout=sandbox_timeout,
                test_runner=active_test_runner,
            )
        except (SandboxUnavailable, OSError, ValueError) as exc:
            status = "repair_blocked_sandbox_unavailable"
            _emit(on_event, attempt_number, "blocked", "The isolated test environment is unavailable.")
            final_test = {"executed": False, "passed": False, "mode": "candidate_patch", "reason": str(exc)}
            attempt_record.update({"status": status, "test_result": final_test})
            attempts.append(attempt_record)
            break

        attempt_record.update({
            "test_command": final_test.get("test_command"),
            "test_runner": final_test.get("runner"),
            "test_timeout_seconds": final_test.get("timeout_seconds"),
            "test_result": final_test,
        })

        review = review_candidate(candidate, final_test)
        if review["verdict"] == "tests_passed_review_required":
            status = "tests_passed_review_required"
            _emit(on_event, attempt_number, "complete", "Candidate tests passed; human review is still required.")
            attempt_record.update({"status": status, "review": review})
            attempts.append(attempt_record)
            break

        if not final_test.get("executed"):
            status = "repair_blocked_sandbox_execution"
            _emit(on_event, attempt_number, "blocked", "The container did not reach the configured test command.")
            attempt_record["status"] = status
            attempts.append(attempt_record)
            break

        failure = analyze_test_failure(final_test)
        failure_query = build_failure_retrieval_query(issue, failure)
        attempt_record["failure_analysis"] = failure.to_dict()
        attempt_record["status"] = "candidate_patch_tests_failed"
        _emit(
            on_event,
            attempt_number,
            "failure_analysis",
            "Extracting test names and source locations from the bounded sandbox output.",
            failed_test_count=len(failure.failed_tests),
            stack_frame_count=len(failure.stack_frames),
        )
        attempts.append(attempt_record)
        status = "repair_attempt_limit_reached" if attempt_number == max_attempts else "repair_retrying"
        if attempt_number < max_attempts:
            previous_test_feedback = provider_failure_feedback(final_test, failure)
            _emit(on_event, attempt_number, "retrieval", "Searching the unchanged repository snapshot for failure-related evidence.")
            try:
                if retry_index is None:
                    root = Path(repository).expanduser().resolve(strict=True)
                    retry_index = TfidfIndex(index_repository(root))
                additional = [_evidence_record(item) for item in retry_index.search(failure_query, limit=retrieval_limit)]
                active_evidence, new_ids = _merge_evidence(additional, active_evidence, evidence_ids)
                attempt_record["next_retrieval"] = {
                    "method": "tfidf_cosine",
                    "query": failure_query,
                    "reason": (
                        "Query augmented with extracted failing-test names, stack-frame paths/symbols, "
                        "and error-class identifiers; search used the unchanged base repository."
                    ),
                    "new_evidence_ids": new_ids,
                    "new_evidence_paths": list(dict.fromkeys(
                        item["path"] for item in active_evidence if item["evidence_id"] in new_ids
                    )),
                }
                evidence_selection = {
                    "method": "failure_informed_tfidf_cosine",
                    "reason": attempt_record["next_retrieval"]["reason"],
                    "query": failure_query,
                    "new_evidence_ids": new_ids,
                }
                _emit(
                    on_event,
                    attempt_number,
                    "retrieval_complete",
                    "Failure-informed retrieval completed against the unchanged repository snapshot.",
                    new_evidence_count=len(new_ids),
                )
            except (OSError, ValueError, SyntaxError) as exc:
                attempt_record["next_retrieval"] = {
                    "method": "tfidf_cosine",
                    "query": failure_query,
                    "reason": "Failure-informed indexing or retrieval could not complete.",
                    "error": f"{type(exc).__name__}: {exc}",
                    "new_evidence_ids": [],
                    "new_evidence_paths": [],
                }
                evidence_selection = {
                    "method": "initial_evidence_after_retrieval_block",
                    "reason": "Failure-informed retrieval was blocked; retain previous evidence and include structured failure feedback.",
                    "query": failure_query,
                    "new_evidence_ids": [],
                }
        else:
            previous_test_feedback = provider_failure_feedback(final_test, failure)
            attempt_record["next_retrieval"] = None
            _emit(on_event, attempt_number, "retry", "Candidate tests failed; the bounded attempt limit was reached.")

    return {
        "status": status,
        "candidate_patch": last_patch,
        "baseline_test_result": baseline_test_result,
        "test_result": final_test,
        "review": review_candidate(last_patch, final_test),
        "attempts": attempts,
        "attempt_count": len(attempts),
    }


def _evidence_record(item: Any) -> dict[str, Any]:
    """Convert an indexed evidence span to the repair prompt/report structure."""
    chunk = item.chunk
    return {
        "path": chunk.path,
        "name": chunk.name,
        "kind": chunk.kind,
        "start_line": chunk.start_line,
        "end_line": chunk.end_line,
        "score": item.score,
        "content": chunk.content,
    }


def _evidence_key(item: Mapping[str, Any]) -> tuple[str, int, int, str, str]:
    content_hash = sha256(str(item.get("content", "")).encode("utf-8")).hexdigest()
    return (
        str(item.get("path", "")),
        int(item.get("start_line", 0)),
        int(item.get("end_line", 0)),
        str(item.get("name", item.get("symbol", ""))),
        content_hash,
    )


def _merge_evidence(
    preferred: list[dict[str, Any]],
    existing: list[dict[str, Any]],
    identifiers: dict[tuple[str, int, int, str, str], str],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Put newly ranked evidence first while preserving stable run-local IDs."""
    merged: list[dict[str, Any]] = []
    added_ids: list[str] = []
    seen: set[tuple[str, int, int, str, str]] = set()
    for is_preferred, raw in [
        *((True, item) for item in preferred),
        *((False, item) for item in existing),
    ]:
        item = dict(raw)
        key = _evidence_key(item)
        if key in seen:
            continue
        seen.add(key)
        evidence_id = identifiers.get(key)
        if evidence_id is None:
            evidence_id = f"E{len(identifiers) + 1}"
            identifiers[key] = evidence_id
            if is_preferred:
                added_ids.append(evidence_id)
        item["evidence_id"] = evidence_id
        merged.append(item)
    return merged, added_ids


def _audit_evidence(item: Mapping[str, Any]) -> dict[str, Any]:
    """Keep a bounded copy of each attempt's exact prompt evidence."""
    result = dict(item)
    result["content"] = str(result.get("content", ""))[:5000]
    return result


def _emit(
    callback: Callable[[dict[str, Any]], None] | None,
    attempt: int,
    stage: str,
    message: str,
    **details: Any,
) -> None:
    """Send a small progress event without including source code or raw logs."""
    if callback is not None:
        callback({"attempt": attempt, "stage": stage, "message": message, **details})

