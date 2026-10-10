import logging
import time

from fastapi import APIRouter, HTTPException, Request

from api.models import ClearConversationResponse, QueryRequest, QueryResponse
from core.query_pipeline import QueryPipeline

logger = logging.getLogger(__name__)

router = APIRouter()
pipeline = QueryPipeline()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.post("/api/query", response_model=QueryResponse)
def execute_query(
    request: Request,
    query_request: QueryRequest,
) -> QueryResponse:
    start_time = time.perf_counter()

    request_id = getattr(request.state, "request_id", "unknown")

    logger.info(
        "Query request received | request_id=%s | question=%s",
        request_id,
        query_request.question,
    )

    try:
        result = pipeline.run(query_request.question)

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "Query request completed | request_id=%s | status=%s | attempts=%s | duration_ms=%.2f",
            request_id,
            result["status"],
            result.get("attempts", 0),
            duration_ms,
        )

        return QueryResponse(
            question=result["question"],
            status=result["status"],
            sql=result.get("sql"),
            results=result.get("results", []),
            attempts=result.get("attempts", 0),
            reason=result.get("reason"),
        )

    except Exception:
        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.exception(
            "Query request failed | request_id=%s | duration_ms=%.2f",
            request_id,
            duration_ms,
        )

        raise HTTPException(
            status_code=500,
            detail="Query processing failed.",
        ) from None

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