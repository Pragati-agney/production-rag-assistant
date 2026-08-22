from fastapi import FastAPI

from app.schemas.chat import ChatRequest, ChatResponse


app = FastAPI(
    title="Internal Knowledge Assistant",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "ok"
    }


@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest) -> ChatResponse:

    return ChatResponse(
        answer=f"You asked: {request.question}"
    )