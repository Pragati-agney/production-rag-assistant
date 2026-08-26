from app.repositories.document_repository import (
    create_document,
    get_all_documents,
)


def main():
    created_document = create_document(
        filename="security_policy.pdf",
        department="Security",
    )

    print("Created:")
    print(created_document)

    print("\nAll documents:")

    documents = get_all_documents()

    for document in documents:
        print(document)


if __name__ == "__main__":
    main()