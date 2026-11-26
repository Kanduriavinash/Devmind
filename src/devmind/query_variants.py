"""Deterministic and inspectable query variants for retrieval experiments."""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Literal

from devmind.analyzer import analyze_issue

TRANSFORMATION_VERSION = "devmind-query-v1"
VARIANT_ORDER = ("raw", "normalized", "keywords_identifiers", "structured")
_CODE_TERM = re.compile(r"[A-Za-z_][A-Za-z0-9_./\\-]*")


@dataclass(frozen=True)
class QueryVariant:
    """One generated query plus the inputs needed to reproduce it."""

    variant: Literal["raw", "normalized", "keywords_identifiers", "structured"]
    original_text: str
    normalized_text: str
    keywords: tuple[str, ...]
    identifiers: tuple[str, ...]
    component_hints: tuple[str, ...]
    category: str
    transformation_version: str
    generated_query: str

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible audit record."""
        return asdict(self)


def normalize_issue_text(text: str) -> str:
    """Apply only Unicode compatibility normalization and whitespace folding."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Bug report must be a non-empty string.")
    normalized = unicodedata.normalize("NFKC", text)
    return " ".join(normalized.replace("\r\n", "\n").replace("\r", "\n").split()).casefold()


def build_query_variants(text: str, *, max_keywords: int = 12) -> tuple[QueryVariant, ...]:
    """Create four fixed query conditions without adding inferred terms.

    ``structured`` includes the rule-based category only when a non-default
    category signal matched. The original report is retained verbatim in every
    record, even though normalized and enriched variants differ from it.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Bug report must be a non-empty string.")
    analysis = analyze_issue(text, max_keywords=max_keywords)
    normalized = normalize_issue_text(text)
    identifiers = _extract_identifiers(text)
    keywords = tuple(analysis.keywords)
    hints = tuple(analysis.component_hints)

    variants: list[QueryVariant] = []
    for name in VARIANT_ORDER:
        terms: list[str] = []
        if name == "raw":
            query = text
        elif name == "normalized":
            query = normalized
        else:
            query = normalized
            terms.extend(keywords)
            terms.extend(identifiers)
            if name == "structured":
                terms.extend(hints)
                if analysis.issue_type != "behavior":
                    terms.append(analysis.issue_type)
            query = " ".join([query, *terms]).strip()

        variants.append(
            QueryVariant(
                variant=name,  # type: ignore[arg-type]
                original_text=text,
                normalized_text=normalized,
                keywords=keywords,
                identifiers=identifiers,
                component_hints=hints,
                category=analysis.issue_type,
                transformation_version=TRANSFORMATION_VERSION,
                generated_query=query,
            )
        )
    return tuple(variants)


def _extract_identifiers(text: str) -> tuple[str, ...]:
    """Return distinct code-like tokens in first-seen order, without guessing."""
    identifiers: list[str] = []
    seen: set[str] = set()
    for match in _CODE_TERM.findall(text):
        candidate = match.strip("./\\-")
        is_identifier = (
            "_" in candidate
            or "/" in match
            or "\\" in match
            or "." in candidate
            or re.search(r"[a-z][A-Z]", candidate) is not None
            or re.search(r"[A-Za-z]\d|\d[A-Za-z]", candidate) is not None
        )
        key = candidate.casefold()
        if is_identifier and candidate and key not in seen:
            identifiers.append(candidate)
            seen.add(key)
    return tuple(identifiers)
