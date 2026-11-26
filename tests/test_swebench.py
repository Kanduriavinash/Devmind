import json
import hashlib

import pytest

from devmind import swebench
from devmind.github_repo import DownloadedRepository
from devmind.models import RunReport
from devmind.providers import DeterministicFakeProvider


def _instance(instance_id="django__django-1"):
    return {
        "instance_id": instance_id,
        "repo": "django/django",
        "base_commit": "a" * 40,
        "problem_statement": "A Django issue with a reproducible failure.",
    }


def test_load_jsonl_and_selects_only_requested_instances(tmp_path):
    path = tmp_path / "instances.jsonl"
    path.write_text(json.dumps(_instance()) + "\n", encoding="utf-8")
    rows = swebench.load_instances(path)
    assert swebench.select_instances(rows, ["django__django-1"]) == rows


def test_load_jsonl_rejects_duplicate_task_ids(tmp_path):
    path = tmp_path / "instances.jsonl"
    row = json.dumps(_instance())
    path.write_text(row + "\n" + row + "\n", encoding="utf-8")
    with pytest.raises(swebench.SWEbenchInputError, match="Duplicate"):
        swebench.load_instances(path)


def test_load_jsonl_accepts_utf8_bom_from_windows_exports(tmp_path):
    path = tmp_path / "instances.jsonl"
    path.write_text(json.dumps(_instance()) + "\n", encoding="utf-8-sig")
    assert swebench.load_instances(path)[0]["instance_id"] == "django__django-1"


@pytest.mark.parametrize(
    ("field", "value"),
    [("repo", "https://github.com/django/django"), ("base_commit", "../main"), ("problem_statement", "")],
)
def test_rejects_invalid_instance_fields(field, value):
    row = _instance()
    row[field] = value
    with pytest.raises(swebench.SWEbenchInputError):
        swebench.validate_instance(row)


def test_selection_requires_explicit_unique_known_ids():
    rows = [_instance()]
    with pytest.raises(swebench.SWEbenchInputError, match="unique"):
        swebench.select_instances(rows, [])
    with pytest.raises(swebench.SWEbenchInputError, match="unique"):
        swebench.select_instances(rows, ["django__django-1", "django__django-1"])
    with pytest.raises(swebench.SWEbenchInputError, match="Unknown"):
        swebench.select_instances(rows, ["missing"])


def test_generate_predictions_uses_pinned_repo_and_marks_patch_untested(tmp_path, monkeypatch):
    instance = _instance()
    downloaded_path = tmp_path / "cache" / "devmind-repo-test"
    downloaded_path.mkdir(parents=True)
    calls = []

    def fake_download(url, cache, *, ref, max_files, skip_symlinks):
        calls.append((url, ref, max_files, skip_symlinks))
        return DownloadedRepository(downloaded_path, "django/django", "main", url, None, skipped_symlinks=2)

    diff = "diff --git a/django/sample.py b/django/sample.py\n--- a/django/sample.py\n+++ b/django/sample.py\n@@ -1 +1 @@\n-old\n+new\n"
    report = RunReport("patch_proposed_unverified", "issue", {}, [], [{"path": "django/sample.py"}], {}, candidate_patch=diff)
    monkeypatch.setattr(swebench, "download_public_repository", fake_download)
    monkeypatch.setattr(swebench, "run_analysis", lambda *args, **kwargs: report)

    predictions, notes = swebench.generate_predictions(
        [instance], instance_ids=[instance["instance_id"]], repository_cache=tmp_path / "cache",
        provider=DeterministicFakeProvider("unused"),
    )

    assert calls == [("https://github.com/django/django", "a" * 40, 20_000, True)]
    assert predictions[0]["instance_id"] == instance["instance_id"]
    assert predictions[0]["model_patch"] == diff
    assert notes[0]["patch_proposed"] is True
    assert notes[0]["patch_tested"] is False
    assert notes[0]["base_commit"] == "a" * 40
    assert notes[0]["skipped_symlinks"] == 2
    pointers = list((tmp_path / "cache").glob("*.json"))
    assert len(pointers) == 1
    assert json.loads(pointers[0].read_text(encoding="utf-8"))["directory"] == "devmind-repo-test"


def test_generate_predictions_passes_bounded_top_k(tmp_path, monkeypatch):
    instance = _instance()
    path = tmp_path / "cache" / "devmind-repo-test"
    path.mkdir(parents=True)
    monkeypatch.setattr(swebench, "download_public_repository", lambda *args, **kwargs: DownloadedRepository(path, "django/django", "main", "url", None))
    received = {}

    def fake_analysis(*args, **kwargs):
        received.update(kwargs)
        return RunReport("patch_blocked_insufficient_evidence", "issue", {}, [], [], {})

    monkeypatch.setattr(swebench, "run_analysis", fake_analysis)
    swebench.generate_predictions([instance], instance_ids=[instance["instance_id"]], repository_cache=tmp_path / "cache", top_k=2)
    assert received["limit"] == 2
    assert received["patch_context_chars"] == 1500
    with pytest.raises(ValueError, match="top_k"):
        swebench.generate_predictions([instance], instance_ids=[instance["instance_id"]], repository_cache=tmp_path / "cache", top_k=9)
    with pytest.raises(ValueError, match="context_chars"):
        swebench.generate_predictions([instance], instance_ids=[instance["instance_id"]], repository_cache=tmp_path / "cache", context_chars=250)


def test_predictions_writer_emits_jsonl(tmp_path):
    target = tmp_path / "out" / "predictions.jsonl"
    swebench.write_jsonl(target, [{"instance_id": "one", "model_patch": ""}])
    assert json.loads(target.read_text(encoding="utf-8")) == {"instance_id": "one", "model_patch": ""}


def test_generate_predictions_reuses_validated_cache_pointer(tmp_path, monkeypatch):
    instance = _instance()
    cache = tmp_path / "cache"
    repository = cache / "devmind-repo-cached"
    repository.mkdir(parents=True)
    cache_key = hashlib.sha256(f"{instance['repo']}@{instance['base_commit']}".encode()).hexdigest()
    (cache / f"{cache_key}.json").write_text(
        json.dumps({"directory": repository.name, "skipped_symlinks": 3}), encoding="utf-8",
    )
    monkeypatch.setattr(
        swebench, "download_public_repository",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("A valid cached snapshot should be reused.")),
    )
    monkeypatch.setattr(
        swebench, "run_analysis",
        lambda *args, **kwargs: RunReport("patch_blocked_insufficient_evidence", "issue", {}, [], [], {}),
    )

    _, notes = swebench.generate_predictions(
        [instance], instance_ids=[instance["instance_id"]], repository_cache=cache,
        provider=DeterministicFakeProvider("unused"),
    )

    assert notes[0]["skipped_symlinks"] == 3
