"""Run known Python and Node patches through DevMind's non-root Docker sandbox."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

from devmind.sandbox import run_tests


def tree_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    for file in sorted(item for item in path.rglob("*") if item.is_file() and not item.is_symlink()):
        digest.update(file.relative_to(path).as_posix().encode("utf-8"))
        digest.update(file.read_bytes())
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("reports/sandbox-nonroot-docker-smoke-reproduction.json"),
        help="new JSON output path; existing files are never overwritten",
    )
    args = parser.parse_args()
    output = args.output.expanduser().resolve()
    if output.exists():
        parser.error(f"refusing to overwrite existing output: {output}")

    root = Path(__file__).resolve().parents[1]
    fixtures = (
        {
            "name": "quickcart-cart-reload",
            "path": root / "examples/quickcart-cart-reload-buggy",
            "image": "devmind-sandbox:node22",
            "runner": "node",
            "patch": '''diff --git a/index.html b/index.html
--- a/index.html
+++ b/index.html
@@ -10,3 +10,4 @@
     window.addEventListener("load", function () {
+      loadCartFromStorage();
       updateCartDisplay();
     });
''',
        },
        {
            "name": "safe-divide-python",
            "path": root / "examples/buggy_project",
            "image": "devmind-sandbox:py312",
            "runner": "pytest",
            "patch": '''diff --git a/calculator.py b/calculator.py
--- a/calculator.py
+++ b/calculator.py
@@ -4,3 +4,5 @@
 def safe_divide(numerator: float, denominator: float) -> float | None:
     """Divide two numbers, returning None when denominator is zero."""
+    if denominator == 0:
+        return None
     return numerator / denominator
''',
        },
    )

    results = []
    for fixture in fixtures:
        before = tree_sha256(fixture["path"])
        baseline = run_tests(
            fixture["path"], image=fixture["image"], test_runner=fixture["runner"], timeout=60
        )
        candidate = run_tests(
            fixture["path"],
            candidate_patch=fixture["patch"],
            image=fixture["image"],
            test_runner=fixture["runner"],
            timeout=60,
        )
        after = tree_sha256(fixture["path"])
        image_id = subprocess.check_output(
            ["docker", "image", "inspect", fixture["image"], "--format", "{{.Id}}"],
            text=True,
        ).strip()
        image_user = subprocess.check_output(
            ["docker", "image", "inspect", fixture["image"], "--format", "{{.Config.User}}"],
            text=True,
        ).strip()
        results.append(
            {
                "fixture": fixture["name"],
                "image": fixture["image"],
                "image_id": image_id,
                "image_user": image_user,
                "runner": fixture["runner"],
                "baseline": baseline,
                "candidate": candidate,
                "fixture_sha256_before": before,
                "fixture_sha256_after": after,
                "fixture_unchanged": before == after,
            }
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "created_at_utc": datetime.now(UTC).isoformat(),
        "docker_server_version": subprocess.check_output(
            ["docker", "version", "--format", "{{.Server.Version}}"], text=True
        ).strip(),
        "runtime_uid_gid": "10001:10001",
        "network": "none",
        "capabilities": "all dropped",
        "read_only_root": True,
        "target_repository_code_executed_on_host": False,
        "fixtures": results,
    }
    output.write_text(json.dumps(artifact, indent=2), encoding="utf-8")
    valid = all(
        row["baseline"]["executed"]
        and not row["baseline"]["passed"]
        and row["candidate"]["executed"]
        and row["candidate"]["passed"]
        and row["candidate"]["container_user"] == "10001:10001"
        and row["image_user"] == "10001:10001"
        and row["fixture_unchanged"]
        for row in results
    )
    for row in results:
        print(
            f"{row['fixture']}: baseline_passed={row['baseline']['passed']} "
            f"candidate_passed={row['candidate']['passed']} user={row['image_user']} "
            f"source_unchanged={row['fixture_unchanged']}"
        )
    print(f"saved {output}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
