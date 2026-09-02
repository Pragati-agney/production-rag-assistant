import os

from dotenv import load_dotenv
from langfuse.openai import OpenAI
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    RateLimitError,
)

from app.core.errors import ProviderError
from app.core.retry import with_retry

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _call_openai(prompt: str) -> str:
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
        )

        return response.output_text

    except RateLimitError as error:
        raise ProviderError(
            message=str(error),
            retryable=True,
        ) from error

    except (APITimeoutError, APIConnectionError) as error:
        raise ProviderError(
            message=str(error),
            retryable=True,
        ) from error

    except APIStatusError as error:
        retryable = error.status_code >= 500

        raise ProviderError(
            message=str(error),
            retryable=retryable,
        ) from error


def generate_answer(prompt: str) -> str:
    return with_retry(
        operation=lambda: _call_openai(prompt),
        max_attempts=3,
        base_delay_seconds=0.5,
    )
