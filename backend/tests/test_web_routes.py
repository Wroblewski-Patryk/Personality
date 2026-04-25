from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient

import app.main as app_main


def _write_web_dist(tmp_path: Path) -> Path:
    dist_dir = tmp_path / "web" / "dist"
    dist_dir.mkdir(parents=True)
    (dist_dir / "index.html").write_text(
        "<!doctype html><html><body><div id='root'>AION Web</div></body></html>",
        encoding="utf-8",
    )
    return dist_dir


def _client() -> TestClient:
    app = FastAPI()
    app.get("/", include_in_schema=False)(app_main.web_index)
    app.get("/{frontend_path:path}", include_in_schema=False)(app_main.web_spa)
    return TestClient(app)


def test_root_serves_web_index_when_dist_is_ready(tmp_path, monkeypatch) -> None:
    dist_dir = _write_web_dist(tmp_path)
    monkeypatch.setattr(app_main, "_WEB_DIST_DIR", dist_dir)

    client = _client()
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "AION Web" in response.text


def test_frontend_route_falls_back_to_web_index(tmp_path, monkeypatch) -> None:
    dist_dir = _write_web_dist(tmp_path)
    monkeypatch.setattr(app_main, "_WEB_DIST_DIR", dist_dir)

    client = _client()
    response = client.get("/chat")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "AION Web" in response.text


def test_blocklisted_route_is_not_served_as_spa(tmp_path, monkeypatch) -> None:
    dist_dir = _write_web_dist(tmp_path)
    monkeypatch.setattr(app_main, "_WEB_DIST_DIR", dist_dir)

    client = _client()
    response = client.get("/health")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not found."}


def test_root_returns_404_when_web_build_is_missing(tmp_path, monkeypatch) -> None:
    dist_dir = tmp_path / "web" / "dist"
    dist_dir.mkdir(parents=True)
    monkeypatch.setattr(app_main, "_WEB_DIST_DIR", dist_dir)

    client = _client()
    response = client.get("/")

    assert response.status_code == 404
    assert response.json() == {"detail": "Web client build is not available."}
