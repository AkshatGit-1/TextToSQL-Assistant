from typing import Any

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)


class QueryResponse(BaseModel):
    question: str
    status: str
    sql: str | None = None
    results: list[dict[str, Any]] = Field(default_factory=list)
    attempts: int = 0
    reason: str | None = None


class ClearConversationResponse(BaseModel):
    status: str
    message: str