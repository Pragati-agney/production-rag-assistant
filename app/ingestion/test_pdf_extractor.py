from app.ingestion.pdf_extractor import extract_pdf_pages


def main():
    pages = extract_pdf_pages("acme_employee_handbook.pdf")

    for page in pages:
        print("=" * 60)
        print(f"PAGE {page['page_number']}")
        print("=" * 60)
        print(page["text"])


if __name__ == "__main__":
    main()
