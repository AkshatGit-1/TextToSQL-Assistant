from fastapi import FastAPI

from api.middleware import RequestIDMiddleware
from api.routes import router
from core.logging_config import configure_logging


configure_logging()

app = FastAPI(
    title="Text-to-SQL Analytics Assistant",
    description="LLM-powered natural-language analytics API.",
    version="1.0.0",
)

app.add_middleware(RequestIDMiddleware)

app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Text-to-SQL Analytics Assistant",
        "status": "running",
    }