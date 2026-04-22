from fastapi.testclient import TestClient


def test_health(monkeypatch):
    # Patch settings so no real Azure credentials are needed in CI
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://fake.openai.azure.com/")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "fake-key")
    monkeypatch.setenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4")
    monkeypatch.setenv("AZURE_SEARCH_ENDPOINT", "https://fake.search.windows.net")
    monkeypatch.setenv("AZURE_SEARCH_ADMIN_KEY", "fake-key")

    from app.main import app

    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
