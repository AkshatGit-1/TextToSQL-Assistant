from core.prompt_builder import (
    build_sql_prompt,
    load_few_shot_examples,
)


def test_few_shot_examples_load_successfully():
    examples = load_few_shot_examples()

    assert isinstance(examples, str)
    assert examples.strip() != ""


def test_prompt_contains_focused_schema():
    prompt = build_sql_prompt(
        "What are the total sales by customer state?"
    )

    assert "analytics.fact_orders" in prompt
    assert "analytics.fact_order_items" in prompt
    assert "analytics.dim_customer" in prompt


def test_prompt_contains_few_shot_examples():
    prompt = build_sql_prompt(
        "What are the total sales by customer state?"
    )

    assert "FEW-SHOT SQL EXAMPLES:" in prompt
    assert "What are the total sales?" in prompt
    assert "analytics.fact_order_items" in prompt


def test_prompt_contains_sql_requirements():
    prompt = build_sql_prompt(
        "What are the total sales by customer state?"
    )

    assert "Return only one SQL SELECT statement." in prompt
    assert "Do not return markdown." in prompt
    assert "Do not include explanations." in prompt


def test_empty_question_is_rejected():
    try:
        build_sql_prompt("")
        assert False, "Expected ValueError for empty question"
    except ValueError:
        pass