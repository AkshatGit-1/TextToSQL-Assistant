from core.llm_client import MockLLMClient
from core.prompt_builder import build_sql_prompt


class QueryGenerator:
    """Generate SQL from a natural-language business question."""

    def __init__(self):
        self.llm = MockLLMClient()

    def generate_sql(self, question: str) -> str:
        """Build the prompt and generate SQL."""
        prompt = build_sql_prompt(question)

        sql = self.llm.generate(prompt)

        return sql.strip()


if __name__ == "__main__":
    question = "How many orders are there?"

    generator = QueryGenerator()

    sql = generator.generate_sql(question)

    print("=" * 70)
    print("Generated SQL")
    print("=" * 70)
    print(sql)