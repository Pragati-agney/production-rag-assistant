from app.observability.langfuse_client import langfuse


def main():
    success = langfuse.auth_check()

    print("Langfuse authentication successful:")
    print(success)


if __name__ == "__main__":
    main()
