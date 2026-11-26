"""Shared, serializable data structures used by DevMind workflow stages."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class IssueAnalysis:
    """Text features extracted from a natural-language bug report."""

    summary: str
    keywords: list[str]
    issue_type: str
    component_hints: list[str]


@dataclass(frozen=True)
class CodeChunk:
    """A traceable source-code unit returned by the repository indexer."""

    path: str
    name: str
    kind: str
    start_line: int
    end_line: int
    content: str


@dataclass(frozen=True)
class Evidence:
    """A retrieved code chunk and its lexical relevance score."""

    chunk: CodeChunk
    score: float


@dataclass(frozen=True)
class Investigation:
    """Evidence-linked findings; hypotheses are explicitly not verified facts."""

    findings: list[str]
    hypotheses: list[str]
    uncertainties: list[str]
    evidence_references: dict[str, list[str]] = field(default_factory=dict)
    source: str = "heuristic"


@dataclass
class RunReport:
    """Result of a single analysis run, suitable for JSON serialization."""

    status: str
    issue: str
    analysis: dict[str, Any]
    plan: list[str]
    evidence: list[dict[str, Any]]
    investigation: dict[str, Any]
    candidate_patch: str | None = None
    baseline_test_result: dict[str, Any] = field(default_factory=dict)
    test_result: dict[str, Any] = field(default_factory=dict)
    review: dict[str, Any] = field(default_factory=dict)
    repair_attempts: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-compatible report data."""
        return asdict(self)

