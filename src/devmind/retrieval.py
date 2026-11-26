"""Offline sparse TF-IDF retrieval over traceable source-code chunks."""

from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Mapping
from typing import Protocol

from devmind.models import CodeChunk, Evidence


class TfidfIndex:
    """Small in-memory sparse vector index using cosine similarity.

    This is a classical lexical vector model, not a neural semantic embedding.
    """

    def __init__(self, chunks: list[CodeChunk]):
        self.chunks = chunks
        self.document_terms = [
            _add_singular_variants(Counter(_tokens(f"{c.name} {c.path} {c.content}")))
            for c in chunks
        ]
        document_frequency: Counter[str] = Counter()
        for terms in self.document_terms:
            document_frequency.update(terms.keys())
        total = len(chunks)
        self.inverse_document_frequency = {
            term: math.log((total + 1) / (frequency + 1)) + 1
            for term, frequency in document_frequency.items()
        }
        self.vectors = [self._weighted_vector(terms) for terms in self.document_terms]
        self.norms = [_norm(vector) for vector in self.vectors]

    def search(self, query: str, *, limit: int = 8) -> list[Evidence]:
        """Return top chunks by TF-IDF cosine score with deterministic tie breaks."""
        if limit < 1:
            raise ValueError("limit must be positive.")
        query_terms = _add_singular_variants(Counter(_tokens(query)))
        if not query_terms or not self.chunks:
            return []
        query_vector = self._weighted_vector(query_terms, include_unknown=True)
        query_norm = _norm(query_vector)
        if query_norm == 0:
            return []
        ranked: list[Evidence] = []
        for index, vector in enumerate(self.vectors):
            if not self.norms[index]:
                continue
            dot = sum(weight * vector.get(term, 0.0) for term, weight in query_vector.items())
            score = dot / (query_norm * self.norms[index])
            if score > 0:
                ranked.append(Evidence(self.chunks[index], round(score, 6)))
        return sorted(ranked, key=lambda item: (-item.score, item.chunk.path, item.chunk.start_line))[:limit]

    def _weighted_vector(self, counts: Counter[str], *, include_unknown: bool = False) -> dict[str, float]:
        vector: dict[str, float] = {}
        total_documents = len(self.chunks)
        for term, count in counts.items():
            idf = self.inverse_document_frequency.get(term)
            if idf is None and include_unknown:
                idf = math.log(total_documents + 1) + 1
            if idf is not None:
                vector[term] = (1 + math.log(count)) * idf
        return vector


class SearchIndex(Protocol):
    """Common search contract for comparable, traceable retrieval indexes."""

    chunks: list[CodeChunk]

    def search(self, query: str, *, limit: int = 8) -> list[Evidence]: ...


class BM25Index:
    """Dependency-free Okapi BM25 over the same traceable chunks as TF-IDF."""

    def __init__(self, chunks: list[CodeChunk], *, k1: float = 1.5, b: float = 0.75):
        if k1 <= 0:
            raise ValueError("BM25 k1 must be positive.")
        if not 0 <= b <= 1:
            raise ValueError("BM25 b must be between 0 and 1.")
        self.chunks = list(chunks)
        self.k1 = float(k1)
        self.b = float(b)
        self.document_terms = [
            _add_singular_variants(Counter(_tokens(f"{chunk.name} {chunk.path} {chunk.content}")))
            for chunk in self.chunks
        ]
        self.document_lengths = [sum(terms.values()) for terms in self.document_terms]
        self.average_document_length = (
            sum(self.document_lengths) / len(self.document_lengths) if self.document_lengths else 0.0
        )
        document_frequency: Counter[str] = Counter()
        for terms in self.document_terms:
            document_frequency.update(terms.keys())
        total_documents = len(self.chunks)
        self.inverse_document_frequency = {
            term: math.log1p((total_documents - frequency + 0.5) / (frequency + 0.5))
            for term, frequency in document_frequency.items()
        }

    def search(self, query: str, *, limit: int = 8) -> list[Evidence]:
        """Rank chunks with Okapi BM25 and stable path/line tie breaks."""
        if limit < 1:
            raise ValueError("limit must be positive.")
        query_terms = set(_add_singular_variants(Counter(_tokens(query))))
        if not query_terms or not self.chunks:
            return []
        ranked: list[Evidence] = []
        average_length = self.average_document_length or 1.0
        for index, terms in enumerate(self.document_terms):
            document_length = self.document_lengths[index]
            score = 0.0
            for term in query_terms:
                term_frequency = terms.get(term, 0)
                if not term_frequency:
                    continue
                denominator = term_frequency + self.k1 * (
                    1 - self.b + self.b * document_length / average_length
                )
                score += self.inverse_document_frequency[term] * (
                    term_frequency * (self.k1 + 1) / denominator
                )
            if score > 0:
                ranked.append(Evidence(self.chunks[index], round(score, 6)))
        return sorted(ranked, key=lambda item: (-item.score, item.chunk.path, item.chunk.start_line))[:limit]


class ReciprocalRankFusion:
    """Fuse equally weighted, same-corpus rankings with reciprocal rank fusion."""

    def __init__(self, indexes: Mapping[str, SearchIndex], *, rank_constant: int = 60):
        if len(indexes) < 2:
            raise ValueError("Reciprocal rank fusion needs at least two retrieval methods.")
        if rank_constant < 1:
            raise ValueError("rank_constant must be positive.")
        self.indexes = dict(indexes)
        if any(not name.strip() for name in self.indexes):
            raise ValueError("Retrieval method names must be non-empty.")
        self.rank_constant = rank_constant
        first_chunks = next(iter(self.indexes.values())).chunks
        signature = [_chunk_signature(chunk) for chunk in first_chunks]
        for index in self.indexes.values():
            if [_chunk_signature(chunk) for chunk in index.chunks] != signature:
                raise ValueError("All fused indexes must contain the same ordered chunks.")
        self.chunks = list(first_chunks)

    def search(self, query: str, *, limit: int = 8) -> list[Evidence]:
        """Fuse complete per-method rankings; scores are RRF scores, not similarities."""
        if limit < 1:
            raise ValueError("limit must be positive.")
        fused: dict[tuple[str, str, int, int], tuple[CodeChunk, float]] = {}
        full_limit = max(len(self.chunks), 1)
        for index in self.indexes.values():
            for rank, evidence in enumerate(index.search(query, limit=full_limit), start=1):
                key = _chunk_signature(evidence.chunk)
                chunk, score = fused.get(key, (evidence.chunk, 0.0))
                fused[key] = (chunk, score + 1.0 / (self.rank_constant + rank))
        ranked = [Evidence(chunk, round(score, 6)) for chunk, score in fused.values()]
        return sorted(ranked, key=lambda item: (-item.score, item.chunk.path, item.chunk.start_line))[:limit]


def _chunk_signature(chunk: CodeChunk) -> tuple[str, str, int, int, str]:
    return chunk.path, chunk.name, chunk.start_line, chunk.end_line, chunk.content


def retrieve(query: str, chunks: list[CodeChunk], *, limit: int = 8) -> list[Evidence]:
    """Convenience wrapper that builds a local TF-IDF index for one query."""
    return TfidfIndex(chunks).search(query, limit=limit)


def _tokens(text: str) -> list[str]:
    """Tokenize identifiers and retain both underscore names and their parts."""
    result: list[str] = []
    for raw in re.findall(r"[a-z][a-z0-9_]*", text.lower()):
        if len(raw) > 1:
            result.append(raw)
            result.extend(part for part in raw.split("_") if len(part) > 1)
    return result


def _singular_form(term: str) -> str | None:
    """Return a conservative singular query variant to improve lexical recall."""
    if len(term) > 4 and term.endswith("ies"):
        return term[:-3] + "y"
    if len(term) > 5 and term.endswith(("sses", "shes", "ches", "xes", "zes")):
        return term[:-2]
    if len(term) > 3 and term.endswith("s") and not term.endswith(("ss", "us", "is")):
        return term[:-1]
    return None


def _add_singular_variants(terms: Counter[str]) -> Counter[str]:
    """Add conservative singular token forms without discarding original terms."""
    expanded = terms.copy()
    for term, count in terms.items():
        singular = _singular_form(term)
        if singular and singular != term:
            expanded[singular] += count
    return expanded


def _norm(vector: dict[str, float]) -> float:
    """Calculate Euclidean vector length."""
    return math.sqrt(sum(weight * weight for weight in vector.values()))

