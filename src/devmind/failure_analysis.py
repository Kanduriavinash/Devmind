"""Extract bounded, repository-relevant context from failed sandbox tests."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any, Mapping

_ANSI_ESCAPE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
_FAILED_TEST_PATTERNS = (
    re.compile(r"^\s*(?:FAILED|ERROR)\s+([^\s]+)", re.MULTILINE),
    re.compile(r"^\s*not ok\s+\d+\s*-\s*(.+)$", re.MULTILINE),
    re.compile(r"^\s*FAIL:\s*(.+)$", re.MULTILINE),
    re.compile(r"^\s*✖\s+(.+)$", re.MULTILINE),
)
_PYTHON_FRAME = re.compile(
    r"File\s+[\"'](?P<path>[^\"']+)[\"'],\s*line\s+(?P<line>\d+)"
    r"(?:,\s*in\s+(?P<function>[A-Za-z_][\w.< >]*))?"
)
_JS_FRAME = re.compile(
    r"^\s*at\s+(?:(?P<function>.*?)\s+\()?"
    r"(?P<path>(?:[A-Za-z]:)?[^()\s]+):(?P<line>\d+):\d+\)?\s*$",
    re.MULTILINE,
)
_JAVA_FRAME = re.compile(
    r"^\s*at\s+(?P<function>[\w.$<>]+)\((?P<path>[^():]+\.java):(?P<line>\d+)\)\s*$",
    re.MULTILINE,
)
_GO_FRAME = re.compile(
    r"^\s*(?P<path>[\w./-]+\.go):(?P<line>\d+)(?:\s|$)", re.MULTILINE
)
_ERROR_TYPE = re.compile(
    r"\b([A-Z][A-Za-z0-9]*(?:Error|Exception|Failure))\b"
)
_IDENTIFIER = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*(?:\.[A-Za-z_$][A-Za-z0-9_$]*)*")
_GENERIC_IDENTIFIERS = {
    "at", "line", "file", "workspace", "home", "usr", "local", "tmp",
    "test", "tests", "error", "failed", "failure", "assertionerror",
}


@dataclass(frozen=True)
class FailureAnalysis:
    """Safe, concise failure signals used to refine retrieval and retry prompts."""

    failed_tests: list[str]
    stack_frames: list[dict[str, Any]]
    error_types: list[str]
    retrieval_terms: list[str]
    summary: str

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-compatible failure analysis without raw test output."""
        return asdict(self)


def analyze_test_failure(test_result: Mapping[str, Any]) -> FailureAnalysis:
    """Extract test names, source frames, and error classes from bounded output.

    Raw stdout and stderr are intentionally excluded from the returned value. The
    caller may keep the captured output in the local run record, but only these
    structured signals should be sent back to an external model provider.
    """
    output = "\n".join(
        str(test_result.get(key, "")) for key in ("stdout", "stderr") if test_result.get(key)
    )
    output = _ANSI_ESCAPE.sub("", output)

    failed_tests = _unique_matches(_FAILED_TEST_PATTERNS, output, limit=10)
    frames = _extract_frames(output)
    error_types = list(dict.fromkeys(_ERROR_TYPE.findall(output)))[:8]

    term_sources = [*failed_tests, *error_types]
    for frame in frames:
        term_sources.extend((frame.get("path", ""), frame.get("function", "")))
    retrieval_terms: list[str] = []
    seen: set[str] = set()
    for match in _IDENTIFIER.findall(" ".join(term_sources)):
        if match.lower() in _GENERIC_IDENTIFIERS or len(match) < 2:
            continue
        if match not in seen:
            seen.add(match)
            retrieval_terms.append(match)
        if len(retrieval_terms) >= 24:
            break

    details: list[str] = []
    if failed_tests:
        details.append("failed tests: " + ", ".join(failed_tests[:5]))
    if frames:
        frame_labels = [
            ":".join(
                part for part in (
                    str(frame.get("path", "")),
                    str(frame.get("line", "")) if frame.get("line") is not None else "",
                ) if part
            )
            + (f" in {frame['function']}" if frame.get("function") else "")
            for frame in frames[:5]
        ]
        details.append("source frames: " + ", ".join(frame_labels))
    if error_types:
        details.append("error types: " + ", ".join(error_types[:5]))
    summary = "Sandboxed tests failed."
    if details:
        summary += " " + "; ".join(details) + "."

    return FailureAnalysis(
        failed_tests=failed_tests,
        stack_frames=frames,
        error_types=error_types,
        retrieval_terms=retrieval_terms,
        summary=summary,
    )


def build_failure_retrieval_query(issue: str, failure: FailureAnalysis) -> str:
    """Combine the original issue with extracted test and source-location cues."""
    cues = " ".join(failure.retrieval_terms)
    if not cues:
        cues = failure.summary
    return f"{issue.strip()}\nFailure context: {cues}".strip()


def provider_failure_feedback(
    test_result: Mapping[str, Any], failure: FailureAnalysis
) -> dict[str, Any]:
    """Build a provider-safe feedback object without raw stdout/stderr values."""
    return {
        "executed": test_result.get("executed") is True,
        "passed": test_result.get("passed") is True,
        "timed_out": test_result.get("timed_out") is True,
        "exit_code": test_result.get("exit_code"),
        "runner": test_result.get("runner"),
        "failure_analysis": failure.to_dict(),
    }


def _unique_matches(
    patterns: tuple[re.Pattern[str], ...], text: str, *, limit: int
) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for pattern in patterns:
        for match in pattern.finditer(text):
            value = " ".join(match.group(1).strip().split())
            if value and value not in seen:
                seen.add(value)
                values.append(value[:240])
                if len(values) >= limit:
                    return values
    return values


def _extract_frames(text: str) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str | None]] = set()
    for pattern in (_PYTHON_FRAME, _JAVA_FRAME, _JS_FRAME, _GO_FRAME):
        for match in pattern.finditer(text):
            path = _normalize_path(match.group("path"))
            function = match.groupdict().get("function")
            function = " ".join(function.split())[:120] if function else None
            try:
                line = int(match.group("line"))
            except (TypeError, ValueError):
                line = None
            key = (path, line or 0, function)
            if not path or key in seen:
                continue
            if path.startswith(("node:internal", "internal/")):
                continue
            seen.add(key)
            frames.append({"path": path, "line": line, "function": function})
            if len(frames) >= 12:
                return frames
    return frames


def _normalize_path(path: str) -> str:
    value = path.strip().replace("\\", "/")
    if value.startswith("/workspace/"):
        value = value[len("/workspace/"):]
    elif value.startswith("./"):
        value = value[2:]
    return value[:300]
