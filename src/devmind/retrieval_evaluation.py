"""Leakage-aware CSV runner for the deterministic TF-IDF query ablation."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Sequence

from devmind.embeddings import SentenceTransformerProvider
from devmind.indexer import index_repository
from devmind.retrieval import SearchIndex
from devmind.retrieval_experiment import build_retrievers, evaluate_retrieval_methods
from devmind.snapshot import snapshot_directory_sha256

INPUT_FIELDS = {
    "issue_id", "repository", "base_commit", "issue_url", "issue_title", "issue_body",
    "language", "base_snapshot_path", "base_snapshot_sha256", "split",
}
LABEL_FIELDS = {
    "issue_id", "relevant_path", "label_type", "label_source", "reviewer",
    "confidence", "decision", "inclusion_reason", "annotation_notes",
}
SUPPORTED_LABEL_TYPES = {"changed_file_proxy", "reviewed_file"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare traceable retrieval methods and query variants.")
    parser.add_argument("--inputs", required=True, type=Path, help="Sanitized datasets/evaluation_inputs.csv")
    parser.add_argument("--labels", required=True, type=Path, help="Human-reviewed datasets/retrieval_ground_truth.csv")
    parser.add_argument("--output", required=True, type=Path, help="New JSONL raw-run output path")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--embedding-model",
        type=Path,
        help="Optional local Sentence Transformers model directory; never downloaded automatically",
    )
    args = parser.parse_args(argv)
    try:
        run_from_csv(
            args.inputs,
            args.labels,
            args.output,
            top_k=args.top_k,
            embedding_model_path=args.embedding_model,
        )
    except (OSError, ValueError, csv.Error) as exc:
        print(f"retrieval evaluation blocked: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    print(f"Wrote retrieval records to {args.output}")
    return 0


def run_from_csv(
    inputs_path: Path,
    labels_path: Path,
    output_path: Path,
    *,
    top_k: int = 5,
    embedding_model_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Load leakage-separated files, index base snapshots, and write JSONL rows."""
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 5:
        raise ValueError("top_k must be at least 5 so all configured metrics are observable.")
    output_path = Path(output_path)
    if output_path.exists():
        raise ValueError(f"Output file already exists: {output_path}")
    inputs = _read_csv(inputs_path, INPUT_FIELDS, "evaluation inputs")
    label_rows = _read_csv(labels_path, LABEL_FIELDS, "ground truth labels")
    labels: dict[str, set[str]] = defaultdict(set)
    for row in label_rows:
        issue_id = row["issue_id"].strip()
        if not issue_id:
            raise ValueError("Ground-truth rows need a non-empty issue_id.")
        decision = row["decision"].strip().casefold()
        if decision == "exclude":
            continue
        if decision != "include":
            raise ValueError(f"Label decision for {issue_id!r} must be include or exclude.")
        if row["label_type"].strip() not in SUPPORTED_LABEL_TYPES:
            raise ValueError(f"Unsupported file-level label type for {issue_id!r}.")
        path = _safe_relative_path(row["relevant_path"])
        labels[issue_id].add(path)

    issue_ids: set[str] = set()
    for row in inputs:
        issue_id = row["issue_id"].strip()
        if not issue_id or issue_id in issue_ids:
            raise ValueError("Evaluation inputs need unique, non-empty issue_id values.")
        issue_ids.add(issue_id)
        if not row["base_commit"].strip() or not row["repository"].strip():
            raise ValueError(f"Issue {issue_id!r} needs a repository and pinned base_commit.")
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", row["base_commit"].strip()):
            raise ValueError(f"Issue {issue_id!r} base_commit must be a hexadecimal Git commit ID.")
        if not (row["issue_title"].strip() or row["issue_body"].strip()):
            raise ValueError(f"Issue {issue_id!r} has no issue title or body.")

    unknown_label_ids = sorted({row["issue_id"].strip() for row in label_rows} - issue_ids)
    if unknown_label_ids:
        raise ValueError(f"Ground-truth issue IDs are absent from evaluation inputs: {unknown_label_ids}.")

    index_cache: dict[
        tuple[str, str, str], tuple[dict[str, SearchIndex], dict[str, float]]
    ] = {}
    snapshot_hash_cache: dict[str, str] = {}
    embedding_provider: SentenceTransformerProvider | None = None
    embedding_model_load_seconds: float | None = None
    records: list[dict[str, Any]] = []
    for row in inputs:
        issue_id = row["issue_id"].strip()
        relevant = labels.get(issue_id, set())
        if not relevant:
            records.append({
                "issue_id": issue_id,
                "variant": None,
                "status": "excluded_missing_included_labels",
                "metrics": None,
                "error": "No included file-level ground-truth labels were provided.",
            })
            continue

        snapshot = Path(row["base_snapshot_path"]).expanduser().resolve()
        if not snapshot.is_dir():
            records.append({
                "issue_id": issue_id,
                "variant": None,
                "status": "index_blocked_snapshot_missing",
                "metrics": None,
                "error": "The recorded base snapshot path is not a directory.",
            })
            continue
        expected_hash = row["base_snapshot_sha256"].strip().casefold()
        actual_hash: str | None = None
        hash_seconds: float | None = None
        hash_verified: bool | None = None
        if expected_hash:
            if not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                records.append({
                    "issue_id": issue_id,
                    "variant": None,
                    "status": "index_blocked_snapshot_hash_invalid",
                    "metrics": None,
                    "snapshot_sha256_expected": expected_hash,
                    "snapshot_hash_verified": False,
                    "error": "The supplied snapshot SHA-256 must contain exactly 64 hexadecimal characters.",
                })
                continue
            hash_started = time.perf_counter()
            try:
                cache_key_path = str(snapshot)
                actual_hash = snapshot_hash_cache.get(cache_key_path)
                if actual_hash is None:
                    actual_hash = snapshot_directory_sha256(snapshot)
                    snapshot_hash_cache[cache_key_path] = actual_hash
            except (OSError, RuntimeError, ValueError) as exc:
                records.append({
                    "issue_id": issue_id,
                    "variant": None,
                    "status": "index_blocked_snapshot_hash_error",
                    "metrics": None,
                    "snapshot_sha256_expected": expected_hash,
                    "snapshot_hash_verified": False,
                    "error": f"{type(exc).__name__}: Could not verify the supplied repository snapshot.",
                })
                continue
            hash_seconds = time.perf_counter() - hash_started
            if actual_hash != expected_hash:
                records.append({
                    "issue_id": issue_id,
                    "variant": None,
                    "status": "index_blocked_snapshot_hash_mismatch",
                    "metrics": None,
                    "snapshot_sha256_expected": expected_hash,
                    "snapshot_sha256": actual_hash,
                    "snapshot_hash_verified": False,
                    "snapshot_hash_seconds": round(hash_seconds, 6),
                    "error": "The repository snapshot content does not match the recorded SHA-256; it was not indexed.",
                })
                continue
            hash_verified = True
        else:
            hash_verified = None
        cache_key = (row["repository"].strip(), row["base_commit"].strip(), str(snapshot))
        index_reused = cache_key in index_cache
        if cache_key not in index_cache:
            try:
                chunks = index_repository(snapshot)
                if embedding_model_path is not None and embedding_provider is None:
                    model_load_started = time.perf_counter()
                    embedding_provider = SentenceTransformerProvider(str(embedding_model_path))
                    embedding_model_load_seconds = time.perf_counter() - model_load_started
                if embedding_provider is not None:
                    indexes, build_seconds, _ = build_retrievers(
                        chunks,
                        embedding_provider=embedding_provider,
                    )
                else:
                    indexes, build_seconds, _ = build_retrievers(chunks)
            except (OSError, RuntimeError, ValueError) as exc:
                records.append({
                    "issue_id": issue_id,
                    "variant": None,
                    "status": "index_failed",
                    "metrics": None,
                    "error": f"{type(exc).__name__}: {exc}",
                })
                continue
            index_cache[cache_key] = (indexes, build_seconds)
        else:
            indexes, build_seconds = index_cache[cache_key]

        issue_text = _compose_issue(row["issue_title"], row["issue_body"])
        try:
            issue_records = evaluate_retrieval_methods(issue_id, issue_text, indexes, relevant, top_k=top_k)
        except ValueError as exc:
            records.append({
                "issue_id": issue_id,
                "variant": None,
                "status": "evaluation_failed",
                "metrics": None,
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue
        for record in issue_records:
            record.update({
                "status": "completed",
                "repository": row["repository"].strip(),
                "base_commit": row["base_commit"].strip(),
                "snapshot_path": str(snapshot),
                "snapshot_sha256": actual_hash,
                "snapshot_sha256_expected": expected_hash or None,
                "snapshot_hash_verified": hash_verified,
                "snapshot_hash_seconds": round(hash_seconds, 6) if hash_seconds is not None else None,
                "language": row["language"].strip() or None,
                "split": row["split"].strip() or None,
                "label_type": sorted({
                    label["label_type"].strip()
                    for label in label_rows
                    if label["issue_id"].strip() == issue_id and label["decision"].strip().casefold() == "include"
                }),
                "index_build_seconds_by_method": {
                    name: round(seconds, 6) for name, seconds in build_seconds.items()
                },
                "index_build_seconds_for_snapshot": round(sum(build_seconds.values()), 6),
                "index_reused": index_reused,
                "indexed_chunk_count": len(next(iter(indexes.values())).chunks),
                "embedding_model_path": str(embedding_model_path) if embedding_model_path else None,
                "embedding_model_load_seconds": round(embedding_model_load_seconds, 6)
                if embedding_model_load_seconds is not None
                else None,
                "snapshot_hash_note": (
                    None if expected_hash else "No snapshot digest was supplied; snapshot integrity was not verified."
                ),
            })
            records.append(record)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8", newline="\n") as stream:
        for record in records:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return records


def _read_csv(path: Path, expected_fields: set[str], label: str) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = set(reader.fieldnames or [])
        if fields != expected_fields:
            unknown = sorted(fields - expected_fields)
            missing = sorted(expected_fields - fields)
            raise ValueError(f"Invalid {label} columns; unknown={unknown}, missing={missing}.")
        return [
            {key: (value or "") for key, value in row.items() if key is not None}
            for row in reader
        ]


def _safe_relative_path(value: str) -> str:
    normalized = value.strip().replace("\\", "/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts or ":" in normalized:
        raise ValueError(f"Unsafe relevant_path label: {value!r}.")
    return path.as_posix()


def _compose_issue(title: str, body: str) -> str:
    return "\n\n".join(part.strip() for part in (title, body) if part.strip())


if __name__ == "__main__":
    raise SystemExit(main())
