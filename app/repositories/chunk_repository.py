from app.db.connection import get_connection
from app.models.retrieval import RetrievedChunk

def create_chunk(
    document_id: int,
    content: str,
    page_number: int | None,
    chunk_index: int,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO document_chunks (
                    document_id,
                    content,
                    page_number,
                    chunk_index
                )
                VALUES (%s, %s, %s, %s)
                RETURNING
                    id,
                    document_id,
                    content,
                    page_number,
                    chunk_index,
                    created_at;
                """,
                (
                    document_id,
                    content,
                    page_number,
                    chunk_index,
                ),
            )

            return cursor.fetchone()

def get_chunks_without_embeddings():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    content
                FROM document_chunks
                WHERE embedding IS NULL
                ORDER BY id;
                """
            )

            return cursor.fetchall()


def update_chunk_embedding(
    chunk_id: int,
    embedding: list[float],
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE document_chunks
                SET embedding = %s
                WHERE id = %s;
                """,
                (
                    embedding,
                    chunk_id,
                ),
            )

def search_similar_chunks(
    query_embedding: list[float],
    limit: int = 3,
) -> list[RetrievedChunk]:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    dc.id,
                    d.filename,
                    dc.page_number,
                    dc.chunk_index,
                    dc.content,
                    1 - (dc.embedding <=> %s::vector) AS similarity
                FROM document_chunks dc
                JOIN documents d
                    ON dc.document_id = d.id
                WHERE dc.embedding IS NOT NULL
                ORDER BY dc.embedding <=> %s::vector
                LIMIT %s;
                """,
                (
                    query_embedding,
                    query_embedding,
                    limit,
                ),
            )

            rows = cursor.fetchall()

            return [
                RetrievedChunk(
                    chunk_id=row[0],
                    filename=row[1],
                    page_number=row[2],
                    chunk_index=row[3],
                    content=row[4],
                    similarity=row[5],
                )
                for row in rows
            ]

         