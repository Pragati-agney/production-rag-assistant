from app.embeddings.openai_embeddings import create_embedding
from app.observability.langfuse_client import langfuse
from app.repositories.chunk_repository import search_similar_chunks


def search(question: str):
    with langfuse.start_as_current_observation(
        as_type="span",
        name="query-embedding",
        input={"question": question},
    ) as embedding_span:
        query_embedding = create_embedding(question)

        embedding_span.update(
            output={
                "dimensions": len(query_embedding)
            }
        )

    with langfuse.start_as_current_observation(
        as_type="span",
        name="pgvector-search",
        input={
            "top_k": 3
        },
    ) as search_span:
        results = search_similar_chunks(
            query_embedding=query_embedding,
            limit=3,
        )

        search_span.update(
            output={
                "results_returned": len(results),
                "scores": [
                    result.similarity
                    for result in results
                ],
            }
        )

    return results