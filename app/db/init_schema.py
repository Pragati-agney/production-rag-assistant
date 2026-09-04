from pathlib import Path

from app.db.connection import get_connection

SQL_FILE = (
    Path(__file__).resolve().parents[2]
    / "db"
    / "init"
    / "001_init.sql"
)


def init_schema() -> None:
    sql = SQL_FILE.read_text(encoding="utf-8")

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql)

        connection.commit()

    print("Database schema initialized successfully.")


if __name__ == "__main__":
    init_schema()