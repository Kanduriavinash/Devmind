"""Run a paired query-variant ablation over one prebuilt TF-IDF index."""

from __future__ import annotations

import time
from pathlib import Path
from collections.abc import Mapping
from typing import Any

from devmind.embeddings import EmbeddingProvider, SentenceTransformerProvider
from devmind.models import CodeChunk, Evidence
from devmind.query_variants import build_query_variants
from devmind.retrieval import BM25Index, ReciprocalRankFusion, SearchIndex, TfidfIndex
from devmind.retrieval_metrics import score_file_ranking
from devmind.vector_index import VectorIndex


def build_retrievers(
    chunks: list[CodeChunk],
    *,
    embedding_model_path: str | Path | None = None,
    embedding_provider: EmbeddingProvider | None = None,
) -> tuple[dict[str, SearchIndex], dict[str, float], float | None]:
    """Build comparable lexical indexes and optional local semantic retrieval.

    The semantic model is loaded only when its local path is explicitly supplied.
    Index-build timings are separated by method; RRF construction is negligible
    metadata wiring and is not treated as a learned/indexed corpus method.
    """
    build_seconds: dict[str, float] = {}
    embedding_model_load_seconds: float | None = None

    started = time.perf_counter()
    tfidf = TfidfIndex(chunks)
    build_seconds["tfidf_cosine"] = time.perf_counter() - started

    started = time.perf_counter()
    bm25 = BM25Index(chunks)
    build_seconds["bm25_okapi"] = time.perf_counter() - started

    lexical_hybrid = ReciprocalRankFusion(
        {"tfidf_cosine": tfidf, "bm25_okapi": bm25}
    )
    indexes: dict[str, SearchIndex] = {
        "tfidf_cosine": tfidf,
        "bm25_okapi": bm25,
        "hybrid_lexical_rrf": lexical_hybrid,
    }
    if embedding_model_path is not None or embedding_provider is not None:
        if embedding_provider is None:
            model_load_started = time.perf_counter()
            embedder = SentenceTransformerProvider(str(embedding_model_path))
            embedding_model_load_seconds = time.perf_counter() - model_load_started
        else:
            embedder = embedding_provider
        started = time.perf_counter()
        semantic = VectorIndex(chunks, embedder)
        build_seconds["sentence_transformer_cosine"] = time.perf_counter() - started
        indexes["sentence_transformer_cosine"] = semantic
        indexes["hybrid_lexical_semantic_rrf"] = ReciprocalRankFusion(
            {"lexical": lexical_hybrid, "sentence_transformer": semantic}
        )
    return indexes, build_seconds, embedding_model_load_seconds


def evaluate_query_variants(
    issue_id: str,
    issue_text: str,
    index: TfidfIndex,
    relevant_files: set[str],
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Evaluate the four queries against one index and the same file labels.

    Labels are read only after each ranking is produced. The retrieval call
    receives only the generated query and the prebuilt index.
    """
    if not isinstance(issue_id, str) or not issue_id.strip():
        raise ValueError("issue_id must be a non-empty string.")
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 5:
        raise ValueError("top_k must be at least 5 so all configured metrics are observable.")
    if not relevant_files:
        raise ValueError("At least one labeled relevant file is required.")

    return evaluate_retrieval_methods(
        issue_id,
        issue_text,
        {"tfidf_cosine": index},
        relevant_files,
        top_k=top_k,
    )


def evaluate_retrieval_methods(
    issue_id: str,
    issue_text: str,
    indexes: Mapping[str, SearchIndex],
    relevant_files: set[str],
    *,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Evaluate every query variant against each method over an identical corpus."""
    if not isinstance(issue_id, str) or not issue_id.strip():
        raise ValueError("issue_id must be a non-empty string.")
    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k < 5:
        raise ValueError("top_k must be at least 5 so all configured metrics are observable.")
    if not relevant_files:
        raise ValueError("At least one labeled relevant file is required.")
    if not indexes:
        raise ValueError("At least one retrieval method is required.")

    first_index = next(iter(indexes.values()), None)
    if first_index is None:
        raise ValueError("At least one retrieval method is required.")
    first_signature = [_chunk_signature(chunk) for chunk in first_index.chunks]
    for name, index in indexes.items():
        if not name.strip():
            raise ValueError("Retrieval method names must be non-empty.")
        if [_chunk_signature(chunk) for chunk in index.chunks] != first_signature:
            raise ValueError("All compared retrievers must use the same ordered chunks.")

    records: list[dict[str, Any]] = []
    for variant in build_query_variants(issue_text):
        for method, index in indexes.items():
            started = time.perf_counter()
            evidence = index.search(variant.generated_query, limit=max(len(index.chunks), 1))
            latency = time.perf_counter() - started
            selected_evidence = _unique_evidence(evidence, top_k)
            ranking = [item.chunk.path for item in selected_evidence]
            records.append(
                {
                    "issue_id": issue_id,
                    "variant": variant.variant,
                    "query_trace": variant.to_dict(),
                    "ranked_files": ranking,
                    "ranked_evidence": [
                        {
                            "path": item.chunk.path,
                            "symbol": item.chunk.name,
                            "kind": item.chunk.kind,
                            "start_line": item.chunk.start_line,
                            "end_line": item.chunk.end_line,
                            "score": item.score,
                        }
                        for item in selected_evidence
                    ],
                    "metrics": score_file_ranking(ranking, relevant_files),
                    "retrieval_latency_seconds": round(latency, 9),
                    "retrieved_context_chars": sum(len(item.chunk.content) for item in selected_evidence),
                    "retrieved_context_whitespace_token_estimate": sum(
                        len(item.chunk.content.split()) for item in selected_evidence
                    ),
                    "retriever": method,
                    "score_semantics": (
                        "reciprocal_rank_fusion"
                        if isinstance(index, ReciprocalRankFusion)
                        else "cosine_similarity"
                        if method.endswith("cosine")
                        else "bm25_score"
                    ),
                    "top_k": top_k,
                }
            )
    return records


def _chunk_signature(chunk: CodeChunk) -> tuple[str, str, int, int, str]:
    return chunk.path, chunk.name, chunk.start_line, chunk.end_line, chunk.content


def _unique_evidence(evidence: list[Evidence], limit: int) -> list[Evidence]:
    selected: list[Evidence] = []
    seen: set[str] = set()
    for item in evidence:
        path = item.chunk.path
        if path not in seen:
            selected.append(item)
            seen.add(path)
        if len(selected) >= limit:
            break
    return selected
