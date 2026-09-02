from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )


class Source(BaseModel):
    filename: str
    page_number: int | None
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
