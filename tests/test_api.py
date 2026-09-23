import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from api.index import app

@pytest.fixture
def client():
    return TestClient(app)

def test_api_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "ResearchPilot Edge" in data["service"]

def test_api_dashboard(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "documents_count" in data
    assert "active_backend" in data

def test_api_demo_loading(client):
    response = client.post("/api/demo")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True

def test_api_chat(client):
    response = client.post("/api/chat", json={
        "query": "What is the NPU TOPS rating of Snapdragon X Elite?",
        "top_k": 3
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "answer" in data["data"]
    assert "sources" in data["data"]

def test_api_search(client):
    response = client.post("/api/search", json={
        "query": "quantization INT4",
        "top_k": 4
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "results" in data

def test_api_benchmark(client):
    response = client.post("/api/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data

def test_api_ui_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "ResearchPilot Edge" in response.text
