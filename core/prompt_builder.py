from core.schema_linker import build_schema_context


def build_sql_prompt(question: str) -> str:
    """
    Build a schema-aware prompt for Text-to-SQL generation.
    """

    focused_schema = build_schema_context(question)

    return f"""
You are a Text-to-SQL assistant for a PostgreSQL analytics database.

Your task is to convert the user's business question into a valid SQL query.

DATABASE:
PostgreSQL

SCHEMA:
analytics

USER QUESTION:
{question}

FOCUSED SCHEMA:
{focused_schema}

BUSINESS RULES:
- Use only the analytics schema.
- Use fact and dimension tables according to their defined grain.
- Use COUNT(DISTINCT order_id) when counting orders.
- Use fact_order_items.price for product sales.
- Use fact_payments.payment_value for payment value.
- Use customer_unique_id when measuring unique customers.
- Use appropriate date keys or timestamps for date analysis.
- Do not invent tables, columns, relationships, or metrics.
- If the requested metric cannot be calculated from the available schema, do not fabricate it.

SQL REQUIREMENTS:
- Return only one SQL SELECT statement.
- Do not return markdown.
- Do not include explanations.
- Do not include comments.
- Use fully qualified analytics table names.
- Generate executable PostgreSQL SQL.

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