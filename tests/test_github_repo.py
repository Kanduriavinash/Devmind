import hashlib
import io
import json
import stat
import zipfile

import pytest

from devmind.github_repo import (
    GitHubRepositoryError,
    _GitHubRedirectHandler,
    _extract_archive,
    download_public_repository,
    parse_public_repository_url,
)


def _archive(entries: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        for name, data in entries.items():
            bundle.writestr(name, data)
    return buffer.getvalue()


def test_parse_public_github_repository_url_accepts_repository_and_issue_links():
    assert parse_public_repository_url("https://github.com/openai/example") == ("openai", "example")
    assert parse_public_repository_url("https://github.com/openai/example.git/issues/3") == ("openai", "example")


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/owner/repo",
        "https://github.com.evil.invalid/owner/repo",
        "https://user:password@github.com/owner/repo",
        "https://github.com/owner/repo?token=secret",
        "https://github.com/owner",
        "https://github.com/../repo",
    ],
)
def test_parse_public_github_repository_url_rejects_unsafe_urls(url):
    with pytest.raises(GitHubRepositoryError):
        parse_public_repository_url(url)


@pytest.mark.parametrize("url", ["http://codeload.github.com/file.zip", "https://attacker.invalid/file.zip"])
def test_github_redirect_handler_rejects_downgrades_and_untrusted_hosts(url):
    with pytest.raises(GitHubRepositoryError, match="unsupported host"):
        _GitHubRedirectHandler().redirect_request(None, None, 302, "Found", {}, url)


def test_extract_archive_strips_archive_root_and_writes_within_destination(tmp_path):
    destination = tmp_path / "repository"
    destination.mkdir()
    archive = _archive({"repo-abc/src/calculator.py": b"def divide(a, b):\n    return a / b\n"})

    _extract_archive(archive, destination, max_files=2, max_extracted_bytes=1000)

    assert (destination / "src/calculator.py").read_text(encoding="utf-8").startswith("def divide")
    assert not (tmp_path / "repo-abc").exists()


def test_extract_archive_rejects_parent_traversal(tmp_path):
    destination = tmp_path / "repository"
    destination.mkdir()
    archive = _archive({"repo-abc/../../escape.txt": b"no"})

    with pytest.raises(GitHubRepositoryError, match="unsafe path"):
        _extract_archive(archive, destination, max_files=2, max_extracted_bytes=1000)
    assert not (tmp_path / "escape.txt").exists()


@pytest.mark.parametrize("member", ["repo-abc/CON", "repo-abc/file.txt:stream", "repo-abc/trailing."])
def test_extract_archive_rejects_windows_unsafe_path_parts(tmp_path, member):
    destination = tmp_path / "repository"
    destination.mkdir()
    archive = _archive({member: b"blocked"})
    with pytest.raises(GitHubRepositoryError, match="unsafe path"):
        _extract_archive(archive, destination, max_files=2, max_extracted_bytes=1000)


def test_extract_archive_rejects_symlink_and_size_limit(tmp_path):
    destination = tmp_path / "repository"
    destination.mkdir()
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        entry = zipfile.ZipInfo("repo-abc/link")
        entry.create_system = 3
        entry.external_attr = (stat.S_IFLNK | 0o777) << 16
        bundle.writestr(entry, "target")
    with pytest.raises(GitHubRepositoryError, match="symbolic links"):
        _extract_archive(buffer.getvalue(), destination, max_files=2, max_extracted_bytes=1000)

    skipped = _extract_archive(
        buffer.getvalue(), destination, max_files=2, max_extracted_bytes=1000, skip_symlinks=True,
    )
    assert skipped == 1
    assert not (destination / "link").exists()

    archive = _archive({"repo-abc/file.txt": b"12345"})
    with pytest.raises(GitHubRepositoryError, match="extracted-size"):
        _extract_archive(archive, destination, max_files=2, max_extracted_bytes=4)


def test_download_public_repository_pins_default_branch_and_hashes_archive(tmp_path, monkeypatch):
    archive = _archive({"example-main/src/app.py": b"def run():\n    return True\n"})
    calls = []
    commit_sha = "a" * 40

    def fake_open(url, *, timeout):
        calls.append((url, timeout))
        if "/commits/" in url:
            return json.dumps({"sha": commit_sha}).encode()
        if "api.github.com" in url:
            return json.dumps({
                "private": False,
                "default_branch": "main",
                "full_name": "owner/example",
                "html_url": "https://github.com/owner/example",
                "pushed_at": "2026-11-16T00:00:00Z",
            }).encode()
        return archive

    monkeypatch.setattr("devmind.github_repo._open_github", fake_open)
    result = download_public_repository("https://github.com/owner/example", tmp_path / "workspace")

    assert result.full_name == "owner/example"
    assert result.path.joinpath("src/app.py").is_file()
    assert result.pushed_at == "2026-11-16T00:00:00Z"
    assert result.commit_sha == commit_sha
    assert result.archive_sha256 == hashlib.sha256(archive).hexdigest()
    assert len(calls) == 3
    assert calls[1][0].endswith("/commits/main")
    assert calls[2][0].endswith("/zip/" + commit_sha)
    assert all(url.startswith(("https://api.github.com/", "https://codeload.github.com/")) for url, _ in calls)


def test_download_public_repository_uses_validated_commit_ref(tmp_path, monkeypatch):
    archive = _archive({"example-abc/src/app.py": b"def run():\n    return True\n"})
    calls = []

    def fake_open(url, *, timeout):
        calls.append(url)
        if "/commits/" in url:
            return json.dumps({"sha": "a" * 40}).encode()
        if "api.github.com" in url:
            return json.dumps({"private": False, "default_branch": "main", "full_name": "owner/example", "html_url": "https://github.com/owner/example"}).encode()
        return archive

    monkeypatch.setattr("devmind.github_repo._open_github", fake_open)
    download_public_repository("https://github.com/owner/example", tmp_path, ref="a" * 40)
    assert calls[-1].endswith("/zip/" + "a" * 40)
    with pytest.raises(GitHubRepositoryError, match="commit ID"):
        download_public_repository("https://github.com/owner/example", tmp_path, ref="../../main")


def test_download_public_repository_rejects_missing_full_commit_sha(tmp_path, monkeypatch):
    calls = []

    def fake_open(url, *, timeout):
        calls.append(url)
        if "/commits/" in url:
            return json.dumps({"sha": "short"}).encode()
        return json.dumps({"private": False, "default_branch": "main", "full_name": "owner/example", "html_url": "https://github.com/owner/example"}).encode()

    monkeypatch.setattr("devmind.github_repo._open_github", fake_open)
    with pytest.raises(GitHubRepositoryError, match="full commit ID"):
        download_public_repository("https://github.com/owner/example", tmp_path)
    assert len(calls) == 2
