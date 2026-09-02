from app.db.connection import get_connection


def test_database_connection():
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute("SELECT current_database();")
        result = cursor.fetchone()

    assert result is not None
    assert result[0] == "production_rag"
