import json

import pytest

from devmind.investigator import investigate
from devmind.models import CodeChunk, Evidence
from devmind.pipeline import run_analysis
from devmind.providers import DeterministicFakeProvider, ProviderInvalidResponse


def _evidence():
    return [Evidence(CodeChunk("parser.py", "parse_value", "function", 4, 8, "def parse_value(text): return int(text)"), 0.82)]


def test_model_investigation_keeps_citations_and_uncertainty():
    response = json.dumps({
        "hypotheses": [{"claim": "The conversion can fail for non-numeric input.", "evidence_ids": ["E1"], "uncertainty": "The report's exact input is unknown."}],
        "open_questions": ["What input triggers the failure?"],
    })
    provider = DeterministicFakeProvider(response)

    result = investigate(_evidence(), issue="parse_value crashes", provider=provider)

    assert result.source == "llm"
    assert result.hypotheses[0].startswith("[E1]")
    assert result.evidence_references[result.hypotheses[0]] == ["E1"]
    assert "unknown" in result.uncertainties[0].lower()
    assert "parse_value crashes" in provider.prompts[0]


@pytest.mark.parametrize("payload", [
    {"hypotheses": [{"claim": "May fail", "evidence_ids": ["E9"], "uncertainty": "unknown"}]},
    {"hypotheses": [{"claim": "May fail", "evidence_ids": ["E1"]}]},
    {"hypotheses": "not a list"},
])
def test_model_investigation_rejects_malformed_or_uncited_claims(payload):
    provider = DeterministicFakeProvider(json.dumps(payload))
    with pytest.raises(ProviderInvalidResponse):
        investigate(_evidence(), issue="bug", provider=provider)


def test_investigation_skips_model_when_evidence_is_empty():
    provider = DeterministicFakeProvider("should not be used")
    result = investigate([], issue="bug", provider=provider)

    assert result.source == "heuristic"
    assert result.uncertainties
    assert not provider.prompts


def test_pipeline_falls_back_to_deterministic_investigation_when_provider_missing(tmp_path, monkeypatch):
    monkeypatch.delenv("DEVMIND_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("DEVMIND_LLM_MODEL", raising=False)
    (tmp_path / "parser.py").write_text("def parse_value(text):\n    return int(text)\n", encoding="utf-8")

    report = run_analysis("parse_value crashes for invalid text", tmp_path, model_investigation=True)

    assert report.investigation["source"] == "heuristic"
    assert any("provider error" in item.lower() for item in report.limitations)
