import pytest

from devmind.models import CodeChunk
from devmind.retrieval import BM25Index, ReciprocalRankFusion, TfidfIndex
from devmind.retrieval_experiment import build_retrievers, evaluate_retrieval_methods
from devmind.vector_index import VectorIndex


def _chunks():
    return [
        CodeChunk("src/cart.py", "restore_cart", "function", 1, 5, "restore cart storage after refresh"),
        CodeChunk("src/storage.py", "read_storage", "function", 1, 4, "read cart from browser storage"),
        CodeChunk("src/checkout.py", "checkout", "function", 1, 3, "submit checkout payment"),
        CodeChunk("tests/test_cart.py", "test_cart", "test", 1, 4, "cart refresh should restore saved items"),
        CodeChunk("README.md", "overview", "file", 1, 2, "project installation"),
    ]


def test_bm25_ranks_relevant_cart_chunk_and_is_deterministic():
    index = BM25Index(_chunks())

    first = index.search("restore cart storage after refresh", limit=5)
    second = index.search("restore cart storage after refresh", limit=5)

    assert first == second
    assert first[0].chunk.path == "src/cart.py"
    assert first[0].score > 0


def test_reciprocal_rank_fusion_is_traceable_and_requires_same_corpus():
    chunks = _chunks()
    fused = ReciprocalRankFusion({"tfidf": TfidfIndex(chunks), "bm25": BM25Index(chunks)})
    ranking = fused.search("cart restore storage refresh", limit=5)

    assert ranking[0].chunk.path in {"src/cart.py", "tests/test_cart.py"}
    assert ranking[0].score > ranking[-1].score

    with pytest.raises(ValueError, match="same ordered chunks"):
        ReciprocalRankFusion({"left": TfidfIndex(chunks), "right": BM25Index(chunks[:-1])})


def test_retriever_builder_and_paired_methods_use_same_chunks():
    chunks = _chunks()
    indexes, build_seconds, model_load_seconds = build_retrievers(chunks)
    records = evaluate_retrieval_methods(
        "issue-1",
        "Cart does not restore saved items after refresh",
        indexes,
        {"src/cart.py"},
        top_k=5,
    )

    assert set(indexes) == {"tfidf_cosine", "bm25_okapi", "hybrid_lexical_rrf"}
    assert set(build_seconds) == {"tfidf_cosine", "bm25_okapi"}
    assert model_load_seconds is None
    assert all(index.chunks == chunks for index in indexes.values())
    assert len(records) == 12
    assert {record["retriever"] for record in records} == set(indexes)
    assert all("retrieved_context_whitespace_token_estimate" in record for record in records)
    assert all(record["metrics"]["precision_at_5"] >= 0 for record in records)


def test_rrf_can_combine_a_traceable_dense_index_with_lexical_search():
    import numpy as np

    class StubSemanticEmbedder:
        dimension = 3
        model_id = "controlled-semantic-ranking-test"

        def embed(self, texts):
            vectors = []
            for text in texts:
                if "src/storage.py" in text or text == "cart state after refresh":
                    vectors.append([1, 0, 0])
                else:
                    vectors.append([0, 1, 0])
            return np.asarray(vectors, dtype=np.float32)

    chunks = _chunks()
    dense = VectorIndex(chunks, StubSemanticEmbedder())
    hybrid = ReciprocalRankFusion({"lexical": BM25Index(chunks), "dense": dense})
    results = hybrid.search("cart state after refresh", limit=5)

    assert results
    assert results[0].chunk in chunks

