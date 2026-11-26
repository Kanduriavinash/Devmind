"""Command-line entry point for DevMind's local analysis workflow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from devmind.logging_config import configure_logging
from devmind.code_agent import write_candidate_patch
from devmind.orchestrator import run_repair
from devmind.pipeline import run_analysis
from devmind.reviewer import review_candidate
from devmind.sandbox import SandboxUnavailable, run_tests


def main() -> int:
    parser = argparse.ArgumentParser(prog="devmind", description="Analyze a source repository against a bug report. Supports Python, JavaScript, TypeScript, Java, C/C++, Go, Rust, C#, Ruby, PHP, Kotlin, and Swift.")
    parser.add_argument("--repo", required=True, type=Path, help="Path to a supported source repository")
    parser.add_argument("--issue", required=True, help="Natural-language bug report")
    parser.add_argument("--top-k", type=int, default=8, help="Number of evidence chunks to retrieve (default: 8)")
    parser.add_argument("--embedding-model", type=Path, help="Optional local Sentence Transformers model folder for vector retrieval")
    parser.add_argument("--vector-index", type=Path, help="Optional saved vector index directory (must be outside the source repository)")
    parser.add_argument("--model-investigation", action="store_true", help="Ask the configured model for evidence-cited investigation hypotheses")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    parser.add_argument("--patch-output", type=Path, help="Optional path for saving the validated candidate diff outside the source repository")
    parser.add_argument("--generate-patch", action="store_true", help="Request a candidate patch from configured provider")
    parser.add_argument("--test", action="store_true", help="Run the configured test runner inside the Docker sandbox")
    parser.add_argument("--repair", action="store_true", help="Run a bounded patch/test feedback loop (requires model and Docker)")
    parser.add_argument("--max-attempts", type=int, choices=range(1, 4), default=2, help="Repair-loop attempt limit (1–3; default: 2)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    configure_logging(verbose=args.verbose)
    try:
        if args.repair and (args.generate_patch or args.test):
            parser.error("--repair already includes patch generation and isolated tests; do not combine it with --generate-patch or --test")
        if args.vector_index and not args.embedding_model:
            parser.error("--vector-index requires --embedding-model")
        report = run_analysis(
            args.issue,
            args.repo,
            limit=args.top_k,
            generate_patch=args.generate_patch,
            model_investigation=args.model_investigation,
            embedding_model_path=args.embedding_model,
            vector_index_directory=args.vector_index,
        )
        if args.repair:
            repair = run_repair(
                args.issue,
                report.evidence,
                args.repo,
                max_attempts=args.max_attempts,
                investigation=report.investigation.get("hypotheses", []),
                repository_metadata={"root_name": args.repo.name, "language": "auto-detected from source files"},
            )
            report.status = repair["status"]
            report.candidate_patch = repair["candidate_patch"]
            report.test_result = repair["test_result"]
            report.review = repair["review"]
            report.repair_attempts = repair["attempts"]
        elif args.test:
            try:
                report.test_result = run_tests(args.repo, candidate_patch=report.candidate_patch)
            except (SandboxUnavailable, ValueError) as exc:
                report.test_result = {"executed": False, "passed": False, "reason": str(exc)}
        if args.patch_output:
            if not report.candidate_patch:
                parser.error("--patch-output requires a valid candidate patch in this run")
            write_candidate_patch(report.candidate_patch, args.patch_output, args.repo)
        report.review = review_candidate(report.candidate_patch, report.test_result)
        if report.review["verdict"] == "tests_passed_review_required":
            report.status = "tests_passed_review_required"
        elif report.review["verdict"] == "changes_requested":
            report.status = "candidate_patch_tests_failed"
        serialized = json.dumps(report.to_dict(), indent=2, ensure_ascii=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized + "\n", encoding="utf-8")
        print(serialized)
        return 0
    except (OSError, ValueError, RuntimeError, SyntaxError) as exc:
        parser.exit(2, f"devmind: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())

