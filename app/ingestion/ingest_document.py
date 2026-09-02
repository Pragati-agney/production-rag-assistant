from pathlib import Path

from app.ingestion.chunker import chunk_page
from app.ingestion.pdf_extractor import extract_pdf_pages
from app.repositories.chunk_repository import create_chunk
from app.repositories.document_repository import create_document


def ingest_document(
    file_path: str,
    department: str | None,
):
    path = Path(file_path)

    document = create_document(
        filename=path.name,
        department=department,
    )

    document_id = document[0]

    pages = extract_pdf_pages(file_path)

    total_chunks = 0

    for page in pages:
        chunks = chunk_page(
            page_number=page["page_number"],
            text=page["text"],
        )

        for chunk in chunks:
            create_chunk(
                document_id=document_id,
                content=chunk["content"],
                page_number=chunk["page_number"],
                chunk_index=chunk["chunk_index"],
            )

            total_chunks += 1

    return {
        "document_id": document_id,
        "filename": path.name,
        "pages": len(pages),
        "chunks": total_chunks,
    }
