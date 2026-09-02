from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_chat_returns_answer():
    response = client.post(
        "/chat",
        json={
            "question": "What is our annual leave policy?"
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert "answer" in body
    assert isinstance(body["answer"], str)
    assert len(body["answer"]) > 0

    assert "sources" in body
    assert isinstance(body["sources"], list)


def test_chat_rejects_empty_question():
    response = client.post(
        "/chat",
        json={
            "question": ""
        },
    )

    assert response.status_code == 422