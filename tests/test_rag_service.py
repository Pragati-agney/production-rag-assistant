from unittest.mock import patch

from app.rag_service import answer_question
from app.repositories.chunk_repository import RetrievedChunk
from app.core.errors import ProviderError
from fastapi.testclient import TestClient
from app.main import app
from app.core.errors import DatabaseError

client = TestClient(app)
def test_answer_question_returns_answer_and_sources():
    fake_chunks = [
        RetrievedChunk(
            chunk_id=1,
            filename="acme_employee_handbook.pdf",
            page_number=1,
            chunk_index=0,
            content="Employees receive 30 days of paid annual leave.",
            similarity=0.91,
        )
    ]

    with patch(
        "app.rag_service.search",
        return_value=fake_chunks,
    ):
        with patch(
            "app.rag_service.generate_answer",
            return_value="Employees receive 30 days of paid annual leave.",
        ):
            result = answer_question(
                "How many vacation days do employees get?"
            )

    assert result["answer"] == (
        "Employees receive 30 days of paid annual leave."
    )

    assert len(result["sources"]) == 1

    assert result["sources"][0].filename == (
        "acme_employee_handbook.pdf"
    )

def test_answer_question_returns_unknown_when_no_chunks():
    with patch(
        "app.rag_service.search",
        return_value=[],
    ):
        with patch(
            "app.rag_service.generate_answer",
        ) as mock_generate:
            result = answer_question(
                "What is the company car leasing allowance?"
            )

    assert result == {
        "answer": (
            "I don't know based on the available company documents."
        ),
        "sources": [],
    }

    mock_generate.assert_not_called()

def test_answer_question_calls_generation_with_retrieved_context():
    fake_chunks = [
        RetrievedChunk(
            chunk_id=1,
            filename="acme_employee_handbook.pdf",
            page_number=1,
            chunk_index=0,
            content="Employees receive 30 days of paid annual leave.",
            similarity=0.91,
        )
    ]

    with patch(
        "app.rag_service.search",
        return_value=fake_chunks,
    ):
        with patch(
            "app.rag_service.generate_answer",
            return_value="Employees receive 30 days of paid annual leave.",
        ) as mock_generate:
            result = answer_question(
                "How many vacation days do employees get?"
            )

    mock_generate.assert_called_once()

    prompt = mock_generate.call_args.args[0]

    assert "Employees receive 30 days of paid annual leave." in prompt
    assert "How many vacation days do employees get?" in prompt

    assert result["answer"] == (
        "Employees receive 30 days of paid annual leave."
    )

def test_chat_returns_503_when_ai_provider_is_unavailable():
    fake_chunks = [
        RetrievedChunk(
            chunk_id=1,
            filename="acme_employee_handbook.pdf",
            page_number=1,
            chunk_index=0,
            content="Employees receive 30 days of paid annual leave.",
            similarity=0.91,
        )
    ]

    with patch(
        "app.rag_service.search",
        return_value=fake_chunks,
    ):
        with patch(
            "app.rag_service.generate_answer",
            side_effect=ProviderError(
                "OpenAI temporarily unavailable",
                retryable=True,
            ),
        ):
            response = client.post(
                "/chat",
                json={
                    "question": (
                        "How many vacation days do employees get?"
                    )
                },
            )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "The AI service is temporarily unavailable. "
            "Please try again."
        )
    }

def test_chat_returns_503_when_database_is_unavailable():
    with patch(
        "app.rag_service.search",
        side_effect=DatabaseError(
            "Database unavailable",
            retryable=True,
        ),
    ):
        response = client.post(
            "/chat",
            json={
                "question": "How many vacation days do employees get?"
            },
        )

    assert response.status_code == 503

    assert response.json() == {
        "detail": (
            "The knowledge service is temporarily unavailable. "
            "Please try again."
        )
    }