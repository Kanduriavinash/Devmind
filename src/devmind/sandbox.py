"""Docker-only isolated test execution; never falls back to running repository code on host."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from threading import Thread
from pathlib import Path
from typing import TextIO

from devmind.code_agent import validate_unified_diff

class SandboxUnavailable(RuntimeError):
    """Raised when Docker or a configured container image is unavailable."""

_TEST_STARTED = "__DEVMIND_TEST_COMMAND_STARTED__"
_PATCH_APPLIED = "__DEVMIND_PATCH_APPLIED__"

def run_tests(repository: str | Path, *, candidate_patch: str | None = None, image: str | None = None, timeout: int | None = None, test_runner: str | None = None) -> dict[str, object]:
    """Copy a repo into a temp directory and run pytest or Node tests in Docker.

    When a patch is supplied it is mounted separately and applied inside the container,
    so an unapplied patch can never be described as tested.
    """
    patch_paths = validate_unified_diff(candidate_patch) if candidate_patch is not None else []
    docker = shutil.which("docker")
    if not docker:
        raise SandboxUnavailable("Docker is not installed or not on PATH; tests were not run.")
    root = Path(repository).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Repository path must be a directory.")
    for relative_path in patch_paths:
        target = root.joinpath(*relative_path.split("/"))
        for parent in (target, *target.parents):
            if parent == root.parent:
                break
            if parent.is_symlink():
                raise ValueError("Candidate patches cannot target symlinks or files inside symlink directories.")
        try:
            target.resolve(strict=False).relative_to(root)
        except ValueError as exc:
            raise ValueError("Candidate patch path resolves outside the selected repository.") from exc
    runner = (test_runner or os.getenv("DEVMIND_TEST_RUNNER", "pytest")).strip().lower()
    _RUNNER_COMMANDS = {
        "pytest": ("pytest", "pytest -q"),
        "node": ("node", "node --test"),
        "go": ("go", "go test ./..."),
        "cargo": ("cargo", "cargo test"),
        "dotnet": ("dotnet", "dotnet test --no-build"),
        "mvn": ("mvn", "mvn test -B"),
        "gradle": ("gradle", "gradle test"),
        "phpunit": ("phpunit", "phpunit"),
        "ruby": ("ruby", "ruby -Itest -e 'Dir.glob(\"test/**/*_test.rb\").each{|f| require \"./#{f}\"}'"),
        "rspec": ("rspec", "rspec"),
        "swift": ("swift", "swift test"),
    }
    if runner not in _RUNNER_COMMANDS:
        supported = ", ".join(sorted(_RUNNER_COMMANDS))
        raise ValueError(f"test_runner must be one of: {supported}.")
    runner_executable, runner_command = _RUNNER_COMMANDS[runner]
    default_image_variable = {
        "node": "DEVMIND_NODE_DOCKER_IMAGE",
        "go": "DEVMIND_GO_DOCKER_IMAGE",
        "cargo": "DEVMIND_RUST_DOCKER_IMAGE",
        "dotnet": "DEVMIND_DOTNET_DOCKER_IMAGE",
        "mvn": "DEVMIND_JAVA_DOCKER_IMAGE",
        "gradle": "DEVMIND_JAVA_DOCKER_IMAGE",
        "phpunit": "DEVMIND_PHP_DOCKER_IMAGE",
        "ruby": "DEVMIND_RUBY_DOCKER_IMAGE",
        "rspec": "DEVMIND_RUBY_DOCKER_IMAGE",
        "swift": "DEVMIND_SWIFT_DOCKER_IMAGE",
    }.get(runner, "DEVMIND_DOCKER_IMAGE")
    container_image = image or os.getenv(default_image_variable, "")
    if not container_image:
        default_sandbox_images = {
            "node": "devmind-sandbox:node22",
            "pytest": "devmind-sandbox:py312",
        }
        container_image = default_sandbox_images.get(runner, "")
    if not container_image:
        raise SandboxUnavailable(f"Set {default_image_variable} to an approved image with {runner} installed.")
    limit = timeout if timeout is not None else int(os.getenv("DEVMIND_SANDBOX_TIMEOUT_SECONDS", "120"))
    if limit < 1:
        raise ValueError("timeout must be positive.")
    with tempfile.TemporaryDirectory(prefix="devmind-run-") as temporary:
        workspace = Path(temporary) / "repo"
        shutil.copytree(root, workspace, symlinks=True, ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".env", ".env.*", ".aws", ".ssh", ".codex", ".npmrc", ".pypirc", ".netrc", "id_rsa", "id_ed25519"))
        command = [
            docker,
            "run",
            "--rm",
            "--user=10001:10001",
            "--env",
            "HOME=/tmp",
            "--network=none",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges:true",
            "--memory=1g",
            "--cpus=1",
            "--pids-limit=128",
            "--read-only",
            "--tmpfs",
            "/tmp:rw,noexec,nosuid,size=256m",
            "--mount",
            f"type=bind,src={workspace},dst=/workspace",
            "--workdir",
            "/workspace",
        ]

        if candidate_patch is not None:
            patch_path = Path(temporary) / "candidate.patch"
            # Keep patch-file newlines stable across Windows hosts and Linux containers.
            patch_path.write_text(candidate_patch.rstrip("\r\n") + "\n", encoding="utf-8", newline="\n")
            shell_command = f"git apply --ignore-whitespace --unidiff-zero /candidate.patch && printf '{_PATCH_APPLIED}\\n' && test \"$(id -u)\" -ne 0 && command -v {runner_executable} >/dev/null && printf '{_TEST_STARTED}\\n' && exec {runner_command}"
            command.extend(["--mount", f"type=bind,src={patch_path},dst=/candidate.patch,readonly"])
        else:
            shell_command = f"test \"$(id -u)\" -ne 0 && command -v {runner_executable} >/dev/null && printf '{_TEST_STARTED}\\n' && exec {runner_command}"
        command.extend(["--entrypoint", "/bin/sh", container_image, "-c", shell_command])
        returncode, stdout, stderr, timed_out, stdout_truncated, stderr_truncated, markers_found = (
            _run_bounded_process(command, limit)
        )
        started = _TEST_STARTED in markers_found
        return {
            "executed": started,
            "passed": started and not timed_out and returncode == 0,
            "timed_out": timed_out,
            "exit_code": None if timed_out else returncode,
            "mode": "candidate_patch" if candidate_patch is not None else "baseline_repository",
            "patch_applied": _PATCH_APPLIED in markers_found if candidate_patch is not None else None,
            "runner": runner,
            "test_command": runner_command,
            "container_command": shell_command,
            "container_user": "10001:10001",
            "timeout_seconds": limit,
            "stdout": _clean_output(stdout),
            "stderr": stderr,
            "stdout_truncated": stdout_truncated,
            "stderr_truncated": stderr_truncated,
        }

def _run_bounded_process(
    command: list[str], timeout: int
) -> tuple[int, str, str, bool, bool, bool, set[str]]:
    """Drain both pipes continuously while retaining only their final 4,000 chars."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if process.stdout is None or process.stderr is None:
        process.kill()
        process.wait()
        raise RuntimeError("Sandbox process output pipes could not be opened.")

    output: dict[str, tuple[str, bool, set[str]]] = {}

    markers = (_TEST_STARTED, _PATCH_APPLIED)

    def drain(name: str, stream: TextIO) -> None:
        output[name] = _read_bounded_stream(stream, markers=markers)

    readers = [
        Thread(target=drain, args=("stdout", process.stdout), daemon=True),
        Thread(target=drain, args=("stderr", process.stderr), daemon=True),
    ]
    for reader in readers:
        reader.start()

    timed_out = False
    try:
        returncode = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        timed_out = True
        process.kill()
        returncode = process.wait()
    except BaseException:
        if process.poll() is None:
            process.kill()
            process.wait()
        raise
    finally:
        for reader in readers:
            reader.join()

    stdout, stdout_truncated, markers_found = output["stdout"]
    stderr, stderr_truncated, _ = output["stderr"]
    return returncode, stdout, stderr, timed_out, stdout_truncated, stderr_truncated, markers_found


def _read_bounded_stream(
    stream: TextIO, *, marker: str | None = None, markers: tuple[str, ...] = (), limit: int = 4000
) -> tuple[str, bool, set[str]]:
    """Read a pipe without accumulating the complete output in memory."""
    tail = ""
    total_chars = 0
    watched_markers = tuple(dict.fromkeys((*markers, *((marker,) if marker else ()))))
    markers_found: set[str] = set()
    marker_overlap = ""
    while True:
        chunk = stream.read(1024)
        if not chunk:
            break
        total_chars += len(chunk)
        tail = (tail + chunk)[-limit:]
        if watched_markers:
            marker_window = marker_overlap + chunk
            markers_found.update(value for value in watched_markers if value in marker_window)
            overlap = max(len(value) for value in watched_markers) - 1
            marker_overlap = marker_window[-overlap:] if overlap else ""
    return tail, total_chars > limit, markers_found

def _clean_output(value: str) -> str:
    """Remove the internal execution marker from user-facing test output."""
    return "\n".join(line for line in value.splitlines() if line not in {_TEST_STARTED, _PATCH_APPLIED})

