import pytest
from fastapi.testclient import TestClient

from app.main import app, reset_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_store():
    reset_store()
    yield
    reset_store()


def test_health_and_ready():
    assert client.get("/healthz").json() == {"status": "ok"}
    assert client.get("/readyz").json() == {"status": "ready"}


def test_version_reports_env(monkeypatch):
    body = client.get("/version").json()
    assert "version" in body
    assert body["uptime_seconds"] >= 0


def test_create_list_get_delete_item():
    created = client.post("/items", json={"name": "widget", "quantity": 3})
    assert created.status_code == 201
    item = created.json()
    assert item == {"id": 1, "name": "widget", "quantity": 3}

    assert client.get("/items").json() == [item]
    assert client.get("/items/1").json() == item

    assert client.delete("/items/1").status_code == 204
    assert client.get("/items/1").status_code == 404


def test_ids_increment():
    a = client.post("/items", json={"name": "a", "quantity": 1}).json()
    b = client.post("/items", json={"name": "b", "quantity": 1}).json()
    assert b["id"] == a["id"] + 1


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "", "quantity": 1},
        {"name": "x", "quantity": -1},
        {"quantity": 1},
    ],
)
def test_invalid_payload_rejected(payload):
    assert client.post("/items", json=payload).status_code == 422


def test_delete_missing_returns_404():
    assert client.delete("/items/999").status_code == 404
