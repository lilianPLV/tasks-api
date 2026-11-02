import pytest

from app.main import create_app


@pytest.fixture()
def client():
    return create_app().test_client()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_version_default(client, monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    assert client.get("/version").get_json() == {"version": "dev"}


def test_version_from_env(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "1.2.3")
    assert client.get("/version").get_json() == {"version": "1.2.3"}


def test_add_and_list_tasks(client):
    created = client.post("/tasks", json={"title": "  apprendre la ci "})
    assert created.status_code == 201
    assert created.get_json() == {"id": 1, "title": "Apprendre la ci"}
    assert client.get("/tasks").get_json() == [{"id": 1, "title": "Apprendre la ci"}]


def test_add_task_invalid_title(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 400
