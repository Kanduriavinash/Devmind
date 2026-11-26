"""Reproduce static import checks on the two repositories used for the demo."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

from devmind.github_repo import download_public_repository
from devmind.pipeline import run_analysis


CASES = (
    (
        "https://github.com/Kanduriavinash/QuickCart",
        "When I add an item to the cart, it appears immediately but disappears after reloading the page. Find the cart persistence and initialization code and explain what behavior the repository currently implements.",
    ),
    (
        "https://github.com/Kanduriavinash/cricket-scorer-pro",
        "Each legal delivery should increment the over by exactly one ball. Find the scoring logic and show whether the current code adds one ball per delivery.",
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/github_repository_import_smoke_reproduction.json"),
        help="new JSON output path; existing files are never overwritten",
    )
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing output: {output}")

    workspace = Path(".devmind/live-github-import-smoke")
    records = []
    for url, issue in CASES:
        downloaded = download_public_repository(url, workspace)
        report = run_analysis(issue, downloaded.path, limit=8)
        report.analysis.update(
            {
                "repository_source": "Public GitHub archive",
                "repository_name": downloaded.full_name,
                "repository_url": url,
                "repository_default_branch": downloaded.default_branch,
                "repository_commit_sha": downloaded.commit_sha,
                "repository_archive_sha256": downloaded.archive_sha256,
                "repository_pushed_at": downloaded.pushed_at,
                "repository_skipped_symlinks": downloaded.skipped_symlinks,
            }
        )
        records.append({"issue": issue, "report": report.to_dict()})

    output.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "analysis_mode": "static retrieval only; no repository code or tests executed",
        "records": records,
    }
    output.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    for item in records:
        analysis = item["report"]["analysis"]
        print(
            f"{analysis['repository_name']} {analysis['repository_commit_sha']} "
            f"archive_sha256={analysis['repository_archive_sha256']} "
            f"evidence={len(item['report']['evidence'])}"
        )
    print(f"saved {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
