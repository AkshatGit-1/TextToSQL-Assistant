from fastapi import FastAPI

from api.routes import router


app = FastAPI(
    title="Text-to-SQL Analytics Assistant",
    description="LLM-powered natural-language analytics API.",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "Text-to-SQL Analytics Assistant",
        "status": "running",
    }