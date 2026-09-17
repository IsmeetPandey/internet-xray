import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app  # noqa: E402

client = TestClient(app)


def sample():
    return {"page_title": "Example", "requested_url": "https://example.com", "final_url": "https://example.com/", "request_count": 1, "third_party_request_count": 0, "failed_request_count": 0, "known_response_bytes": 100, "requests": []}


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_rejects_invalid_url():
    response = client.post("/api/analyze", json={"url": "ftp://example.com"})
    assert response.status_code == 422


def test_json_report_endpoint():
    response = client.post("/api/report/json", json=sample())
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert response.json()["schema_version"] == "1.0"


def test_html_report_endpoint():
    response = client.post("/api/report/html", json=sample())
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Internet X-Ray" in response.text
