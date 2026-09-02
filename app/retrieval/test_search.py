from app.retrieval.search import search


def main():
    question = "How many vacation days do employees get?"

    results = search(question)

    print(f"Question: {question}")
    print()

    for result in results:
        print("=" * 60)
        print(f"Similarity: {result.similarity:.4f}")
        print(f"File: {result.filename}")
        print(f"Page: {result.page_number}")
        print(f"Chunk: {result.chunk_index}")
        print()
        print(result.content)


if __name__ == "__main__":
    main()
