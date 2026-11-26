"""Stable content hashing for repository snapshots used in experiments."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Protocol


class _DigestWriter(Protocol):
    def update(self, data: bytes, /) -> None: ...


def snapshot_directory_sha256(directory: str | Path) -> str:
    """Hash relative paths and file bytes without traversing directory symlinks.

    Regular-file records use UTF-8 POSIX relative paths, a NUL separator, an
    unsigned 8-byte big-endian file size, and the file bytes. Internal file
    symlinks hash the resolved in-tree target bytes, matching what the static
    indexer reads. External, broken, and directory symlinks hash their link
    target text only; their targets are never opened. Empty directories are
    omitted because they contain no source content.
    """
    root = Path(directory).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Snapshot path must be a directory.")

    entries: list[Path] = []
    for current, directory_names, file_names in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        traversable: list[str] = []
        for name in sorted(directory_names, key=str.casefold):
            path = current_path / name
            if path.is_symlink():
                entries.append(path)
            else:
                traversable.append(name)
        directory_names[:] = traversable
        entries.extend(current_path / name for name in sorted(file_names, key=str.casefold))

    entries.sort(key=lambda item: item.relative_to(root).as_posix().casefold())
    digest = hashlib.sha256()
    for entry in entries:
        relative = entry.relative_to(root).as_posix().encode("utf-8")
        digest.update(relative + b"\0")
        if entry.is_symlink():
            try:
                target = entry.resolve(strict=True)
                if target.is_file() and target.is_relative_to(root):
                    _hash_file(digest, target)
                    continue
            except (OSError, RuntimeError):
                pass
            link_target = os.readlink(entry).replace("\\", "/").encode("utf-8", errors="surrogatepass")
            digest.update(b"LINK\0" + len(link_target).to_bytes(8, "big") + link_target)
            continue

        resolved = entry.resolve(strict=True)
        if not resolved.is_file() or not resolved.is_relative_to(root):
            # Ignore entries that are not regular in-tree files.
            digest.update(b"SKIP\0")
            continue
        _hash_file(digest, resolved)
    return digest.hexdigest()


def _hash_file(digest: _DigestWriter, path: Path) -> None:
    size = path.stat().st_size
    digest.update(size.to_bytes(8, "big"))
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
