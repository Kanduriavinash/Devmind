from io import StringIO
from pathlib import Path
import subprocess

from devmind import sandbox

VALID_PATCH = "diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1 +1 @@\n-a\n+b\n"


def test_missing_docker_is_reported_without_host_execution(tmp_path, monkeypatch):
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: None)
    try:
        sandbox.run_tests(tmp_path)
    except sandbox.SandboxUnavailable as error:
        assert "not run" in str(error)
    else:
        raise AssertionError("Missing Docker must block execution.")


def test_candidate_diff_is_passed_to_docker_not_host_tests(tmp_path, monkeypatch):
    (tmp_path / "test_sample.py").write_text("def test_sample(): assert True\n", encoding="utf-8")
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")
    captured = {}

    class Process:
        returncode = 0

        def __init__(self):
            self.stdout = StringIO(f"{sandbox._TEST_STARTED}\n1 passed")
            self.stderr = StringIO("")

        def wait(self, timeout=None):
            captured["timeout"] = timeout
            return self.returncode

        def poll(self):
            return self.returncode

        def kill(self):
            self.returncode = -9

    def fake_popen(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        mounts = [command[index + 1] for index, value in enumerate(command[:-1]) if value == "--mount"]
        patch_mount = mounts[-1]
        patch_file = Path(patch_mount.split("src=", 1)[1].split(",dst=", 1)[0])
        captured["patch_bytes"] = patch_file.read_bytes()
        process = Process()
        captured["process"] = process
        return process

    monkeypatch.setattr(sandbox.subprocess, "Popen", fake_popen)
    # Provider responses are stripped by the Code Agent, so normalize a missing final newline.
    result = sandbox.run_tests(tmp_path, candidate_patch=VALID_PATCH.rstrip("\n"), image="test-image")
    command = captured["command"]
    assert result["mode"] == "candidate_patch"
    assert result["passed"] is True
    assert result["test_command"] == "pytest -q"
    assert result["timeout_seconds"] == 120
    assert result["stdout_truncated"] is False
    assert result["stderr_truncated"] is False
    assert captured["patch_bytes"] == VALID_PATCH.encode("utf-8")
    assert "--user=10001:10001" in command
    assert "HOME=/tmp" in command
    assert "--network=none" in command
    assert "--cap-drop=ALL" in command
    assert "--security-opt=no-new-privileges:true" in command
    assert "--memory=1g" in command
    assert "--cpus=1" in command
    assert "--pids-limit=128" in command
    assert "--read-only" in command
    assert command[-1] == "git apply --ignore-whitespace --unidiff-zero /candidate.patch && printf '__DEVMIND_PATCH_APPLIED__\\n' && test \"$(id -u)\" -ne 0 && command -v pytest >/dev/null && printf '__DEVMIND_TEST_COMMAND_STARTED__\\n' && exec pytest -q"
    assert "/bin/sh" in command
    assert captured["timeout"] == 120


def test_javascript_patch_uses_node_test_runner_inside_docker(tmp_path, monkeypatch):
    patch = "diff --git a/script.js b/script.js\n--- a/script.js\n+++ b/script.js\n@@ -1 +1 @@\n-old\n+new\n"
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")

    class Result:
        returncode = 0
        stdout = f"{sandbox._TEST_STARTED}\n✔ 1 test passed"
        stderr = ""

    captured = {}
    def fake_popen(command, **kwargs):
        captured["command"] = command
        result = Result()
        process = type("Process", (), {
            "returncode": result.returncode,
            "stdout": StringIO(result.stdout),
            "stderr": StringIO(result.stderr),
            "wait": lambda self, timeout=None: self.returncode,
            "poll": lambda self: self.returncode,
            "kill": lambda self: setattr(self, "returncode", -9),
        })()
        return process

    monkeypatch.setattr(sandbox.subprocess, "Popen", fake_popen)
    result = sandbox.run_tests(tmp_path, candidate_patch=patch, image="node-image", test_runner="node")
    assert result["passed"] is True
    assert result["runner"] == "node"
    assert "--user=10001:10001" in captured["command"]
    command = captured["command"][-1]
    assert "git apply --ignore-whitespace --unidiff-zero /candidate.patch" in command
    assert "command -v node" in command
    assert "test \"$(id -u)\" -ne 0" in command
    assert command.endswith("exec node --test")


def test_sandbox_streams_output_and_retains_only_bounded_tails(tmp_path, monkeypatch):
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")

    class Process:
        returncode = 0

        def __init__(self):
            self.stdout = StringIO(
                f"{sandbox._TEST_STARTED}\n" + "x" * 12_000 + "\n3 passed"
            )
            self.stderr = StringIO("warning " + "y" * 12_000)

        def wait(self, timeout=None):
            return self.returncode

        def poll(self):
            return self.returncode

        def kill(self):
            self.returncode = -9

    monkeypatch.setattr(sandbox.subprocess, "Popen", lambda *args, **kwargs: Process())
    result = sandbox.run_tests(tmp_path, image="test-image")

    assert result["executed"] is True
    assert result["passed"] is True
    assert result["stdout_truncated"] is True
    assert result["stderr_truncated"] is True
    assert len(result["stdout"]) <= 4000
    assert len(result["stderr"]) == 4000
    assert "3 passed" in result["stdout"]


def test_sandbox_timeout_kills_process_and_keeps_bounded_output(tmp_path, monkeypatch):
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")

    class Process:
        def __init__(self):
            self.returncode = None
            self.wait_calls = 0
            self.stdout = StringIO(f"{sandbox._TEST_STARTED}\n" + "x" * 8000)
            self.stderr = StringIO("partial diagnostic")

        def wait(self, timeout=None):
            self.wait_calls += 1
            if self.wait_calls == 1:
                raise subprocess.TimeoutExpired("docker", timeout)
            return self.returncode

        def poll(self):
            return self.returncode

        def kill(self):
            self.returncode = -9

    process = Process()
    monkeypatch.setattr(sandbox.subprocess, "Popen", lambda *args, **kwargs: process)
    result = sandbox.run_tests(tmp_path, image="test-image", timeout=3)

    assert result["executed"] is True
    assert result["passed"] is False
    assert result["timed_out"] is True
    assert result["exit_code"] is None
    assert result["timeout_seconds"] == 3
    assert result["stdout_truncated"] is True
    assert len(result["stdout"]) <= 4000
    assert process.returncode == -9


def test_sandbox_rejects_path_traversal_before_container_execution(tmp_path, monkeypatch):
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")
    traversal_patch = "diff --git a/../outside.py b/../outside.py\n--- a/../outside.py\n+++ b/../outside.py\n@@ -1 +1 @@\n-a\n+b\n"
    try:
        sandbox.run_tests(tmp_path, candidate_patch=traversal_patch, image="test-image")
    except ValueError as error:
        assert "relative" in str(error) or "traversal" in str(error)
    else:
        raise AssertionError("Unsafe paths must be rejected before container execution.")


def test_sandbox_does_not_patch_through_symlinks(tmp_path, monkeypatch):
    import os
    import pytest

    target = tmp_path / "real.py"
    target.write_text("old\n", encoding="utf-8")
    link = tmp_path / "linked.py"
    try:
        os.symlink(target, link)
    except OSError:
        pytest.skip("Windows did not permit creating a file symlink.")
    linked_patch = "diff --git a/linked.py b/linked.py\n--- a/linked.py\n+++ b/linked.py\n@@ -1 +1 @@\n-old\n+new\n"
    monkeypatch.setattr(sandbox.shutil, "which", lambda _: "docker")
    with pytest.raises(ValueError, match="symlink"):
        sandbox.run_tests(tmp_path, candidate_patch=linked_patch, image="test-image")

