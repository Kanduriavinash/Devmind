"""Conservative review gate that separates candidate patches from verified fixes."""

from typing import Any


def review_candidate(candidate_patch: str | None, test_result: dict[str, Any] | None) -> dict[str, Any]:
    """Approve only when a patch exists and that patch's isolated tests genuinely passed."""
    if not candidate_patch:
        return {"verdict": "not_reviewable", "reason": "No candidate patch is available."}
    if not test_result or not test_result.get("executed"):
        return {"verdict": "unverified", "reason": "Candidate patch has no executed test result."}
    if test_result.get("mode") != "candidate_patch":
        return {"verdict": "unverified", "reason": "Tests did not run against the candidate patch."}
    if test_result.get("timed_out"):
        return {"verdict": "unverified", "reason": "Candidate patch tests timed out."}
    if test_result.get("passed") is not True or test_result.get("exit_code") != 0:
        return {"verdict": "changes_requested", "reason": "Candidate patch tests failed or returned a nonzero exit code."}
    return {"verdict": "tests_passed_review_required", "reason": "Candidate patch tests passed in isolation; human review is still required."}

