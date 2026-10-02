from fastapi import APIRouter, HTTPException

from api.models import ClearConversationResponse, QueryRequest, QueryResponse
from core.query_pipeline import QueryPipeline


router = APIRouter()
pipeline = QueryPipeline()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.post("/api/query", response_model=QueryResponse)
def execute_query(request: QueryRequest) -> QueryResponse:
    try:
        result = pipeline.run(request.question)

        return QueryResponse(
            question=result["question"],
            status=result["status"],
            sql=result.get("sql"),
            results=result.get("results", []),
            attempts=result.get("attempts", 0),
            reason=result.get("reason"),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.post(
    "/api/conversation/clear",
    response_model=ClearConversationResponse,
)
def clear_conversation() -> ClearConversationResponse:
    pipeline.clear_memory()

    return ClearConversationResponse(
        status="success",
        message="Conversation memory cleared.",
    )