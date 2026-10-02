import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from fastapi.testclient import TestClient

from api.main import app
from api.routes import pipeline


client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Text-to-SQL Analytics Assistant",
        "status": "running",
    }


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_query_endpoint():
    pipeline.clear_memory()

    response = client.post(
        "/api/query",
        json={"question": "What are the total sales?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What are the total sales?"
    assert data["status"] == "success"
    assert data["sql"]
    assert data["results"]
    assert data["attempts"] >= 1


def test_query_endpoint_rejects_empty_question():
    response = client.post(
        "/api/query",
        json={"question": ""},
    )

    assert response.status_code == 422


def test_conversation_follow_up():
    pipeline.clear_memory()

    first_response = client.post(
        "/api/query",
        json={"question": "What are the total sales by customer state?"},
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "success"

    follow_up_response = client.post(
        "/api/query",
        json={"question": "Show only the top 5"},
    )

    assert follow_up_response.status_code == 200

    data = follow_up_response.json()

    assert data["status"] == "success"
    assert "LIMIT 5" in data["sql"].upper()


def test_clear_conversation_endpoint():
    response = client.post("/api/conversation/clear")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "message": "Conversation memory cleared.",
    }


def test_follow_up_requires_context_after_clear():
    response = client.post(
        "/api/query",
        json={"question": "Show only the top 5"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "clarification_required"
    assert data["sql"] is None
    assert data["attempts"] == 0