"""Generate and validate minimal, evidence-grounded source diffs across supported languages."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from devmind.providers import ChatProvider


class InvalidCandidatePatch(ValueError):
    """Raised when model output is not a safe, non-empty source unified diff."""


def generate_candidate_patch(
    issue: str,
    evidence: list[dict[str, Any]],
    provider: ChatProvider,
    *,
    test_feedback: dict[str, Any] | None = None,
    investigation: list[str] | None = None,
    repository_metadata: dict[str, Any] | None = None,
    baseline_test_result: dict[str, Any] | None = None,
    generation_trace: dict[str, Any] | None = None,
    max_evidence_chars: int = 5000,
) -> str | None:
    """Request a constrained diff; returns ``None`` for malformed/untrusted output."""
    if not evidence:
        return None
    if not isinstance(max_evidence_chars, int) or isinstance(max_evidence_chars, bool) or max_evidence_chars < 1:
        raise ValueError("max_evidence_chars must be a positive integer.")
    context = "\n\n".join(
        f"# Evidence {item.get('evidence_id', f'E{index}')} | "
        f"{item['path']}:{item['start_line']}-{item['end_line']}\n"
        f"{str(item['content'])[:max_evidence_chars]}"
        for index, item in enumerate(evidence[:8], start=1)
    )
    feedback = ""
    if test_feedback is not None:
        feedback = "\n\nPrevious isolated test result (use it to revise the patch):\n" + json.dumps(test_feedback, ensure_ascii=False)[:8000]
    findings = "\n".join(f"- {item}" for item in (investigation or [])[:5]) or "No separate investigation hypotheses were supplied."
    metadata = json.dumps(repository_metadata or {"language": "auto-detected from source files"}, ensure_ascii=False)[:2000]
    baseline = ""
    if baseline_test_result is not None:
        baseline_fields = {
            key: baseline_test_result.get(key)
            for key in ("runner", "test_command", "executed", "passed", "timed_out", "exit_code", "stdout", "stderr")
            if key in baseline_test_result
        }
        baseline = "\n\nBaseline regression test run before patch generation:\n" + json.dumps(
            baseline_fields, ensure_ascii=False
        )[:5000]
    prompt = (
        "Propose a minimal unified diff for the bug report. Use only the supplied repository evidence. "
        "Change only evidenced source files and keep every path repository-relative. Start each changed-file section with exactly these "
        "three header lines: `diff --git a/<path> b/<path>`, `--- a/<path>`, then `+++ b/<path>`, followed by a valid @@ hunk. "
        "For example, use `diff --git a/calculator.py b/calculator.py`, `--- a/calculator.py`, and `+++ b/calculator.py`. "
        "Do not put a filename on a separate line, emit a bare --- separator, or add a code fence. Count hunk lines exactly: "
        "context and deleted lines count toward the old range, while context and added lines count toward the new range. "
        "Keep unchanged lines from the supplied evidence as context. Do not omit any original line between changed lines, "
        "including docstrings, and do not delete and re-add identical lines. For a line replacement, include the old line "
        "exactly once with a `-` prefix followed by its replacement with a `+` prefix; never repeat that old line as context. "
        "Preserve values needed for the requested operation: complete the operation successfully before clearing or changing "
        "an identifier or state value that the operation uses. "
        "Explain reasoning only through changed code; return the diff only. "
        "If evidence is insufficient, reply exactly "
        "INSUFFICIENT_EVIDENCE. Do not claim tests passed.\n\n"
        f"Bug report:\n{issue[:8000]}\n\nRepository metadata:\n{metadata}\n\nInvestigation hypotheses (unverified):\n{findings}\n\n"
        f"Retrieved evidence:\n{context}{baseline}{feedback}"
    )
    # A trailing context line may contain one significant space; strip line breaks only.
    raw_response = provider.complete(prompt)
    proposal = _normalize_hunk_counts(raw_response.strip("\r\n"))
    if generation_trace is not None:
        generation_trace.update({
            "model": str(getattr(provider, "model", "unknown")),
            "prompt": prompt,
            "raw_model_response": raw_response,
            "candidate_patch": proposal,
            "hunk_count_normalization_changed": proposal != raw_response.strip("\r\n"),
        })
    try:
        changed_paths = validate_unified_diff(proposal, allowed_paths={item["path"] for item in evidence})
    except InvalidCandidatePatch as exc:
        if generation_trace is not None:
            generation_trace["validation"] = {"valid": False, "reason": str(exc)}
        return None
    if generation_trace is not None:
        generation_trace["validation"] = {"valid": True, "changed_paths": changed_paths}
    return proposal


def _normalize_hunk_counts(patch: str) -> str:
    """Recount unified-diff hunk lines so small-model count errors stay patchable."""
    lines = patch.splitlines()
    index = 0
    while index < len(lines):
        match = re.match(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)$", lines[index])
        if match is None:
            index += 1
            continue

        old_start, old_declared, new_start, new_declared, suffix = match.groups()
        old_count = 0
        new_count = 0
        end = index + 1
        while end < len(lines) and not lines[end].startswith("@@ ") and not lines[end].startswith("diff --git "):
            line = lines[end]
            if (line.startswith("--- a/") or line == "--- /dev/null") and end + 1 < len(lines) and lines[end + 1].startswith("+++ "):
                break
            if line.startswith(" "):
                old_count += 1
                new_count += 1
            elif line.startswith("-"):
                old_count += 1
            elif line.startswith("+"):
                new_count += 1
            elif line.startswith("\\"):
                pass
            else:
                # Small local models sometimes append a fallback or explanation after
                # a complete diff. Stop at the first non-diff line; tests still decide
                # whether the retained patch is applicable and correct.
                lines = lines[:end]
                break
            end += 1

        if old_count != int(old_declared or 1) or new_count != int(new_declared or 1):
            lines[index] = f"@@ -{old_start},{old_count} +{new_start},{new_count} @@{suffix}"
        index = end
    return "\n".join(lines)


def validate_unified_diff(patch: str, *, allowed_paths: set[str] | None = None) -> list[str]:
    """Validate diff framing, supported relative source paths, hunks, and non-no-op edits.

    Returns unique repository-relative changed paths. Actual patch application is
    still performed only inside the Docker sandbox, where `git apply` checks context.
    """
    if not isinstance(patch, str) or not patch.strip():
        raise InvalidCandidatePatch("Candidate patch must be non-empty text.")
    lines = patch.splitlines()
    if not lines or (not lines[0].startswith("diff --git ") and not lines[0].startswith("--- ")):
        raise InvalidCandidatePatch("Candidate must begin with a unified-diff file header.")
    boundaries = [i for i, line in enumerate(lines) if line.startswith("diff --git ")]
    if boundaries and boundaries[0] != 0:
        raise InvalidCandidatePatch("Unexpected text appears before the diff.")
    starts = boundaries or [0]
    ends = starts[1:] + [len(lines)]
    changed_paths: list[str] = []
    for start, end in zip(starts, ends):
        section = lines[start:end]
        git_old = git_new = None
        offset = 0
        if section[0].startswith("diff --git "):
            match = re.fullmatch(r"diff --git a/([^\s]+) b/([^\s]+)", section[0])
            if not match:
                raise InvalidCandidatePatch("Git diff paths must be simple repository-relative names without quoting.")
            git_old, git_new = match.groups()
            offset = 1
        old_line = next((i for i, line in enumerate(section[offset:], start=offset) if line.startswith("--- ")), None)
        if old_line is None or old_line + 1 >= len(section) or not section[old_line + 1].startswith("+++ "):
            raise InvalidCandidatePatch("Each diff file needs matching --- and +++ headers.")
        old_name = section[old_line][4:]
        new_name = section[old_line + 1][4:]
        old_path = _validate_patch_path(old_name, "a/") if old_name != "/dev/null" else None
        new_path = _validate_patch_path(new_name, "b/") if new_name != "/dev/null" else None
        if old_path is None and new_path is None:
            raise InvalidCandidatePatch("A diff cannot delete and create /dev/null.")
        if git_old is not None:
            expected = old_path or new_path
            if (old_path is not None and old_path != git_old) or (new_path is not None and new_path != git_new):
                raise InvalidCandidatePatch("Git diff paths do not match the file headers.")
            if old_path is None and git_old != expected or new_path is None and git_new != expected:
                raise InvalidCandidatePatch("New or deleted file paths do not match the Git diff header.")
        path = new_path or old_path
        if path is None:
            raise InvalidCandidatePatch("Diff path could not be validated.")
        hunks = [line for line in section[old_line + 2:] if line.startswith("@@")]
        if not hunks or any(not re.match(r"^@@ -\d+(?:,\d+)? \+\d+(?:,\d+)? @@(?: .*)?$", hunk) for hunk in hunks):
            raise InvalidCandidatePatch("Each changed file needs a valid unified-diff hunk.")
        edits = [line for line in section[old_line + 2:] if (line.startswith("+") and not line.startswith("+++")) or (line.startswith("-") and not line.startswith("---"))]
        if not edits:
            raise InvalidCandidatePatch("No-op patches are not accepted.")
        changed_paths.append(path)
    unique_paths = list(dict.fromkeys(changed_paths))
    if allowed_paths is not None and any(path not in allowed_paths for path in unique_paths):
        raise InvalidCandidatePatch("Diff changes a file outside the retrieved evidence paths.")
    return unique_paths


def write_candidate_patch(patch: str, destination: str | Path, repository: str | Path) -> Path:
    """Save a validated diff outside the source repository for human review."""
    validate_unified_diff(patch)
    repository_root = Path(repository).expanduser().resolve(strict=True)
    target = Path(destination).expanduser().resolve()
    try:
        target.relative_to(repository_root)
    except ValueError:
        pass
    else:
        raise ValueError("Candidate patch output must be outside the selected source repository.")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(patch.rstrip() + "\n", encoding="utf-8")
    return target


# All source file extensions that DevMind can index, generate patches for, and test.
_SUPPORTED_EXTENSIONS = {
    ".py",                              # Python
    ".js", ".jsx", ".mjs", ".cjs",      # JavaScript
    ".html", ".htm",                      # HTML with inline JavaScript
    ".ts", ".tsx",                       # TypeScript
    ".java",                            # Java
    ".c", ".h", ".cpp", ".hpp",         # C / C++
    ".cc", ".cxx", ".hxx", ".hh",       # C / C++ (alternate extensions)
    ".go",                              # Go
    ".rs",                              # Rust
    ".cs",                              # C#
    ".rb",                              # Ruby
    ".php",                             # PHP
    ".kt", ".kts",                      # Kotlin
    ".swift",                           # Swift
}


def _validate_patch_path(raw_path: str, prefix: str) -> str:
    if not raw_path.startswith(prefix):
        raise InvalidCandidatePatch("Diff paths must use matching a/ and b/ relative prefixes.")
    value = raw_path[len(prefix):]
    path = PurePosixPath(value)
    if (
        not value
        or "\\" in value
        or ":" in value
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in value.split("/"))
        or path.suffix.lower() not in _SUPPORTED_EXTENSIONS
    ):
        raise InvalidCandidatePatch("Only repository-relative source paths without traversal are accepted for supported languages.")
    return value
