from math import sqrt

from app.embeddings.openai_embeddings import create_embedding


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = sqrt(
        sum(b * b for b in vector_b)
    )

    return dot_product / (magnitude_a * magnitude_b)


def main():
    text_1 = "annual leave"
    text_2 = "vacation days"
    text_3 = "database server"

    embedding_1 = create_embedding(text_1)
    embedding_2 = create_embedding(text_2)
    embedding_3 = create_embedding(text_3)

    similarity_1_2 = cosine_similarity(
        embedding_1,
        embedding_2,
    )

    similarity_1_3 = cosine_similarity(
        embedding_1,
        embedding_3,
    )

    print(
        f'"{text_1}" vs "{text_2}" = '
        f"{similarity_1_2:.4f}"
    )

    print(
        f'"{text_1}" vs "{text_3}" = '
        f"{similarity_1_3:.4f}"
    )


if __name__ == "__main__":
    main()