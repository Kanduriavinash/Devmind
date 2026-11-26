"""Generate SWE-bench-compatible patch predictions from an instance JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from devmind.logging_config import configure_logging
from devmind.swebench import generate_predictions, load_instances, select_instances, write_jsonl


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="devmind-swebench",
        description="Generate unverified DevMind patch predictions for selected SWE-bench Lite tasks.",
    )
    parser.add_argument("--instances", required=True, type=Path, help="SWE-bench Lite JSONL export")
    parser.add_argument("--instance-ids", required=True, nargs="+", help="Explicit task IDs to run")
    parser.add_argument("--repository-cache", type=Path, default=Path(".devmind/swebench"))
    parser.add_argument("--top-k", type=int, choices=range(1, 9), default=4, help="Maximum retrieved source snippets per issue")
    parser.add_argument("--context-chars", type=int, choices=range(500, 5001, 500), default=1500, help="Maximum source characters per snippet in the model prompt")
    parser.add_argument("--predictions", required=True, type=Path, help="Output in official harness JSONL format")
    parser.add_argument("--run-notes", required=True, type=Path, help="Output status JSONL; records patches as untested")
    args = parser.parse_args()
    configure_logging()
    try:
        rows = load_instances(args.instances)
        selected = select_instances(rows, args.instance_ids)
        predictions, notes = generate_predictions(
            selected,
            instance_ids=[row["instance_id"] for row in selected],
            repository_cache=args.repository_cache,
            top_k=args.top_k,
            context_chars=args.context_chars,
        )
        write_jsonl(args.predictions, predictions)
        write_jsonl(args.run_notes, notes)
        print(json.dumps({"selected": len(selected), "predictions": str(args.predictions), "run_notes": str(args.run_notes)}, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        parser.exit(2, f"devmind-swebench: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
