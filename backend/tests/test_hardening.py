import json
import sqlite3

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app import archive


@pytest.mark.parametrize('value', ['NaN', 'Infinity', '-Infinity'])
def test_nonfinite_json_is_rejected_without_server_error(value):
    with TestClient(app) as client:
        response = client.post('/api/simulations/preview', content='{"overrides":{"cac":'+value+'}}', headers={'Content-Type':'application/json'})
    assert response.status_code == 422
    assert isinstance(response.json()['detail'], str)


@pytest.mark.parametrize('streamed', [False, True])
def test_body_limit_precedes_json_parsing(streamed):
    content = b' ' * (128 * 1024 + 1)
    with TestClient(app) as client:
        response = client.post('/api/simulations/preview', content=iter([content[:65536], content[65536:]]) if streamed else content)
    assert response.status_code == 413


def test_stale_database_returns_service_error(tmp_path, monkeypatch):
    target = tmp_path / 'stale.sqlite3'
    target.write_bytes(archive.DATABASE.read_bytes())
    with sqlite3.connect(target) as db:
        db.execute("UPDATE model_versions SET checksum='wrong'")
    monkeypatch.setattr(archive, 'DATABASE', target)
    with TestClient(app) as client:
        assert client.get('/api/health').status_code == 503
        assert client.get('/api/reference').status_code == 503


def test_missing_manifest_returns_service_error(tmp_path, monkeypatch):
    monkeypatch.setattr(archive, 'DATA', tmp_path)
    with TestClient(app) as client:
        assert client.get('/api/files').status_code == 503


def test_cors_allows_configured_origin_only():
    with TestClient(app) as client:
        allowed = client.options('/api/simulations/preview', headers={'Origin':'http://127.0.0.1:5173','Access-Control-Request-Method':'POST'})
        denied = client.options('/api/simulations/preview', headers={'Origin':'https://untrusted.example','Access-Control-Request-Method':'POST'})
    assert allowed.headers['access-control-allow-origin'] == 'http://127.0.0.1:5173'
    assert 'access-control-allow-origin' not in denied.headers
