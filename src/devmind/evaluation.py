"""Aggregate reproducible run records without inventing missing outcomes."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

METHODS = {"llm_only", "rag_only", "agentic_rag"}


def summarize_runs(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute rates and means; ground truth and system predictions stay separate."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        method = record.get("method")
        if method not in METHODS:
            raise ValueError(f"Unknown evaluation method: {method!r}")
        if not isinstance(record.get("issue_id"), str) or not record["issue_id"].strip():
            raise ValueError("Each run record needs a non-empty issue_id.")
        prediction = record.get("prediction", {})
        ground_truth = record.get("ground_truth", {})
        measurements = record.get("measurements", {})
        if not isinstance(prediction, dict) or not isinstance(ground_truth, dict) or not isinstance(measurements, dict):
            raise ValueError("prediction, ground_truth, and measurements must be objects.")
        if not isinstance(prediction.get("status"), str) or not prediction["status"]:
            raise ValueError("Each prediction needs a non-empty status.")
        for value, field in (
            (prediction.get("tests_passed"), "prediction.tests_passed"),
            (prediction.get("issue_resolved"), "prediction.issue_resolved"),
            (ground_truth.get("issue_resolved"), "ground_truth.issue_resolved"),
        ):
            if value is not True and value is not False and value is not None:
                raise ValueError(f"{field} must be true, false, or null.")
        groups[method].append(record)

    result: dict[str, Any] = {}
    for method in sorted(METHODS):
        runs = groups[method]
        if not runs:
            result[method] = {
                "run_count": 0, "status_counts": {}, "run_failure_rate": None,
                "run_failure_count": 0, "test_pass_rate": None,
                "test_observed_count": 0, "resolution_accuracy": None,
                "baseline_test_pass_rate": None, "baseline_test_observed_count": 0,
                "baseline_test_blocked_count": 0,
                "resolution_observed_count": 0, "mean_iterations": None,
                "mean_latency_seconds": None, "mean_model_requests": None,
                "mean_sandbox_calls": None, "mean_token_count": None,
                "mean_estimated_cost_usd": None,
            }
            continue

        test_values = [r["prediction"]["tests_passed"] for r in runs if r["prediction"].get("tests_passed") is not None]
        baseline_results = [r.get("baseline_test_result") for r in runs]
        baseline_observed = [
            item for item in baseline_results if isinstance(item, dict) and item.get("executed") is True
        ]
        baseline_blocked_count = sum(
            isinstance(item, dict) and item.get("executed") is not True for item in baseline_results
        )
        baseline_test_values = [item.get("passed") is True for item in baseline_observed]
        labeled = [r for r in runs if r["ground_truth"].get("issue_resolved") is not None and r["prediction"].get("issue_resolved") is not None]
        correct = [r["ground_truth"]["issue_resolved"] == r["prediction"]["issue_resolved"] for r in labeled]
        status_counts: dict[str, int] = defaultdict(int)
        for run in runs:
            status_counts[run["prediction"]["status"]] += 1
        failures = [run for run in runs if _is_failed_status(run["prediction"]["status"])]

        result[method] = {
            "run_count": len(runs),
            "status_counts": dict(sorted(status_counts.items())),
            "run_failure_rate": len(failures) / len(runs),
            "run_failure_count": len(failures),
            "test_pass_rate": sum(test_values) / len(test_values) if test_values else None,
            "test_observed_count": len(test_values),
            "baseline_test_pass_rate": (
                sum(baseline_test_values) / len(baseline_test_values) if baseline_test_values else None
            ),
            "baseline_test_observed_count": len(baseline_test_values),
            "baseline_test_blocked_count": baseline_blocked_count,
            "resolution_accuracy": sum(correct) / len(correct) if correct else None,
            "resolution_observed_count": len(correct),
            "mean_iterations": _mean(_observations(runs, "iterations")),
            "mean_latency_seconds": _mean(_observations(runs, "latency_seconds")),
            "mean_model_requests": _mean(_observations(runs, "model_requests")),
            "mean_sandbox_calls": _mean(_observations(runs, "sandbox_calls")),
            "mean_token_count": _mean(_observations(runs, "token_count")),
            "mean_estimated_cost_usd": _mean(_observations(runs, "estimated_cost_usd")),
        }
    definition = (
        "run_failure_rate = blocked statuses, statuses ending _failed, or repair_attempt_limit_reached divided by all runs; "
        "test_pass_rate = passed candidate test runs / runs with an observed candidate test result; baseline_test_pass_rate = passed unmodified test suites / runs with an observed baseline suite; resolution_accuracy = exact matches between "
        "separately stored ground-truth and predicted issue-resolution labels; numeric means exclude missing, negative, "
        "boolean, and non-finite values; null means no observations"
    )
    return {"metrics_definition": definition, "methods": result}


def _number(value: Any) -> bool:
    """Return whether a value is a finite non-negative numeric observation."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0


def _observations(runs: list[dict[str, Any]], field: str) -> list[int | float]:
    """Get valid numeric measurements from each raw run record."""
    values = [record["measurements"].get(field) for record in runs]
    return [value for value in values if _number(value)]


def _mean(values: list[int | float]) -> float | None:
    """Return an arithmetic mean or null when there are no observations."""
    return sum(values) / len(values) if values else None


def _is_failed_status(status: str) -> bool:
    """Classify blocked runs, failed tests, and exhausted repair loops as failures."""
    return "blocked" in status or status.endswith("_failed") or status == "repair_attempt_limit_reached"


def write_run_records(path: str | Path, records: list[dict[str, Any]]) -> None:
    """Append raw records as UTF-8 JSON Lines so earlier runs are preserved."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
