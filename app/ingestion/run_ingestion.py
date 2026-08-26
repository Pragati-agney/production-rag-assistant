from app.ingestion.ingest_document import ingest_document


def main():
    result = ingest_document(
        file_path="acme_employee_handbook.pdf",
        department="HR",
    )

    print(result)


if __name__ == "__main__":
    main()