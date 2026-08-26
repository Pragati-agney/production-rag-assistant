from dataclasses import dataclass


@dataclass
class RetrievedChunk:
    chunk_id: int
    filename: str
    page_number: int | None
    chunk_index: int
    content: str
    similarity: float