from app.db.connection import pool


def test_connection_pool_can_borrow_connection():
    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()

    assert result is not None
    assert result[0] == 1