from psycopg_pool import ConnectionPool


DATABASE_URL = (
    "dbname=production_rag "
    "user=pragatichinnayya "
    "host=localhost "
    "port=5432"
)


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=2,
    max_size=5,
    timeout=5,
    open=True,
)


def get_connection():
    return pool.connection()