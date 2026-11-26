"""Evidence-constrained investigation with deterministic and optional model paths."""

from __future__ import annotations

import json
from typing import Any

from devmind.models import Evidence, Investigation
from devmind.providers import ChatProvider, ProviderInvalidResponse, complete_json


def investigate(evidence: list[Evidence], *, issue: str = "", provider: ChatProvider | None = None) -> Investigation:
    """Summarize retrieved code and make only evidence-cited, uncertain hypotheses."""
    if not evidence:
        return Investigation([], [], ["No matching source evidence was retrieved; root cause is unknown."], source="heuristic")

    evidence_ids = {f"E{number}": item for number, item in enumerate(evidence[:8], start=1)}
    findings = [
        f"[{evidence_id}] Retrieved {item.chunk.kind} `{item.chunk.name}` at {item.chunk.path}:{item.chunk.start_line}-{item.chunk.end_line} (similarity {item.score:.4f})."
        for evidence_id, item in evidence_ids.items()
    ]
    if provider is None:
        hypotheses = [
            f"[{evidence_id}] `{item.chunk.name}` may be relevant because its name or source overlaps the issue; inspect its behavior and related tests."
            for evidence_id, item in list(evidence_ids.items())[:3]
        ]
        refs = {hypothesis: [evidence_id] for hypothesis, evidence_id in zip(hypotheses, list(evidence_ids)[:3])}
        return Investigation(
            findings,
            hypotheses,
            ["Similarity does not establish causality; verify behavior with targeted tests."],
            evidence_references=refs,
            source="heuristic",
        )

    result = complete_json(provider, _investigation_prompt(issue, evidence_ids))
    hypotheses, refs, uncertainties = _validate_model_result(result, evidence_ids)
    return Investigation(
        findings,
        hypotheses,
        uncertainties or ["The model's hypotheses are unverified and need targeted tests."],
        evidence_references=refs,
        source="llm",
    )


def _investigation_prompt(issue: str, evidence: dict[str, Evidence]) -> str:
    snippets = [
        {
            "evidence_id": evidence_id,
            "path": item.chunk.path,
            "symbol": item.chunk.name,
            "line_start": item.chunk.start_line,
            "line_end": item.chunk.end_line,
            "code": item.chunk.content[:3000],
        }
        for evidence_id, item in evidence.items()
    ]
    return (
        "Inspect these retrieved repository snippets and return exactly one JSON object with keys "
        '"hypotheses" and "open_questions". Each hypothesis must be an object with a concise "claim", '
        'a non-empty "evidence_ids" list containing only supplied IDs, and a non-empty "uncertainty". '
        "Do not invent files, functions, tests, or facts. A similarity match does not prove causality. "
        "Return at most 5 hypotheses and 5 open questions.\nBug report:\n"
        + issue[:4000]
        + "\nEvidence:\n"
        + json.dumps(snippets, ensure_ascii=False)
    )


def _validate_model_result(
    payload: dict[str, Any], evidence: dict[str, Evidence]
) -> tuple[list[str], dict[str, list[str]], list[str]]:
    raw_hypotheses = payload.get("hypotheses")
    raw_questions = payload.get("open_questions", [])
    if not isinstance(raw_hypotheses, list) or len(raw_hypotheses) > 5:
        raise ProviderInvalidResponse("Investigation hypotheses must be a list of at most five items.")
    if not isinstance(raw_questions, list) or len(raw_questions) > 5:
        raise ProviderInvalidResponse("Investigation open_questions must be a list of at most five items.")
    if any(not isinstance(question, str) or not question.strip() or len(question) > 400 for question in raw_questions):
        raise ProviderInvalidResponse("Investigation questions must be non-empty strings up to 400 characters.")

    hypotheses: list[str] = []
    references: dict[str, list[str]] = {}
    uncertainties: list[str] = []
    for item in raw_hypotheses:
        if not isinstance(item, dict):
            raise ProviderInvalidResponse("Each investigation hypothesis must be an object.")
        claim = item.get("claim")
        ids = item.get("evidence_ids")
        uncertainty = item.get("uncertainty")
        if not isinstance(claim, str) or not claim.strip() or len(claim) > 500:
            raise ProviderInvalidResponse("Each investigation claim must be a concise non-empty string.")
        if not isinstance(ids, list) or not ids or any(not isinstance(identifier, str) or identifier not in evidence for identifier in ids):
            raise ProviderInvalidResponse("Each hypothesis must cite only evidence IDs supplied to the investigator.")
        if not isinstance(uncertainty, str) or not uncertainty.strip() or len(uncertainty) > 400:
            raise ProviderInvalidResponse("Each investigation hypothesis must state its uncertainty.")
        normalized_ids = list(dict.fromkeys(ids))
        hypothesis = f"[{', '.join(normalized_ids)}] {claim}"
        hypotheses.append(hypothesis)
        references[hypothesis] = normalized_ids
        uncertainties.append(uncertainty.strip())
    uncertainties.extend(question.strip() for question in raw_questions)
    return hypotheses, references, uncertainties
