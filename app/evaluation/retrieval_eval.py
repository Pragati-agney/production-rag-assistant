from app.retrieval.search import search

EVALUATION_CASES = [
    {
        "question": "How many vacation days do employees get?",
        "expected_text": "Annual Leave",
    },
    {
        "question": "How many days per week can employees work remotely?",
        "expected_text": "Remote Work",
    },
    {
        "question": "How much money can employees spend on learning each year?",
        "expected_text": "Learning and Development",
    },
    {
        "question": "When do business expenses need to be submitted?",
        "expected_text": "Expenses",
    },
    {
        "question": "Where should confidential company information be stored?",
        "expected_text": "Information Security",
    },
]


def evaluate_retrieval():
    top_1_correct = 0
    top_3_correct = 0

    for case in EVALUATION_CASES:
        question = case["question"]
        expected_text = case["expected_text"]

        results = search(question)

        top_1_match = (
            len(results) > 0 and expected_text.lower() in results[0].content.lower()
        )

        top_3_match = any(
            expected_text.lower() in result.content.lower() for result in results[:3]
        )

        if top_1_match:
            top_1_correct += 1

        if top_3_match:
            top_3_correct += 1

        print("=" * 70)
        print(f"QUESTION: {question}")
        print(f"EXPECTED: {expected_text}")
        print(f"TOP-1 CORRECT: {top_1_match}")
        print(f"TOP-3 CORRECT: {top_3_match}")

        print("\nRetrieved:")

        for index, result in enumerate(results, start=1):
            print(
                f"{index}. "
                f"{result.filename}, "
                f"page {result.page_number}, "
                f"similarity={result.similarity:.4f}"
            )

            print(result.content[:150])
            print()

    total = len(EVALUATION_CASES)

    top_1_accuracy = top_1_correct / total
    top_3_accuracy = top_3_correct / total

    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(f"Top-1 accuracy: {top_1_correct}/{total} ({top_1_accuracy:.2%})")

    print(f"Top-3 accuracy: {top_3_correct}/{total} ({top_3_accuracy:.2%})")


if __name__ == "__main__":
    evaluate_retrieval()
