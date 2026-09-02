import random
import time
from collections.abc import Callable
from typing import TypeVar

from app.core.errors import ProviderError
from app.observability.langfuse_client import langfuse

T = TypeVar("T")


def with_retry(
    operation: Callable[[], T],
    max_attempts: int = 3,
    base_delay_seconds: float = 0.5,
) -> T:
    attempt = 1

    while True:
        with langfuse.start_as_current_observation(
            as_type="span",
            name=f"retry-attempt-{attempt}",
            input={
                "attempt": attempt,
                "max_attempts": max_attempts,
            },
        ) as attempt_span:
            try:
                result = operation()

                attempt_span.update(
                    output={
                        "status": "success",
                    }
                )

                return result

            except ProviderError as error:
                attempt_span.update(
                    output={
                        "status": "failed",
                        "retryable": error.retryable,
                        "error": str(error),
                    }
                )

                if not error.retryable:
                    raise

                if attempt >= max_attempts:
                    raise

                delay = base_delay_seconds * (2 ** (attempt - 1))

                jitter = random.uniform(
                    0,
                    delay * 0.2,
                )

                final_delay = delay + jitter

                attempt_span.update(
                    metadata={
                        "backoff_seconds": final_delay,
                    }
                )

                print(f"Attempt {attempt} failed. Retrying in {final_delay:.2f}s...")

                time.sleep(final_delay)

                attempt += 1
