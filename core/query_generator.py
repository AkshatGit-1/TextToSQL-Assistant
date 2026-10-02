from core.llm_client import LLMClient
from core.prompt_builder import build_sql_prompt
from core.sql_validator import validate_sql


class QueryGenerator:
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or LLMClient()

    def generate_sql(
        self,
        question: str,
        error_feedback: str | None = None,
        conversation_context: str | None = None,
    ) -> str:
        prompt = build_sql_prompt(
            question,
            error_feedback=error_feedback,
            conversation_context=conversation_context,
        )

        sql = self.llm.generate(prompt)

        return validate_sql(sql)