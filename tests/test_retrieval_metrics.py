import math

import pytest

from devmind.retrieval_metrics import score_file_ranking


def test_scores_precision_recall_mrr_and_ndcg_for_binary_file_labels():
    result = score_file_ranking(
        ["src/a.py", "src/a.py", "tests/test_a.py", "src/b.py"],
        {"src/a.py", "src/b.py"},
    )
    assert result["retrieved_unique_count"] == 3
    assert result["precision_at_1"] == 1.0
    assert result["precision_at_3"] == pytest.approx(2 / 3)
    assert result["recall_at_5"] == 1.0
    assert result["mrr"] == 1.0
    expected_ndcg = (1 + 1 / math.log2(4)) / (1 + 1 / math.log2(3))
    assert result["ndcg_at_3"] == pytest.approx(expected_ndcg)


def test_missing_ground_truth_is_not_silently_scored_as_zero():
    with pytest.raises(ValueError, match="relevant file"):
        score_file_ranking(["src/a.py"], set())


def test_invalid_or_duplicate_cutoffs_are_rejected():
    with pytest.raises(ValueError, match="positive integers"):
        score_file_ranking(["a.py"], {"a.py"}, cutoffs=(1, 0))
    with pytest.raises(ValueError, match="unique"):
        score_file_ranking(["a.py"], {"a.py"}, cutoffs=(1, 1))
