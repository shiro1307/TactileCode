import io
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)


def create_dummy_png_bytes() -> bytes:
    img = Image.new("RGB", (100, 100), color=(73, 109, 137))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model_name" in data


def test_get_sample_architecture():
    response = client.get("/api/diagrams/sample/architecture")
    assert response.status_code == 200
    data = response.json()
    assert "diagram_id" in data
    assert data["status"] == "completed"
    assert "graph" in data
    assert len(data["graph"]["nodes"]) > 0
    assert len(data["graph"]["edges"]) > 0
    assert data["metadata"]["node_count"] == len(data["graph"]["nodes"])


def test_upload_valid_diagram():
    png_bytes = create_dummy_png_bytes()
    response = client.post(
        "/api/diagrams",
        files={"file": ("test_diagram.png", png_bytes, "image/png")}
    )
    assert response.status_code == 201
    data = response.json()
    assert "diagram_id" in data
    assert data["status"] == "completed"
    assert "graph" in data
    assert len(data["graph"]["nodes"]) > 0

    # Retrieve diagram by ID
    diagram_id = data["diagram_id"]
    get_res = client.get(f"/api/diagrams/{diagram_id}")
    assert get_res.status_code == 200
    assert get_res.json()["diagram_id"] == diagram_id


def test_upload_invalid_mime_type():
    response = client.post(
        "/api/diagrams",
        files={"file": ("malicious.exe", b"MZ...", "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_get_nonexistent_diagram():
    response = client.get("/api/diagrams/unknown_id_12345")
    assert response.status_code == 404


def test_query_node_neighbors():
    sample_res = client.get("/api/diagrams/sample/architecture")
    diagram_id = sample_res.json()["diagram_id"]

    query_res = client.get(f"/api/diagrams/{diagram_id}/nodes/api_gateway/neighbors")
    assert query_res.status_code == 200
    neighbors = query_res.json()
    assert neighbors["node_id"] == "api_gateway"
    assert "incoming" in neighbors
    assert "outgoing" in neighbors
    assert neighbors["total_connections"] > 0
