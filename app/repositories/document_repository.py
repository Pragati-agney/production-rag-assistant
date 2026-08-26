from app.db.connection import get_connection


def get_all_documents():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    id,
                    filename,
                    department,
                    created_at
                FROM documents
                ORDER BY id;
            """)

            return cursor.fetchall()

def create_document(filename: str, department: str | None):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO documents (
                    filename,
                    department
                )
                VALUES (%s, %s)
                RETURNING id, filename, department, created_at;
                """,
                (filename, department),
            )

            return cursor.fetchone()