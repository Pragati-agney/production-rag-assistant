from app.observability.langfuse_client import langfuse

DATASET_NAME = "employee-handbook-v1"


DATASET_ITEMS = [
    {
        "input": {"question": "How many vacation days do employees get?"},
        "expected_output": {
            "answer": (
                "Full-time employees receive 30 days of paid "
                "annual leave per calendar year."
            )
        },
        "metadata": {
            "category": "annual_leave",
            "answerable": True,
        },
    },
    {
        "input": {"question": "How many days per week can employees work remotely?"},
        "expected_output": {
            "answer": (
                "Employees may work remotely up to three days per week "
                "when their role permits it and their manager approves."
            )
        },
        "metadata": {
            "category": "remote_work",
            "answerable": True,
        },
    },
    {
        "input": {
            "question": "How much money can employees spend on learning each year?"
        },
        "expected_output": {
            "answer": ("Each employee has an annual learning budget of EUR 1,500.")
        },
        "metadata": {
            "category": "learning_and_development",
            "answerable": True,
        },
    },
    {
        "input": {"question": "When do business expenses need to be submitted?"},
        "expected_output": {
            "answer": (
                "Business expenses must be submitted within 30 days of the transaction."
            )
        },
        "metadata": {
            "category": "expenses",
            "answerable": True,
        },
    },
    {
        "input": {
            "question": ("Where should confidential company information be stored?")
        },
        "expected_output": {
            "answer": (
                "Confidential company information must only be stored "
                "in approved company systems."
            )
        },
        "metadata": {
            "category": "information_security",
            "answerable": True,
        },
    },
    {
        "input": {"question": "What is the company car leasing allowance?"},
        "expected_output": {
            "answer": ("I don't know based on the available company documents.")
        },
        "metadata": {
            "category": "unknown",
            "answerable": False,
        },
    },
]


def main():
    print(f"Adding items to dataset: {DATASET_NAME}")

    for index, item in enumerate(DATASET_ITEMS, start=1):
        langfuse.create_dataset_item(
            dataset_name=DATASET_NAME,
            input=item["input"],
            expected_output=item["expected_output"],
            metadata=item["metadata"],
        )

        print(f"Added {index}/{len(DATASET_ITEMS)}: {item['input']['question']}")

    print("Dataset creation completed.")


if __name__ == "__main__":
    main()
