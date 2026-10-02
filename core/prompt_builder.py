from pathlib import Path

from core.schema_linker import build_schema_context


BASE_DIR = Path(__file__).resolve().parents[1]
FEW_SHOT_FILE = BASE_DIR / "config" / "few_shot_examples.md"


def load_few_shot_examples() -> str:
    """Load approved few-shot SQL examples."""
    if not FEW_SHOT_FILE.exists():
        raise FileNotFoundError(
            f"Few-shot examples file not found: {FEW_SHOT_FILE}"
        )

    content = FEW_SHOT_FILE.read_text(
        encoding="utf-8"
    ).strip()

    if not content:
        raise ValueError("Few-shot examples file is empty.")

    return content


def build_sql_prompt(
    question: str,
    error_feedback: str | None = None,
    conversation_context: str | None = None,
) -> str:
    """Build a schema-aware prompt for Text-to-SQL generation."""
    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    focused_schema = build_schema_context(question)
    few_shot_examples = load_few_shot_examples()

    feedback_section = ""

    if error_feedback:
        feedback_section = f"""
PREVIOUS ATTEMPT FEEDBACK:
The previous SQL attempt failed validation or execution.

ERROR:
{error_feedback}

CORRECTION REQUIREMENT:
Generate a corrected SQL query that addresses the error above.
Do not repeat the same mistake.
""".strip()

    conversation_section = "No previous conversation."

    if conversation_context and conversation_context.strip():
        conversation_section = conversation_context.strip()

    return f"""
You are a Text-to-SQL assistant for a PostgreSQL analytics database.

Your task is to convert the user's business question into a valid SQL query.

DATABASE:
PostgreSQL

SCHEMA:
analytics

PREVIOUS CONVERSATION:
{conversation_section}

USER QUESTION:
{question.strip()}

FOCUSED SCHEMA:
{focused_schema}

BUSINESS METRICS AND RULES:
- Use only the analytics schema.
- Use fact and dimension tables according to their defined grain.
- Use COUNT(DISTINCT order_id) when counting orders.
- Use fact_order_items.price for product sales.
- Use fact_payments.payment_value for payment value.
- Use customer_unique_id when measuring unique customers.
- Use appropriate date keys or timestamps for date analysis.
- Do not invent tables, columns, relationships, or metrics.
- If the requested metric cannot be calculated from the available schema, do not fabricate it.
- Use previous conversation context when the current question refers to an earlier result.
- Treat the current USER QUESTION as the primary instruction.

FEW-SHOT SQL EXAMPLES:
{few_shot_examples}

{feedback_section}

SQL REQUIREMENTS:
- Return only one SQL SELECT statement.
- Do not return markdown.
- Do not include explanations.
- Do not include comments.
- Use fully qualified analytics table names.
- Generate executable PostgreSQL SQL.
- Follow the business metric definitions and SQL patterns shown in the examples.
- Use only tables and columns available in the focused schema.

OUTPUT:
Return only the SQL query.
""".strip()


if __name__ == "__main__":
    question = "What are the total sales by customer state?"

    prompt = build_sql_prompt(question)

    print("=" * 70)
    print("Generated Prompt")
    print("=" * 70)
    print(prompt)