from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from devmind.api import (
    AnalyzeRequest,
    _APP_COMPATIBILITY_ERROR,
    _RUN_HISTORY,
    _is_loopback_request,
    _resolve_allowed_repository,
    analyze,
    app,
    get_run,
    health,
    list_runs,
)


def test_health_and_loopback_request_policy():
    assert health() == {"status": "ok", "service": "devmind-local-api"}
    local = SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"), headers={"host": "127.0.0.1:8000"})
    remote = SimpleNamespace(client=SimpleNamespace(host="192.168.1.10"), headers={"host": "127.0.0.1:8000"})
    foreign_origin = SimpleNamespace(
        client=SimpleNamespace(host="127.0.0.1"),
        headers={"host": "127.0.0.1:8000", "origin": "https://attacker.invalid"},
    )
    assert _is_loopback_request(local) == (True, None)
    assert _is_loopback_request(remote)[0] is False
    assert _is_loopback_request(foreign_origin)[0] is False


def test_analyze_uses_only_configured_repositories_and_records_history(tmp_path, monkeypatch):
    allowed = tmp_path / "projects"
    repository = allowed / "sample"
    repository.mkdir(parents=True)
    (repository / "maths.py").write_text("def divide(a, b):\n    return a / b\n", encoding="utf-8")
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.setenv("DEVMIND_API_REPOSITORY_ROOTS", str(allowed))
    _RUN_HISTORY.clear()

    record = analyze(AnalyzeRequest(repository=str(repository), bug_report="divide returns wrong result", top_k=3))
    assert record["report"]["evidence"][0]["path"] == "maths.py"
    assert list_runs()["runs"][0]["run_id"] == record["run_id"]
    assert get_run(record["run_id"]) == record
    with pytest.raises(HTTPException) as missing:
        get_run("missing")
    assert missing.value.status_code == 404
    with pytest.raises(HTTPException) as forbidden:
        _resolve_allowed_repository(str(outside))
    assert forbidden.value.status_code == 403


def test_api_requires_an_explicit_allow_list_and_validates_requests(tmp_path, monkeypatch):
    repository = tmp_path / "repo"
    repository.mkdir()
    monkeypatch.delenv("DEVMIND_API_REPOSITORY_ROOTS", raising=False)
    with pytest.raises(HTTPException) as missing_roots:
        _resolve_allowed_repository(str(repository))
    assert missing_roots.value.status_code == 503
    with pytest.raises(ValueError):
        AnalyzeRequest(repository=str(repository), bug_report=" ", top_k=1)
    with pytest.raises(ValueError):
        AnalyzeRequest(repository=str(repository), bug_report="issue", top_k=99)
    with pytest.raises(ValueError):
        AnalyzeRequest(repository=str(repository), bug_report="issue", top_k=1, unexpected="value")


@pytest.mark.skipif(app is None, reason=f"FastAPI/Starlette mismatch: {_APP_COMPATIBILITY_ERROR}")
def test_api_routes_are_registered():
    paths = {route.path for route in app.routes}
    assert {"/api/health", "/api/analyze", "/api/runs", "/api/runs/{run_id}"}.issubset(paths)


@pytest.mark.skipif(app is None, reason=f"FastAPI/Starlette mismatch: {_APP_COMPATIBILITY_ERROR}")
def test_api_http_request_allow_list_and_loopback_middleware(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    repository = allowed / "repo"
    repository.mkdir(parents=True)
    (repository / "sample.py").write_text("def run():\n    return True\n", encoding="utf-8")
    monkeypatch.setenv("DEVMIND_API_REPOSITORY_ROOTS", str(allowed))
    _RUN_HISTORY.clear()
    with TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 12345)) as client:
        response = client.post("/api/analyze", json={"repository": str(repository), "bug_report": "run fails"})
        assert response.status_code == 200
        assert response.json()["report"]["evidence"][0]["path"] == "sample.py"
        assert client.get("/api/runs").status_code == 200
    with TestClient(app, base_url="http://127.0.0.1", client=("192.168.1.10", 12345)) as remote_client:
        assert remote_client.get("/api/health").status_code == 403
