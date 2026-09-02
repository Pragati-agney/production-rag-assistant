from types import SimpleNamespace
from unittest.mock import patch

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
    fake_chunk = SimpleNamespace(
        filename="employee_handbook.pdf",
        page_number=1,
        similarity=0.95,
    )

    with patch("app.main.answer_question") as mock_answer_question:
        mock_answer_question.return_value = {
            "answer": "Employees receive 30 days of annual leave.",
            "sources": [fake_chunk],
        }

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