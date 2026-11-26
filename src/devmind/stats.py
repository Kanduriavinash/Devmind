"""Aggregate and summarize historical DevMind run reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_report_history(reports_directory: str | Path = "reports") -> list[dict[str, Any]]:
    """Scan a reports directory and extract structured run records.
    
    Skips unreadable, invalid, or non-dictionary JSON files gracefully.
    """
    directory = Path(reports_directory).expanduser().resolve()
    if not directory.is_dir():
        return []

    records: list[dict[str, Any]] = []
    for file_path in sorted(directory.glob("*.json")):
        try:
            content = json.loads(file_path.read_text(encoding="utf-8"))
            if not isinstance(content, dict):
                continue
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue

        status = content.get("status", "unknown")
        issue = content.get("issue", "")
        test_result = content.get("test_result") or {}
        test_executed = bool(test_result.get("executed", False))
        test_passed = bool(test_result.get("passed", False))
        candidate_patch = content.get("candidate_patch")
        patch_generated = bool(candidate_patch and str(candidate_patch).strip())
        repair_attempts = len(content.get("repair_attempts", []))

        # Detect project / language from retrieved evidence or issue text
        evidence = content.get("evidence", [])
        primary_path = evidence[0].get("path", "") if evidence and isinstance(evidence, list) and isinstance(evidence[0], dict) else ""
        project = _detect_project_name(file_path.name, primary_path, issue)

        stat_info = file_path.stat()
        records.append({
            "filename": file_path.name,
            "file_path": str(file_path),
            "modified_time": stat_info.st_mtime,
            "status": status,
            "issue": issue,
            "project": project,
            "primary_path": primary_path,
            "test_executed": test_executed,
            "test_passed": test_passed,
            "patch_generated": patch_generated,
            "repair_attempts": repair_attempts,
            "is_test_passed_candidate": status == "tests_passed_review_required" and test_passed,
        })

    # Sort descending by file modification time (most recent first)
    records.sort(key=lambda r: r["modified_time"], reverse=True)
    return records


def compute_dashboard_stats(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute high-level KPIs and project-level breakdown from run records."""
    if not records:
        return {
            "total_runs": 0,
            "test_passed_candidates": 0,
            "unique_projects": 0,
            "test_pass_rate": None,
            "patches_generated": 0,
            "projects": {},
            "status_distribution": {},
        }

    total_runs = len(records)
    test_passed_candidates = sum(1 for r in records if r["is_test_passed_candidate"])
    patches_generated = sum(1 for r in records if r["patch_generated"])
    tested_runs = [r for r in records if r["test_executed"]]
    test_pass_rate = (sum(1 for r in tested_runs if r["test_passed"]) / len(tested_runs) * 100.0) if tested_runs else None

    projects: dict[str, dict[str, Any]] = {}
    status_distribution: dict[str, int] = {}

    for r in records:
        proj = r["project"]
        if proj not in projects:
            projects[proj] = {"total_runs": 0, "test_passed_candidates": 0, "patches_generated": 0}
        projects[proj]["total_runs"] += 1
        if r["is_test_passed_candidate"]:
            projects[proj]["test_passed_candidates"] += 1
        if r["patch_generated"]:
            projects[proj]["patches_generated"] += 1

        st = r["status"]
        status_distribution[st] = status_distribution.get(st, 0) + 1

    return {
        "total_runs": total_runs,
        "test_passed_candidates": test_passed_candidates,
        "unique_projects": len(projects),
        "test_pass_rate": round(test_pass_rate, 1) if test_pass_rate is not None else None,
        "patches_generated": patches_generated,
        "projects": dict(sorted(projects.items())),
        "status_distribution": dict(sorted(status_distribution.items())),
    }


def _detect_project_name(filename: str, path: str, issue: str) -> str:
    """Infer a human-readable project label from metadata."""
    combined = f"{filename} {path} {issue}".lower()
    if "cricket" in combined or "script.js" in combined:
        return "Cricket Scorer Pro (JavaScript)"
    if "calc" in combined or "safe_divide" in combined or "buggy_project" in combined:
        return "Calculator Project (Python)"
    if path:
        return Path(path).parts[0] if len(Path(path).parts) > 1 else Path(path).stem
    return "Generic Repository"
