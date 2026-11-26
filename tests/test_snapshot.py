import hashlib

import pytest

from devmind.snapshot import snapshot_directory_sha256


def test_snapshot_digest_is_stable_and_covers_relative_paths_and_contents(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "z.py").write_bytes(b"z = 2\n")
    (root / "a.py").write_bytes(b"a = 1\n")

    expected = hashlib.sha256()
    for name, content in [("a.py", b"a = 1\n"), ("z.py", b"z = 2\n")]:
        expected.update(name.encode("utf-8") + b"\0")
        expected.update(len(content).to_bytes(8, "big"))
        expected.update(content)

    first = snapshot_directory_sha256(root)
    second = snapshot_directory_sha256(root)

    assert first == expected.hexdigest()
    assert second == first
    (root / "a.py").write_bytes(b"a = 3\n")
    assert snapshot_directory_sha256(root) != first


def test_snapshot_digest_does_not_read_external_symlink_target(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("def secret():\n    return 'one'\n", encoding="utf-8")
    link = root / "linked.py"
    try:
        link.symlink_to(outside)
    except OSError as exc:
        pytest.skip(f"Windows did not allow symlink creation: {exc}")

    first = snapshot_directory_sha256(root)
    outside.write_text("def secret():\n    return 'two'\n", encoding="utf-8")

    assert snapshot_directory_sha256(root) == first
