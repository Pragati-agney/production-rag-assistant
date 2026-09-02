from pathlib import Path

from pypdf import PdfReader


def extract_pdf_pages(file_path: str):
    pdf_path = Path(file_path)

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    return pages
