"""CLI entry point for controlled three-method evaluation runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from devmind.evaluation_runner import run_comparison
from devmind.logging_config import configure_logging


def main() -> int:
    parser = argparse.ArgumentParser(prog="devmind-evaluate", description="Compare DevMind bug-fixing approaches on the same issue set.")
    parser.add_argument("--issues", required=True, type=Path, help="JSON file containing an array of issue input records")
    parser.add_argument("--output", required=True, type=Path, help="JSON evaluation report path")
    parser.add_argument("--raw-records", type=Path, help="Optional append-only JSON Lines run record path")
    parser.add_argument("--max-attempts", type=int, choices=range(1, 4), default=2)
    args = parser.parse_args()
    configure_logging()
    try:
        issues = json.loads(args.issues.read_text(encoding="utf-8"))
        if not isinstance(issues, list):
            raise ValueError("The issues file must contain a JSON array.")
        result = run_comparison(issues, max_attempts=args.max_attempts, output_path=args.raw_records)
        serialized = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
        print(serialized)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.exit(2, f"devmind-evaluate: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())

