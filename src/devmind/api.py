"""Loopback-only FastAPI backend for local, read-only repository analysis."""

from __future__ import annotations

import ipaddress
import os
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from devmind.pipeline import run_analysis

_HISTORY_LIMIT = 50
_RUN_HISTORY: OrderedDict[str, dict] = OrderedDict()
_HISTORY_LOCK = Lock()


class AnalyzeRequest(BaseModel):
    """Bounded request for offline bug-report analysis."""

    repository: str = Field(min_length=1, max_length=2048)
    bug_report: str = Field(min_length=1, max_length=10_000)
    top_k: int = Field(default=8, ge=1, le=12)

    model_config = ConfigDict(extra="forbid")

    @field_validator("repository", "bug_report", mode="before")
    @classmethod
    def reject_blank_text(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Value must be a non-empty string.")
        return value.strip()


def health() -> dict[str, str]:
    """Return process health without revealing configured filesystem paths."""
    return {"status": "ok", "service": "devmind-local-api"}


def analyze(payload: AnalyzeRequest) -> dict:
    """Analyze a bug report only when its repository is within configured roots."""
    repository = _resolve_allowed_repository(payload.repository)
    try:
        report = run_analysis(payload.bug_report, repository, limit=payload.top_k)
    except (ValueError, OSError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Analysis could not complete in this environment.") from exc
    run_id = uuid4().hex
    record = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "report": report.to_dict(),
    }
    with _HISTORY_LOCK:
        _RUN_HISTORY[run_id] = record
        while len(_RUN_HISTORY) > _HISTORY_LIMIT:
            _RUN_HISTORY.popitem(last=False)
    return record


def list_runs() -> dict[str, list[dict[str, str]]]:
    """List recent in-memory run IDs and timestamps, newest first."""
    with _HISTORY_LOCK:
        items = [{"run_id": item["run_id"], "created_at": item["created_at"]} for item in reversed(_RUN_HISTORY.values())]
    return {"runs": items}


def get_run(run_id: str) -> dict:
    """Return one recent report or a 404 if it is no longer in local history."""
    with _HISTORY_LOCK:
        record = _RUN_HISTORY.get(run_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Run was not found in recent in-memory history.")
    return record


def _resolve_allowed_repository(raw_path: str) -> Path:
    roots_value = os.getenv("DEVMIND_API_REPOSITORY_ROOTS", "")
    roots: list[Path] = []
    for entry in roots_value.split(os.pathsep):
        if not entry.strip():
            continue
        try:
            root = Path(entry).expanduser().resolve(strict=True)
        except OSError:
            continue
        if root.is_dir():
            roots.append(root)
    if not roots:
        raise HTTPException(
            status_code=503,
            detail="Set DEVMIND_API_REPOSITORY_ROOTS to one or more allowed local repository parent folders.",
        )
    try:
        repository = Path(raw_path).expanduser().resolve(strict=True)
    except OSError as exc:
        raise HTTPException(status_code=422, detail="Repository folder does not exist or cannot be read.") from exc
    if not repository.is_dir():
        raise HTTPException(status_code=422, detail="Repository path must be a directory.")
    if not any(repository == root or _is_child(repository, root) for root in roots):
        raise HTTPException(status_code=403, detail="Repository is outside the configured allow-list.")
    return repository


def _is_child(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _is_loopback_request(request: Request) -> tuple[bool, str | None]:
    client_host = request.client.host if request.client else ""
    try:
        if not ipaddress.ip_address(client_host).is_loopback:
            return False, "DevMind API accepts loopback clients only."
    except ValueError:
        return False, "DevMind API accepts loopback clients only."
    hostname = urlsplit("//" + request.headers.get("host", "")).hostname or ""
    hostname = hostname.lower()
    if hostname not in {"localhost", "127.0.0.1", "::1"}:
        return False, "DevMind API accepts local Host headers only."
    origin = request.headers.get("origin")
    if origin:
        origin_host = (urlsplit(origin).hostname or "").lower()
        if origin_host not in {"localhost", "127.0.0.1", "::1"}:
            return False, "DevMind API accepts local browser origins only."
    return True, None


def create_app() -> FastAPI:
    """Create the API application and its routes; separated for testability."""
    api = FastAPI(
        title="DevMind Local API",
        version="0.1.0",
        description="Local-only analysis API. Repository access is restricted to configured allow-list roots.",
        docs_url=None,
        redoc_url=None,
    )

    @api.middleware("http")
    async def restrict_remote_clients(request: Request, call_next):
        allowed, reason = _is_loopback_request(request)
        if not allowed:
            return JSONResponse(status_code=403, content={"detail": reason})
        return await call_next(request)

    api.add_api_route("/api/health", health, methods=["GET"])
    api.add_api_route("/api/analyze", analyze, methods=["POST"])
    api.add_api_route("/api/runs", list_runs, methods=["GET"])
    api.add_api_route("/api/runs/{run_id}", get_run, methods=["GET"])
    return api


_APP_COMPATIBILITY_ERROR: Exception | None = None
try:
    app: FastAPI | None = create_app()
except TypeError as exc:
    # Some pre-existing environments contain a FastAPI/Starlette version mismatch.
    app = None
    _APP_COMPATIBILITY_ERROR = exc


def main() -> None:
    """Run the API on loopback only; no command-line host override is exposed."""
    if app is None:
        raise RuntimeError(
            "FastAPI and Starlette are incompatible in this Python environment. "
            "Reinstall with `python -m pip install -e '.[api]'`."
        ) from _APP_COMPATIBILITY_ERROR
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Install the 'api' extra to run DevMind's FastAPI backend.") from exc
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")


if __name__ == "__main__":
    main()
