"""Download bounded snapshots of public GitHub repositories without running code."""

from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import stat
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

_ALLOWED_REDIRECT_HOSTS = {"api.github.com", "codeload.github.com"}
_MAX_ARCHIVE_BYTES = 100 * 1024 * 1024
_MAX_EXTRACTED_BYTES = 500 * 1024 * 1024
_MAX_FILES = 5000
_MAX_FILE_BYTES = 50 * 1024 * 1024
_OWNER_REPO = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")
_WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$",
    *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10)),
}


class GitHubRepositoryError(ValueError):
    """A public GitHub repository URL or archive could not be processed safely."""


@dataclass(frozen=True)
class DownloadedRepository:
    """Metadata and local folder for a downloaded public repository snapshot."""

    path: Path
    full_name: str
    default_branch: str
    html_url: str
    pushed_at: str | None
    skipped_symlinks: int = 0
    commit_sha: str | None = None
    archive_sha256: str | None = None


def parse_public_repository_url(value: str) -> tuple[str, str]:
    """Accept a github.com repository URL and return owner/repository names."""
    if not isinstance(value, str) or not value.strip():
        raise GitHubRepositoryError("Enter a GitHub repository URL.")
    try:
        parsed = urllib.parse.urlsplit(value.strip())
        port = parsed.port
    except ValueError as exc:
        raise GitHubRepositoryError("Enter a valid GitHub repository URL.") from exc
    if parsed.scheme != "https" or parsed.hostname != "github.com" or parsed.username or parsed.password or port:
        raise GitHubRepositoryError("Only public HTTPS repositories hosted on github.com are supported.")
    if parsed.query or parsed.fragment:
        raise GitHubRepositoryError("Remove query strings and fragments from the repository URL.")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise GitHubRepositoryError("Use a repository URL such as https://github.com/owner/repository.")
    owner, repository = parts[:2]
    if repository.endswith(".git"):
        repository = repository[:-4]
    if not _OWNER_REPO.fullmatch(owner) or not _OWNER_REPO.fullmatch(repository) or owner in {".", ".."} or repository in {".", ".."}:
        raise GitHubRepositoryError("The repository URL contains an invalid owner or repository name.")
    return owner, repository


class _GitHubRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Permit redirects only to GitHub API/archive hosts."""

    def redirect_request(self, request, file_pointer, code, message, headers, new_url):
        parsed = urllib.parse.urlsplit(new_url)
        if parsed.scheme != "https" or parsed.hostname not in _ALLOWED_REDIRECT_HOSTS:
            raise GitHubRepositoryError("GitHub returned a redirect to an unsupported host.")
        return super().redirect_request(request, file_pointer, code, message, headers, new_url)


def _open_github(url: str, *, timeout: float) -> bytes:
    opener = urllib.request.build_opener(_GitHubRedirectHandler())
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DevMind-Repository-Analyzer", "Accept": "application/vnd.github+json"},
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > _MAX_ARCHIVE_BYTES:
                raise GitHubRepositoryError("The repository archive exceeds the 100 MiB download limit.")
            data = response.read(_MAX_ARCHIVE_BYTES + 1)
    except GitHubRepositoryError:
        raise
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise GitHubRepositoryError("Could not download the public GitHub repository. Check the URL and network, then retry.") from exc
    if len(data) > _MAX_ARCHIVE_BYTES:
        raise GitHubRepositoryError("The repository archive exceeds the 100 MiB download limit.")
    return data


def download_public_repository(
    value: str,
    workspace: str | Path,
    *,
    ref: str | None = None,
    timeout: float = 20.0,
    max_files: int = _MAX_FILES,
    max_extracted_bytes: int = _MAX_EXTRACTED_BYTES,
    skip_symlinks: bool = False,
) -> DownloadedRepository:
    """Download and safely extract a bounded source snapshot for local analysis.

    Only GitHub's public repository metadata and archive hosts are contacted. The
    returned source files are treated as data; this function never executes them.
    """
    if timeout <= 0 or max_files < 1 or max_extracted_bytes < 1:
        raise ValueError("Download timeout and repository limits must be positive.")
    if ref is not None and (not isinstance(ref, str) or not re.fullmatch(r"[0-9a-fA-F]{7,64}", ref)):
        raise GitHubRepositoryError("A pinned repository ref must be a hexadecimal commit ID.")
    owner, repository = parse_public_repository_url(value)
    api_url = f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repository)}"
    try:
        metadata = json.loads(_open_github(api_url, timeout=timeout))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise GitHubRepositoryError("GitHub returned invalid repository metadata.") from exc
    if not isinstance(metadata, dict) or metadata.get("private") is not False:
        raise GitHubRepositoryError("Only public GitHub repositories are supported.")
    branch = metadata.get("default_branch")
    full_name = metadata.get("full_name")
    html_url = metadata.get("html_url")
    if not isinstance(branch, str) or not branch or not isinstance(full_name, str) or not isinstance(html_url, str):
        raise GitHubRepositoryError("GitHub repository metadata is missing its default branch or URL.")
    requested_ref = ref or branch
    commit_url = (
        f"https://api.github.com/repos/{urllib.parse.quote(owner)}/{urllib.parse.quote(repository)}"
        f"/commits/{urllib.parse.quote(requested_ref, safe='')}"
    )
    try:
        commit_metadata = json.loads(_open_github(commit_url, timeout=timeout))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise GitHubRepositoryError("GitHub returned invalid commit metadata.") from exc
    commit_sha = commit_metadata.get("sha") if isinstance(commit_metadata, dict) else None
    if not isinstance(commit_sha, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", commit_sha):
        raise GitHubRepositoryError("GitHub did not return a full commit ID for the selected repository revision.")

    archive_url = (
        f"https://codeload.github.com/{urllib.parse.quote(owner)}/{urllib.parse.quote(repository)}"
        f"/zip/{urllib.parse.quote(commit_sha, safe='')}"
    )
    archive = _open_github(archive_url, timeout=timeout)

    workspace_root = Path(workspace).expanduser().resolve()
    workspace_root.mkdir(parents=True, exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix="devmind-repo-", dir=workspace_root)).resolve()
    try:
        skipped_symlinks = _extract_archive(
            archive,
            destination,
            max_files=max_files,
            max_extracted_bytes=max_extracted_bytes,
            skip_symlinks=skip_symlinks,
        )
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise
    return DownloadedRepository(
        path=destination,
        full_name=full_name,
        default_branch=branch,
        html_url=html_url,
        pushed_at=metadata.get("pushed_at") if isinstance(metadata.get("pushed_at"), str) else None,
        skipped_symlinks=skipped_symlinks,
        commit_sha=commit_sha.lower(),
        archive_sha256=hashlib.sha256(archive).hexdigest(),
    )


def _extract_archive(
    archive: bytes,
    destination: Path,
    *,
    max_files: int,
    max_extracted_bytes: int,
    skip_symlinks: bool = False,
) -> int:
    try:
        bundle = zipfile.ZipFile(io.BytesIO(archive))
    except (zipfile.BadZipFile, OSError) as exc:
        raise GitHubRepositoryError("GitHub returned an invalid ZIP archive.") from exc
    with bundle:
        entries = bundle.infolist()
        files = [entry for entry in entries if not entry.is_dir()]
        if len(files) > max_files:
            raise GitHubRepositoryError(f"The repository contains more than the {max_files} file limit.")
        total_size = 0
        for entry in files:
            mode = entry.external_attr >> 16
            if stat.S_ISLNK(mode) and not skip_symlinks:
                raise GitHubRepositoryError("Repository archives containing symbolic links are not accepted.")
            if entry.file_size > _MAX_FILE_BYTES:
                raise GitHubRepositoryError("A repository file exceeds the 50 MiB extraction limit.")
            total_size += entry.file_size
            if total_size > max_extracted_bytes:
                raise GitHubRepositoryError("The repository exceeds the extracted-size limit.")

        roots = {PurePosixPath(entry.filename).parts[0] for entry in entries if PurePosixPath(entry.filename).parts}
        common_root = next(iter(roots)) if len(roots) == 1 else None
        skipped_symlinks = 0
        for entry in entries:
            raw = entry.filename
            if "\\" in raw or raw.startswith("/"):
                raise GitHubRepositoryError("The repository archive contains an unsafe path.")
            source_path = PurePosixPath(raw)
            if any(not _safe_archive_part(part) for part in source_path.parts):
                raise GitHubRepositoryError("The repository archive contains an unsafe path.")
            parts = source_path.parts[1:] if common_root and source_path.parts[0] == common_root else source_path.parts
            if not parts:
                continue
            if stat.S_ISLNK(entry.external_attr >> 16):
                skipped_symlinks += 1
                continue
            target = destination.joinpath(*parts).resolve()
            try:
                target.relative_to(destination)
            except ValueError as exc:
                raise GitHubRepositoryError("The repository archive contains a path outside its workspace.") from exc
            if entry.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            with bundle.open(entry) as source, target.open("xb") as output:
                shutil.copyfileobj(source, output, length=1024 * 1024)
    return skipped_symlinks


def _safe_archive_part(part: str) -> bool:
    """Reject traversal and Windows device/alternate-stream path hazards."""
    if part in {"", ".", ".."} or part.endswith((" ", ".")) or ":" in part:
        return False
    if any(ord(character) < 32 for character in part):
        return False
    device_name = part.split(".", 1)[0].upper()
    return device_name not in _WINDOWS_RESERVED_NAMES

