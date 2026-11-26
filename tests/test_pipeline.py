import json

import numpy as np
import pytest

from devmind.pipeline import run_analysis


class FakeEmbedder:
    dimension = 2
    model_id = "pipeline-fake-v1"

    def embed(self, texts):
        rows = [[1, 0] if "divide" in text.lower() else [0, 1] for text in texts]
        return np.asarray(rows, dtype=np.float32).reshape(len(texts), 2)


def test_pipeline_produces_source_cited_hypotheses(tmp_path):
    (tmp_path / "maths.py").write_text("def divide_values(left, right):\n    return left / right\n", encoding="utf-8")
    report = run_analysis("divide values returns wrong result", tmp_path)
    assert report.status == "analysis_complete"
    assert report.evidence[0]["path"] == "maths.py"
    assert report.investigation["uncertainties"]
    assert "patch" in report.limitations[1]


def test_patch_request_without_provider_is_explicitly_blocked(tmp_path):
    (tmp_path / "module.py").write_text("def run_task():\n    return True\n", encoding="utf-8")
    report = run_analysis("run task returns false", tmp_path, generate_patch=True)
    assert report.status == "patch_blocked_provider_unavailable"
    assert report.candidate_patch is None


def test_pipeline_uses_saved_vector_index_and_refreshes_changed_source(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    source = repository / "maths.py"
    source.write_text("def divide_values(left, right):\n    return left / right\n", encoding="utf-8")
    cache = tmp_path / "saved-index"

    first = run_analysis("divide values by zero", repository, embedding_provider=FakeEmbedder(), vector_index_directory=cache)
    assert first.analysis["retrieval_method"] == "embedding_cosine"
    assert first.analysis["score_metric"] == "cosine_similarity"
    assert first.evidence[0]["path"] == "maths.py"

    source.write_text("def divide_values(left, right):\n    return left * right\n", encoding="utf-8")
    second = run_analysis("divide values by zero", repository, embedding_provider=FakeEmbedder(), vector_index_directory=cache)
    stored = json.loads((cache / "metadata.json").read_text(encoding="utf-8"))
    assert second.evidence[0]["content"].endswith("return left * right")
    assert stored["chunks"][0]["content"].endswith("return left * right")


def test_vector_index_must_be_outside_the_source_repository(tmp_path):
    repository = tmp_path / "repo"
    repository.mkdir()
    (repository / "module.py").write_text("def function():\n    return 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="outside"):
        run_analysis(
            "function returns wrong result",
            repository,
            embedding_provider=FakeEmbedder(),
            vector_index_directory=repository / "index",
        )

