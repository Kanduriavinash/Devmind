import sys
from types import SimpleNamespace

import pytest

from devmind.embeddings import SentenceTransformerProvider


@pytest.mark.parametrize(
    ("dimension_method", "expected"),
    [("get_embedding_dimension", 384), ("get_sentence_embedding_dimension", 128)],
)
def test_sentence_transformer_provider_supports_dimension_api_versions(
    tmp_path, monkeypatch, dimension_method, expected
):
    class FakeModel:
        def __getattr__(self, name):
            if name == dimension_method:
                return lambda: expected
            raise AttributeError(name)

    fake_model = FakeModel()
    monkeypatch.setitem(
        sys.modules,
        "sentence_transformers",
        SimpleNamespace(SentenceTransformer=lambda *args, **kwargs: fake_model),
    )

    provider = SentenceTransformerProvider(str(tmp_path))

    assert provider.dimension == expected
    assert provider.model_id == str(tmp_path.resolve())
