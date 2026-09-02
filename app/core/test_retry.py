from app.core.errors import ProviderError
from app.core.retry import with_retry
from app.observability.langfuse_client import langfuse

attempts = 0


def flaky_operation():
    global attempts

    attempts += 1

    print(f"Running attempt {attempts}")

    if attempts < 3:
        raise ProviderError(
            "Simulated temporary failure",
            retryable=True,
        )

    return "Success!"


def main():
    try:
        result = with_retry(
            operation=flaky_operation,
            max_attempts=3,
            base_delay_seconds=0.5,
        )

        print(result)

    except ProviderError as error:
        print("Operation failed.")
        print(f"Retryable: {error.retryable}")
        print(f"Reason: {error}")

    langfuse.flush()


if __name__ == "__main__":
    main()
