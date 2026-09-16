from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_rejects_invalid_url():
    response = client.post("/api/analyze", json={"url": "ftp://example.com"})
    assert response.status_code == 422
