from app.generation.openai_generator import generate_answer
from app.generation.prompt_builder import build_rag_prompt
from app.observability.langfuse_client import langfuse
from app.retrieval.search import search


def answer_question(question: str):
    with langfuse.start_as_current_observation(
        as_type="span",
        name="rag-request",
        input={"question": question},
    ) as rag_span:

        with langfuse.start_as_current_observation(
            as_type="span",
            name="retrieval",
            input={"question": question},
        ) as retrieval_span:

            retrieved_chunks = search(question)

            retrieval_span.update(
                output={
                    "chunks": [
                        {
                            "filename": chunk.filename,
                            "page_number": chunk.page_number,
                            "chunk_index": chunk.chunk_index,
                            "similarity": chunk.similarity,
                            "content": chunk.content,
                        }
                        for chunk in retrieved_chunks
                    ]
                }
            )

        prompt = build_rag_prompt(
            question=question,
            retrieved_chunks=retrieved_chunks,
        )

        with langfuse.start_as_current_observation(
            as_type="span",
            name="answer-generation",
            input={"prompt": prompt},
        ) as generation_span:

            answer = generate_answer(prompt)

            generation_span.update(
                output={
                    "answer": answer
                }
            )

        rag_span.update(
            output={
                "answer": answer,
            }
        )

        return {
            "answer": answer,
            "sources": retrieved_chunks,
        }