from devmind.models import CodeChunk
from devmind.retrieval import TfidfIndex
from devmind.retrieval_experiment import evaluate_query_variants


def test_experiment_collapses_multiple_chunks_to_distinct_file_ranking():
    chunks = [
        CodeChunk("src/cart.py", "add_to_cart", "function", 1, 4, "cart add item count"),
        CodeChunk("src/cart.py", "save_cart", "function", 6, 9, "cart save local storage"),
        CodeChunk("src/storage.py", "load_cart", "function", 1, 4, "cart load storage on refresh"),
        CodeChunk("README.md", "overview", "file", 1, 2, "project setup"),
    ]
    rows = evaluate_query_variants(
        "issue-1",
        "Cart state is lost on refresh; loadCart from localStorage",
        TfidfIndex(chunks),
        {"src/storage.py"},
        top_k=5,
    )
    assert len(rows) == 4
    assert {row["variant"] for row in rows} == {"raw", "normalized", "keywords_identifiers", "structured"}
    assert all(len(row["ranked_files"]) == len(set(row["ranked_files"])) for row in rows)
    assert all("recall_at_5" in row["metrics"] for row in rows)
    assert all(row["query_trace"]["original_text"].startswith("Cart state") for row in rows)
