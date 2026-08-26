from app.observability.langfuse_client import langfuse


def main():
    with langfuse.start_as_current_observation(
        as_type="span",
        name="test-rag-trace",
        input={
            "question": "How many vacation days do employees get?"
        },
    ) as trace:

        trace.update(
            output={
                "answer": "Employees receive 30 days of annual leave."
            }
        )

    langfuse.flush()

    print("Test trace sent to Langfuse.")


if __name__ == "__main__":
    main()