import numpy as np
import pytest

from devmind.embeddings import HashEmbeddingProvider
from devmind.models import CodeChunk
from devmind.vector_index import VectorIndex


def _chunks():
    return [
        CodeChunk("math_ops.py", "divide", "function", 3, 6, "def divide(a, b): return a / b"),
        CodeChunk("text.py", "normalize", "function", 10, 14, "def normalize(value): return value.strip()"),
    ]


class TableEmbedder:
    dimension = 3
    model_id = "table-test-model-v1"

    def embed(self, texts):
        rows = []
        for text in texts:
            if "math_ops.py" in text or "divide by zero" in text:
                rows.append([1, 0, 0])
            else:
                rows.append([0, 1, 0])
        return np.asarray(rows, dtype=np.float32)


def test_vector_index_returns_traceable_cosine_evidence():
    index = VectorIndex(_chunks(), TableEmbedder())
    result = index.search("divide by zero")

    assert result[0].chunk.path == "math_ops.py"
    assert result[0].chunk.start_line == 3
    assert result[0].score == 1.0


def test_vector_index_keeps_negative_cosine_scores_in_rank_order():
    class NegativeQueryEmbedder:
        dimension = 2
        model_id = "negative-query-test-v1"

        def embed(self, texts):
            rows = []
            for text in texts:
                if text == "query":
                    rows.append([-1.0, 0.0])
                elif "math_ops.py" in text:
                    rows.append([1.0, 0.0])
                else:
                    rows.append([0.0, 1.0])
            return np.asarray(rows, dtype=np.float32)

    result = VectorIndex(_chunks(), NegativeQueryEmbedder()).search("query")

    assert [item.chunk.path for item in result] == ["text.py", "math_ops.py"]
    assert result[0].score == 0.0
    assert result[1].score == -1.0


def test_vector_index_save_load_preserves_search_and_metadata(tmp_path):
    embedder = TableEmbedder()
    original = VectorIndex(_chunks(), embedder)
    original.save(tmp_path / "saved")

    loaded = VectorIndex.load(tmp_path / "saved", embedder)

    assert loaded.search("divide by zero") == original.search("divide by zero")
    assert (tmp_path / "saved" / "metadata.json").is_file()
    assert (tmp_path / "saved" / "vectors.npy").is_file()


def test_hash_embedder_is_deterministic_and_validates_dimension():
    embedder = HashEmbeddingProvider(32)
    assert np.array_equal(embedder.embed(["parse empty input"]), embedder.embed(["parse empty input"]))
    with pytest.raises(ValueError, match="positive"):
        HashEmbeddingProvider(0)


def test_empty_inputs_and_incompatible_saved_dimension_are_handled(tmp_path):
    empty = VectorIndex([], HashEmbeddingProvider(4))
    assert empty.search("anything") == []
    empty.save(tmp_path / "empty")
    with pytest.raises(ValueError, match="dimension"):
        VectorIndex.load(tmp_path / "empty", HashEmbeddingProvider(5))


def test_incompatible_model_id_is_rejected(tmp_path):
    index = VectorIndex(_chunks(), TableEmbedder())
    index.save(tmp_path / "saved")

    class DifferentModel(TableEmbedder):
        model_id = "different-model"

    with pytest.raises(ValueError, match="model"):
        VectorIndex.load(tmp_path / "saved", DifferentModel())


def test_bad_embedding_shape_is_rejected():
    class BadEmbedder:
        dimension = 2

        def embed(self, texts):
            return np.zeros((len(texts), 3), dtype=np.float32)

    with pytest.raises(ValueError, match="shape"):
        VectorIndex(_chunks(), BadEmbedder())

