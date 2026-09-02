from app.models.retrieval import RetrievedChunk


def build_rag_prompt(
    question: str,
    retrieved_chunks: list[RetrievedChunk],
) -> str:
    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"""
Source: {chunk.filename}, page {chunk.page_number}
Content:
{chunk.content}
""".strip()
        )

    context = "\n\n---\n\n".join(context_parts)

    return f"""
You are an internal company knowledge assistant.

Answer the user's question using only the context below.

If the answer is not present in the context, say:
"I don't know based on the available company documents."

Do not invent information.

Context:
{context}

Question:
{question}
""".strip()
