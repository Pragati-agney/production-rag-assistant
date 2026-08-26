from app.ingestion.chunker import chunk_page
from app.ingestion.pdf_extractor import extract_pdf_pages


def main():
    pages = extract_pdf_pages(
        "acme_employee_handbook.pdf"
    )

    for page in pages:
        chunks = chunk_page(
            page_number=page["page_number"],
            text=page["text"],
        )

        for chunk in chunks:
            print("=" * 60)
            print(
                f"PAGE {chunk['page_number']} "
                f"CHUNK {chunk['chunk_index']}"
            )
            print("=" * 60)
            print(chunk["content"])


if __name__ == "__main__":
    main()