"""Explainable, dependency-free text analysis for software bug reports."""

from __future__ import annotations

import re
from collections import Counter

from devmind.models import IssueAnalysis

_STOP_WORDS = {
    "a", "about", "after", "again", "also", "an", "and", "any", "are", "as",
    "at", "be", "because", "been", "before", "being", "between", "bug", "but",
    "by", "can", "could", "did", "do", "does", "during", "each", "either",
    "else", "for", "from", "had", "has", "have", "how", "if", "in", "into",
    "is", "it", "its", "may", "might", "more", "most", "must", "neither",
    "no", "nor", "not", "of", "on", "once", "only", "or", "other", "our",
    "out", "over", "same", "should", "so", "some", "such", "than", "that",
    "the", "their", "then", "there", "these", "they", "this", "those", "through",
    "to", "under", "until", "up", "very", "was", "were", "what", "when", "where",
    "which", "while", "who", "why", "will", "with", "would", "you", "your",
}

# These small, inspectable vocabularies are deliberately described as heuristics,
# not as a trained classifier. Each matched signal contributes one category point.
_CATEGORY_SIGNALS = (
    ("exception", {"exception", "traceback", "crash", "crashes", "raises", "raise", "error", "errors", "failed", "failure", "fails"}),
    ("incorrect_result", {"wrong", "incorrect", "unexpected", "returns", "return", "result", "mismatch", "value", "output"}),
    ("performance", {"slow", "slower", "timeout", "timeouts", "performance", "memory", "hang", "hangs", "latency", "deadlock"}),
)


def analyze_issue(text: str, *, max_keywords: int = 12) -> IssueAnalysis:
    """Extract normalized terms, a heuristic category, and code-like hints.

    Tokenization understands snake_case and camelCase identifiers while retaining
    their complete spelling. Category selection uses exact token matches, avoiding
    accidental matches inside unrelated words (for example, ``terror``/``error``).
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Bug report must be a non-empty string.")
    if not isinstance(max_keywords, int) or isinstance(max_keywords, bool) or max_keywords < 1:
        raise ValueError("max_keywords must be a positive integer.")

    raw_tokens = re.findall(r"[A-Za-z][A-Za-z0-9_./-]*", text)
    terms: Counter[str] = Counter()
    normalized_tokens: list[str] = []
    for raw in raw_tokens:
        # Keep a useful identifier as a keyword and also expose its constituent
        # words so ``matchState`` can match ``match state`` in source code.
        identifier = raw.casefold().strip("./-")
        parts = re.sub(r"([a-z])([A-Z])", r"\1 \2", raw).casefold()
        parts = re.findall(r"[a-z]+|[0-9]+", parts)
        if identifier and len(identifier) > 1 and identifier not in _STOP_WORDS:
            terms[identifier] += 1
        for part in parts:
            if len(part) > 1 and part not in _STOP_WORDS and not part.isdigit():
                terms[part] += 1
                normalized_tokens.append(part)
    keywords = sorted(terms, key=lambda term: (-terms[term], term))[:max_keywords]
    token_counts = Counter(normalized_tokens)

    category_scores = {
        name: sum(token_counts[signal] for signal in signals)
        for name, signals in _CATEGORY_SIGNALS
    }
    winning_category, winning_score = max(category_scores.items(), key=lambda item: item[1])
    issue_type = winning_category if winning_score else "behavior"

    # Preserve file paths and dotted/snake/camel identifiers as useful retrieval
    # hints. These are extracted from the original casing before normalization.
    hints_set: set[str] = set()
    for match in re.findall(r"[A-Za-z_][A-Za-z0-9_./-]*", text):
        candidate = match.rstrip(".,:;()[]{}")
        if candidate and (
            "." in candidate
            or "/" in candidate
            or "_" in candidate
            or re.search(r"[a-z][A-Z]", candidate)
        ):
            hints_set.add(candidate)
    hints = sorted(hints_set)
    summary = " ".join(text.strip().split())[:240]
    return IssueAnalysis(summary, keywords, issue_type, hints)
