from app.repositories.document_repository import (
    create_document,
    get_all_documents,
)


def test_create_and_get_document():
    created_document = create_document(
        filename="security_policy.pdf",
        department="Security",
    )

    assert created_document is not None
    assert created_document[1] == "security_policy.pdf"
    assert created_document[2] == "Security"

    documents = get_all_documents()

    filenames = [
        document[1]
        for document in documents
    ]

    assert "security_policy.pdf" in filenames