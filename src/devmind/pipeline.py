"""Bounded, evidence-first DevMind analysis workflow."""

from __future__ import annotations

import logging
from pathlib import Path

from devmind.analyzer import analyze_issue
from devmind.code_agent import generate_candidate_patch
from devmind.embeddings import EmbeddingProvider, SentenceTransformerProvider
from devmind.indexer import index_repository
from devmind.investigator import investigate
from devmind.models import RunReport
from devmind.planner import create_plan
from devmind.providers import ChatProvider, OpenAICompatibleProvider, ProviderUnavailable
from devmind.retrieval import retrieve
from devmind.vector_index import VectorIndex

logger = logging.getLogger("devmind")


def run_analysis(
    issue: str,
    repository: str | Path,
    *,
    limit: int = 8,
    provider: ChatProvider | None = None,
    generate_patch: bool = False,
    model_investigation: bool = False,
    embedding_provider: EmbeddingProvider | None = None,
    embedding_model_path: str | Path | None = None,
    vector_index_directory: str | Path | None = None,
    patch_context_chars: int = 5000,
) -> RunReport:
    """Analyze and retrieve evidence; optionally ask a configured provider for a diff."""
    if embedding_provider is not None and embedding_model_path is not None:
        raise ValueError("Pass an embedding provider or a model path, not both.")
    if vector_index_directory is not None and embedding_provider is None and embedding_model_path is None:
        raise ValueError("A vector index directory requires an embedding model.")
    if embedding_model_path is not None:
        embedding_provider = SentenceTransformerProvider(str(embedding_model_path))
    active_provider = provider
    if (generate_patch or model_investigation) and active_provider is None:
        active_provider = OpenAICompatibleProvider()
    analysis = analyze_issue(issue)
    plan = create_plan(analysis)
    logger.info("analysis_started")
    repository_root = Path(repository).expanduser().resolve(strict=True)
    chunks = index_repository(repository_root)
    query = " ".join([issue, *analysis.keywords, *analysis.component_hints])
    retrieval_method = "tfidf_cosine"
    if embedding_provider is None:
        evidence = retrieve(query, chunks, limit=limit)
        retrieval_note = "Retrieval uses lexical overlap; semantic embeddings and reranking are not configured."
    else:
        index_directory = _external_index_directory(vector_index_directory, repository_root) if vector_index_directory is not None else None
        vector_index = None
        if index_directory is not None and index_directory.exists():
            try:
                vector_index = VectorIndex.load(index_directory, embedding_provider)
            except ValueError as exc:
                logger.info("saved_vector_index_unusable", extra={"reason": str(exc)})
            if vector_index is not None and vector_index.chunks != chunks:
                logger.info("saved_vector_index_stale", extra={"chunk_count": len(chunks)})
                vector_index = None
        if vector_index is None:
            vector_index = VectorIndex(chunks, embedding_provider)
            if index_directory is not None:
                vector_index.save(index_directory)
        evidence = vector_index.search(query, limit=limit)
        retrieval_method = "embedding_cosine"
        retrieval_note = "Vector retrieval was used; semantic quality depends on the configured embedding model and has not been benchmarked here."
    investigation_error = None
    if model_investigation:
        try:
            findings = investigate(evidence, issue=issue, provider=active_provider)
        except ProviderUnavailable as exc:
            investigation_error = str(exc)
            findings = investigate(evidence, issue=issue)
    else:
        findings = investigate(evidence, issue=issue)
    patch = None
    status = "analysis_complete"
    limitations = [retrieval_note, "A candidate patch is not evidence that the bug is fixed."]
    if model_investigation:
        if findings.source == "llm":
            limitations.append("Model-assisted investigation contains unverified hypotheses, not a confirmed root cause.")
        else:
            limitations.append("Model-assisted investigation was unavailable; deterministic evidence leads are shown instead.")
        if investigation_error:
            limitations.append(f"Investigation provider error: {investigation_error}")
    if generate_patch:
        evidence_records = [
            {"path": e.chunk.path, "name": e.chunk.name, "kind": e.chunk.kind, "start_line": e.chunk.start_line, "end_line": e.chunk.end_line, "score": e.score, "content": e.chunk.content}
            for e in evidence
        ]
        if not evidence:
            status = "patch_blocked_insufficient_evidence"
            limitations.append("No source evidence was retrieved, so no patch request was made.")
        else:
            try:
                patch = generate_candidate_patch(
                    issue,
                    evidence_records,
                    active_provider,
                    investigation=findings.hypotheses,
                    repository_metadata={"root_name": repository_root.name, "language": "Python, JavaScript, or TypeScript"},
                    max_evidence_chars=patch_context_chars,
                )
                if patch:
                    status = "patch_proposed_unverified"
                else:
                    status = "patch_blocked_insufficient_evidence"
                    limitations.append("The model did not return a unified diff; no patch was accepted.")
            except ProviderUnavailable as exc:
                status = "patch_blocked_provider_unavailable"
                limitations.append(str(exc))
    logger.info("analysis_completed", extra={"status": status, "evidence_count": len(evidence)})
    return RunReport(
        status=status,
        issue=issue,
        analysis={"summary": analysis.summary, "keywords": analysis.keywords, "issue_type": analysis.issue_type, "component_hints": analysis.component_hints, "retrieval_method": retrieval_method, "score_metric": "cosine_similarity"},
        plan=plan,
        evidence=[{"path": e.chunk.path, "name": e.chunk.name, "kind": e.chunk.kind, "start_line": e.chunk.start_line, "end_line": e.chunk.end_line, "score": e.score, "content": e.chunk.content} for e in evidence],
        investigation={"findings": findings.findings, "hypotheses": findings.hypotheses, "uncertainties": findings.uncertainties, "evidence_references": findings.evidence_references, "source": findings.source},
        candidate_patch=patch,
        limitations=limitations,
    )


def _external_index_directory(index_directory: str | Path, repository: Path) -> Path:
    """Resolve a vector cache path and ensure it cannot modify the source tree."""
    target = Path(index_directory).expanduser().resolve()
    try:
        target.relative_to(repository)
    except ValueError:
        return target
    raise ValueError("The saved vector index must be outside the selected source repository.")

