from app.db.connection import get_connection


def main():
    with get_connection() as connection, connection.cursor() as cursor:
        cursor.execute("SHOW statement_timeout;")
        timeout = cursor.fetchone()

        print("Current statement timeout:")
        print(timeout)

        print("Starting slow query...")

        cursor.execute("SELECT pg_sleep(5);")

        print("Query finished.")


if __name__ == "__main__":
    main()
