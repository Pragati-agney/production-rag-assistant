from app.embeddings.openai_embeddings import create_embedding
from app.repositories.chunk_repository import (
    get_chunks_without_embeddings,
    update_chunk_embedding,
)


def embed_missing_chunks():
    chunks = get_chunks_without_embeddings()

    print(f"Found {len(chunks)} chunks without embeddings.")

    for chunk_id, content in chunks:
        print(f"Embedding chunk {chunk_id}...")

        embedding = create_embedding(content)

        update_chunk_embedding(
            chunk_id=chunk_id,
            embedding=embedding,
        )

    print("Embedding complete.")


if __name__ == "__main__":
    embed_missing_chunks()