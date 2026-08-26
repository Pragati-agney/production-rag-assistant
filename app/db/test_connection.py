from app.db.connection import get_connection


def main():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    d.filename,
                    dc.page_number,
                    dc.content
                FROM document_chunks dc
                JOIN documents d
                    ON dc.document_id = d.id
                ORDER BY d.id, dc.chunk_index
            """)

            rows = cursor.fetchall()

            for row in rows:
                print(row)


if __name__ == "__main__":
    main()