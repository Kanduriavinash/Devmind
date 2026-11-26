"""Prepare SWE-bench Lite predictions from exported JSONL instances.

This module produces candidate patches only. It never executes repository code;
the official SWE-bench Docker harness is responsible for grading predictions.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from devmind.github_repo import download_public_repository
from devmind.pipeline import run_analysis
from devmind.providers import ChatProvider, OpenAICompatibleProvider


class SWEbenchInputError(ValueError):
    """An exported SWE-bench instance is missing required benchmark metadata."""


def load_instances(path: str | Path) -> list[dict[str, Any]]:
    """Read the JSONL instance export produced from SWE-bench Lite."""
    rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SWEbenchInputError(f"Invalid JSON on line {line_number}.") from exc
                validate_instance(row)
                if row["instance_id"] in seen_ids:
                    raise SWEbenchInputError(f"Duplicate SWE-bench instance ID on line {line_number}.")
                seen_ids.add(row["instance_id"])
                rows.append(row)
    except OSError as exc:
        raise SWEbenchInputError(f"Could not read SWE-bench instances: {exc}") from exc
    if not rows:
        raise SWEbenchInputError("The instance file contains no tasks.")
    return rows


def validate_instance(row: Any) -> None:
    """Validate only the official fields needed for pinned static analysis."""
    if not isinstance(row, dict):
        raise SWEbenchInputError("Each SWE-bench JSONL row must be an object.")
    for field in ("instance_id", "repo", "base_commit", "problem_statement"):
        if not isinstance(row.get(field), str) or not row[field].strip():
            raise SWEbenchInputError(f"SWE-bench instance needs a non-empty {field}.")
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}", row["repo"]):
        raise SWEbenchInputError("SWE-bench repo must be an owner/repository name.")
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", row["base_commit"]):
        raise SWEbenchInputError("SWE-bench base_commit must be a hexadecimal commit ID.")


def select_instances(rows: list[dict[str, Any]], instance_ids: Iterable[str]) -> list[dict[str, Any]]:
    """Select an explicit, unique task subset and reject unknown IDs."""
    requested = list(instance_ids)
    if not requested or len(requested) != len(set(requested)):
        raise SWEbenchInputError("Provide one or more unique --instance-ids; full-suite runs must be explicit.")
    by_id = {row["instance_id"]: row for row in rows}
    missing = [instance_id for instance_id in requested if instance_id not in by_id]
    if missing:
        raise SWEbenchInputError(f"Unknown SWE-bench instance ID(s): {', '.join(missing)}")
    return [by_id[instance_id] for instance_id in requested]


def generate_predictions(
    rows: list[dict[str, Any]],
    *,
    instance_ids: Iterable[str],
    repository_cache: str | Path,
    provider: ChatProvider | None = None,
    top_k: int = 4,
    context_chars: int = 1500,
) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    """Analyze pinned source snapshots and return harness predictions + run notes."""
    if not 1 <= top_k <= 8:
        raise ValueError("top_k must be between 1 and 8.")
    if not 500 <= context_chars <= 5000:
        raise ValueError("context_chars must be between 500 and 5000.")
    selected = select_instances(rows, instance_ids)
    active_provider = provider or OpenAICompatibleProvider()
    cache = Path(repository_cache).expanduser().resolve()
    cache.mkdir(parents=True, exist_ok=True)
    predictions: list[dict[str, str]] = []
    notes: list[dict[str, Any]] = []
    for instance in selected:
        owner, repository = instance["repo"].split("/", 1)
        identity = f"{instance['repo']}@{instance['base_commit']}"
        cache_name = hashlib.sha256(identity.encode("utf-8")).hexdigest()
        cache_pointer = cache / f"{cache_name}.json"
        repository_path: Path | None = None
        skipped_symlinks: int | None = None
        if cache_pointer.is_symlink():
            raise SWEbenchInputError("The SWE-bench repository cache pointer cannot be a symbolic link.")
        if cache_pointer.is_file():
            try:
                cached = json.loads(cache_pointer.read_text(encoding="utf-8"))
                directory = cached.get("directory") if isinstance(cached, dict) else None
                if isinstance(directory, str) and Path(directory).name == directory and directory.startswith("devmind-repo-"):
                    candidate = (cache / directory).resolve()
                    candidate.relative_to(cache)
                    if candidate.is_dir() and not candidate.is_symlink():
                        repository_path = candidate
                        count = cached.get("skipped_symlinks")
                        skipped_symlinks = count if isinstance(count, int) and count >= 0 else None
            except (OSError, ValueError, json.JSONDecodeError):
                repository_path = None
        if repository_path is None:
            downloaded = download_public_repository(
                f"https://github.com/{owner}/{repository}",
                cache,
                ref=instance["base_commit"],
                max_files=20_000,
                skip_symlinks=True,
            )
            skipped_symlinks = downloaded.skipped_symlinks
            repository_path = downloaded.path.resolve()
            try:
                repository_path.relative_to(cache)
            except ValueError as exc:
                raise SWEbenchInputError("Downloaded repository escaped the configured cache directory.") from exc
            cache_pointer.write_text(
                json.dumps({"directory": repository_path.name, "skipped_symlinks": skipped_symlinks}),
                encoding="utf-8",
            )
        report = run_analysis(
            instance["problem_statement"],
            repository_path,
            provider=active_provider,
            generate_patch=True,
            limit=top_k,
            patch_context_chars=context_chars,
        )
        patch = report.candidate_patch or ""
        predictions.append({
            "instance_id": instance["instance_id"],
            "model_patch": patch,
            "model_name_or_path": str(getattr(active_provider, "model", "unknown") or "unknown"),
        })
        notes.append({
            "instance_id": instance["instance_id"],
            "repository": instance["repo"],
            "base_commit": instance["base_commit"],
            "skipped_symlinks": skipped_symlinks,
            "status": report.status,
            "retrieved_evidence_count": len(report.evidence),
            "patch_proposed": bool(patch),
            "patch_tested": False,
            "limitations": report.limitations,
        })
    return predictions, notes


def write_jsonl(path: str | Path, records: Iterable[dict[str, Any]]) -> None:
    """Write a UTF-8 JSONL file, replacing any previous run at that path."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
