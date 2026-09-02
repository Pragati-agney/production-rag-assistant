import re


def chunk_page(page_number: int, text: str):
    sections = re.split(
        r"(?=\d+\.\s+[A-Z])",
        text,
    )

    chunks = []

    chunk_index = 0

    for section in sections:
        section = section.strip()

        if not section:
            continue

        chunks.append(
            {
                "page_number": page_number,
                "chunk_index": chunk_index,
                "content": section,
            }
        )

        chunk_index += 1

    return chunks
