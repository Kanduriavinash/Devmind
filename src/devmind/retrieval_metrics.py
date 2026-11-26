"""Standard ranked-retrieval metrics for binary relevance labels."""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence


def score_file_ranking(
    ranked_files: Sequence[str],
    relevant_files: Iterable[str],
    *,
    cutoffs: Sequence[int] = (1, 3, 5),
) -> dict[str, float | int]:
    """Score one ranking against a non-empty set of relevant file paths.

    Duplicate ranked paths are ignored after their first occurrence. Precision
    uses the requested cutoff as its denominator, even when fewer results exist.
    An empty relevance set is rejected because it represents missing labels, not
    a meaningful zero-relevance query.
    """
    relevant = {path for path in relevant_files if isinstance(path, str) and path}
    if not relevant:
        raise ValueError("At least one labeled relevant file is required.")
    if not cutoffs or any(not isinstance(k, int) or isinstance(k, bool) or k < 1 for k in cutoffs):
        raise ValueError("cutoffs must contain positive integers.")
    if len(set(cutoffs)) != len(cutoffs):
        raise ValueError("cutoffs must be unique.")
    if any(not isinstance(path, str) or not path for path in ranked_files):
        raise ValueError("ranked file paths must be non-empty strings.")

    ranking = _unique_in_order(ranked_files)
    result: dict[str, float | int] = {"relevant_count": len(relevant), "retrieved_unique_count": len(ranking)}
    first_relevant_rank: int | None = None
    for rank, path in enumerate(ranking, start=1):
        if path in relevant and first_relevant_rank is None:
            first_relevant_rank = rank

    result["mrr"] = 1.0 / first_relevant_rank if first_relevant_rank is not None else 0.0
    for cutoff in cutoffs:
        top = ranking[:cutoff]
        hits = sum(path in relevant for path in top)
        result[f"precision_at_{cutoff}"] = hits / cutoff
        result[f"recall_at_{cutoff}"] = hits / len(relevant)
        dcg = sum(1.0 / math.log2(rank + 1) for rank, path in enumerate(top, start=1) if path in relevant)
        ideal_hits = min(len(relevant), cutoff)
        idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
        result[f"ndcg_at_{cutoff}"] = dcg / idcg if idcg else 0.0
    return result


def _unique_in_order(items: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result
