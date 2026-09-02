from fastapi import FastAPI

from app.core.error_handlers import database_error_handler, provider_error_handler
from app.core.errors import DatabaseError, ProviderError
from app.core.logging_config import configure_logging
from app.rag_service import answer_question
from app.schemas.chat import ChatRequest, ChatResponse, Source

configure_logging()
app = FastAPI(
    title="Internal Knowledge Assistant",
    version="0.1.0",
)
app.add_exception_handler(
    ProviderError,
    provider_error_handler,
)

app.add_exception_handler(
    DatabaseError,
    database_error_handler,
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest) -> ChatResponse:
    result = answer_question(request.question)

    sources = []

    for chunk in result["sources"]:
        sources.append(
            Source(
                filename=chunk.filename,
                page_number=chunk.page_number,
                similarity=chunk.similarity,
            )
        )

    return ChatResponse(
        answer=result["answer"],
        sources=sources,
    )
