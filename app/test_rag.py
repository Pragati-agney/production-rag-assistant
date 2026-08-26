from app.rag_service import answer_question


def main():
    question = "How many vacation days do employees get?"
    

    result = answer_question(question)

    print("QUESTION")
    print(question)

    print("\nANSWER")
    print(result["answer"])

    print("\nSOURCES")

    for source in result["sources"]:
        (
            chunk_id,
            filename,
            page_number,
            chunk_index,
            content,
            similarity,
        ) = source

        print(
            f"- {filename}, page {page_number}, "
            f"similarity={similarity:.4f}"
        )


if __name__ == "__main__":
    main()