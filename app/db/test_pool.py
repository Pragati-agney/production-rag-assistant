from app.db.connection import pool


def main():
    print("Initial pool stats:")
    print(pool.get_stats())

    with pool.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT current_database();"
            )

            result = cursor.fetchone()

            print("\nDatabase:")
            print(result)

            print("\nPool stats while connection is borrowed:")
            print(pool.get_stats())

    print("\nPool stats after connection is returned:")
    print(pool.get_stats())


if __name__ == "__main__":
    main()