import csv
import json

import pytest

from devmind.retrieval_evaluation import run_from_csv
from devmind.snapshot import snapshot_directory_sha256


INPUT_FIELDS = [
    "issue_id", "repository", "base_commit", "issue_url", "issue_title", "issue_body",
    "language", "base_snapshot_path", "base_snapshot_sha256", "split",
]
LABEL_FIELDS = [
    "issue_id", "relevant_path", "label_type", "label_source", "reviewer",
    "confidence", "decision", "inclusion_reason", "annotation_notes",
]


def _write_csv(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_runner_uses_separate_inputs_and_labels_and_writes_paired_method_rows(tmp_path):
    repository = tmp_path / "base"
    (repository / "src").mkdir(parents=True)
    (repository / "src" / "cart.py").write_text(
        "def restore_cart(localStorage):\n    return localStorage.get('cart', [])\n\n"
        "def add_to_cart(cart, item):\n    cart.append(item)\n",
        encoding="utf-8",
    )
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, [{
        "issue_id": "q1", "repository": "owner/repo", "base_commit": "abc1234",
        "issue_url": "https://github.com/owner/repo/issues/1", "issue_title": "Cart is lost after refresh",
        "issue_body": "restore_cart should load localStorage", "language": "python",
        "base_snapshot_path": str(repository), "base_snapshot_sha256": snapshot_directory_sha256(repository), "split": "test",
    }])
    _write_csv(labels, LABEL_FIELDS, [{
        "issue_id": "q1", "relevant_path": "src/cart.py", "label_type": "changed_file_proxy",
        "label_source": "reviewed patch metadata", "reviewer": "reviewer-1", "confidence": "medium",
        "decision": "include", "inclusion_reason": "source fix modifies cart restore", "annotation_notes": "",
    }])

    records = run_from_csv(inputs, labels, output)
    assert len(records) == 12
    assert all(record["status"] == "completed" for record in records)
    assert all(record["snapshot_hash_verified"] is True for record in records)
    assert all(record["snapshot_sha256"] == snapshot_directory_sha256(repository) for record in records)
    assert all(any(path == "src/cart.py" for path in record["ranked_files"]) for record in records)
    assert all(record["query_trace"]["transformation_version"] == "devmind-query-v1" for record in records)
    assert {record["retriever"] for record in records} == {
        "tfidf_cosine", "bm25_okapi", "hybrid_lexical_rrf"
    }
    assert all("index_build_seconds_by_method" in record for record in records)
    assert len(output.read_text(encoding="utf-8").splitlines()) == 12
    assert json.loads(output.read_text(encoding="utf-8").splitlines()[0])["issue_id"] == "q1"


def test_runner_rejects_fix_metadata_in_sanitized_input(tmp_path):
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, [*INPUT_FIELDS, "fix_commit"], [])
    _write_csv(labels, LABEL_FIELDS, [])
    with pytest.raises(ValueError, match="unknown=.*fix_commit"):
        run_from_csv(inputs, labels, output)


def test_runner_blocks_snapshot_when_content_hash_does_not_match(tmp_path):
    repository = tmp_path / "base"
    repository.mkdir()
    (repository / "cart.py").write_text("def restore_cart():\n    return []\n", encoding="utf-8")
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, [{
        "issue_id": "q1", "repository": "owner/repo", "base_commit": "abc1234",
        "issue_url": "", "issue_title": "Cart is lost after refresh", "issue_body": "restore cart",
        "language": "python", "base_snapshot_path": str(repository),
        "base_snapshot_sha256": "0" * 64, "split": "test",
    }])
    _write_csv(labels, LABEL_FIELDS, [{
        "issue_id": "q1", "relevant_path": "cart.py", "label_type": "changed_file_proxy",
        "label_source": "test fixture", "reviewer": "", "confidence": "",
        "decision": "include", "inclusion_reason": "fixture", "annotation_notes": "",
    }])

    records = run_from_csv(inputs, labels, output)

    assert len(records) == 1
    assert records[0]["status"] == "index_blocked_snapshot_hash_mismatch"
    assert records[0]["snapshot_hash_verified"] is False
    assert records[0]["snapshot_sha256_expected"] == "0" * 64
    assert records[0]["snapshot_sha256"] == snapshot_directory_sha256(repository)
    assert records[0]["metrics"] is None
    assert "not indexed" in records[0]["error"]


@pytest.mark.parametrize(
    ("snapshot_hash", "expected_status"),
    [("", "completed"), ("not-a-sha256", "index_blocked_snapshot_hash_invalid")],
)
def test_runner_reports_missing_or_malformed_snapshot_hash(tmp_path, snapshot_hash, expected_status):
    repository = tmp_path / "base"
    repository.mkdir()
    (repository / "cart.py").write_text("def restore_cart():\n    return []\n", encoding="utf-8")
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, [{
        "issue_id": "q1", "repository": "owner/repo", "base_commit": "abc1234",
        "issue_url": "", "issue_title": "Cart is lost after refresh", "issue_body": "restore cart",
        "language": "python", "base_snapshot_path": str(repository),
        "base_snapshot_sha256": snapshot_hash, "split": "test",
    }])
    _write_csv(labels, LABEL_FIELDS, [{
        "issue_id": "q1", "relevant_path": "cart.py", "label_type": "changed_file_proxy",
        "label_source": "test fixture", "reviewer": "", "confidence": "",
        "decision": "include", "inclusion_reason": "fixture", "annotation_notes": "",
    }])

    records = run_from_csv(inputs, labels, output)

    assert records[0]["status"] == expected_status
    if not snapshot_hash:
        assert records[0]["snapshot_hash_verified"] is None
        assert records[0]["snapshot_sha256"] is None
        assert "integrity was not verified" in records[0]["snapshot_hash_note"]
    else:
        assert records[0]["snapshot_hash_verified"] is False
        assert records[0]["metrics"] is None


def test_runner_records_unlabeled_issue_as_excluded_without_scoring(tmp_path):
    repository = tmp_path / "base"
    repository.mkdir()
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, [{
        "issue_id": "q2", "repository": "owner/repo", "base_commit": "abc1234",
        "issue_url": "", "issue_title": "Issue title", "issue_body": "", "language": "python",
        "base_snapshot_path": str(repository), "base_snapshot_sha256": "", "split": "test",
    }])
    _write_csv(labels, LABEL_FIELDS, [])
    records = run_from_csv(inputs, labels, output)
    assert records == [{
        "issue_id": "q2", "variant": None, "status": "excluded_missing_included_labels",
        "metrics": None, "error": "No included file-level ground-truth labels were provided.",
    }]


def test_runner_rejects_path_traversal_in_ground_truth(tmp_path):
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, [])
    _write_csv(labels, LABEL_FIELDS, [{
        "issue_id": "q3", "relevant_path": "../outside.py", "label_type": "changed_file_proxy",
        "label_source": "", "reviewer": "", "confidence": "low", "decision": "include",
        "inclusion_reason": "", "annotation_notes": "",
    }])
    with pytest.raises(ValueError, match="Unsafe relevant_path"):
        run_from_csv(inputs, labels, output)


def test_runner_rejects_cutoffs_that_cannot_cover_all_reported_metrics(tmp_path):
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, [])
    _write_csv(labels, LABEL_FIELDS, [])
    with pytest.raises(ValueError, match="at least 5"):
        run_from_csv(inputs, labels, output, top_k=3)


def test_runner_refuses_to_overwrite_existing_run_records(tmp_path):
    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, [])
    _write_csv(labels, LABEL_FIELDS, [])
    output.write_text("keep this record\n", encoding="utf-8")
    with pytest.raises(ValueError, match="already exists"):
        run_from_csv(inputs, labels, output)
    assert output.read_text(encoding="utf-8") == "keep this record\n"


def test_runner_reuses_one_embedding_model_across_repository_snapshots(
    tmp_path, monkeypatch
):
    np = pytest.importorskip("numpy")
    import devmind.retrieval_evaluation as evaluation_module

    provider_calls = []

    class FakeEmbeddingProvider:
        dimension = 3
        model_id = "test-embedding-provider"

        def embed(self, texts):
            return np.ones((len(texts), self.dimension), dtype=np.float32)

    def make_provider(path):
        provider_calls.append(path)
        return FakeEmbeddingProvider()

    monkeypatch.setattr(evaluation_module, "SentenceTransformerProvider", make_provider)

    input_rows = []
    label_rows = []
    for index in range(2):
        repository = tmp_path / f"repo-{index}"
        repository.mkdir()
        (repository / "cart.py").write_text(
            f"def restore_cart_{index}():\n    return []\n", encoding="utf-8"
        )
        issue_id = f"q{index}"
        input_rows.append({
            "issue_id": issue_id,
            "repository": f"owner/repo-{index}",
            "base_commit": f"abc123{index}",
            "issue_url": "",
            "issue_title": "Cart is lost after refresh",
            "issue_body": "restore the saved cart",
            "language": "python",
            "base_snapshot_path": str(repository),
            "base_snapshot_sha256": snapshot_directory_sha256(repository),
            "split": "test",
        })
        label_rows.append({
            "issue_id": issue_id,
            "relevant_path": "cart.py",
            "label_type": "changed_file_proxy",
            "label_source": "test fixture",
            "reviewer": "",
            "confidence": "",
            "decision": "include",
            "inclusion_reason": "fixture path",
            "annotation_notes": "",
        })

    inputs = tmp_path / "inputs.csv"
    labels = tmp_path / "labels.csv"
    output = tmp_path / "runs.jsonl"
    _write_csv(inputs, INPUT_FIELDS, input_rows)
    _write_csv(labels, LABEL_FIELDS, label_rows)

    records = run_from_csv(
        inputs,
        labels,
        output,
        embedding_model_path=tmp_path / "local-model",
    )

    assert len(provider_calls) == 1
    assert len(records) == 40
    assert all(record["status"] == "completed" for record in records)
    assert all(record["embedding_model_load_seconds"] is not None for record in records)
    assert all(record["embedding_model_path"] == str(tmp_path / "local-model") for record in records)
