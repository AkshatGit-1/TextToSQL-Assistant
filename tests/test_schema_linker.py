from core.schema_linker import find_relevant_tables, build_schema_context


def test_customer_state_sales():
    question = "What are the total sales by customer state?"

    tables = find_relevant_tables(question)

    assert "order_items" in tables
    assert "customers" in tables

    context = build_schema_context(question)

    assert "analytics.fact_order_items" in context
    assert "analytics.dim_customer" in context
    assert "analytics.fact_orders" in context


def test_payment_type_payment_value():
    question = "Which payment type has the highest payment value?"

    tables = find_relevant_tables(question)

    assert "payments" in tables
    assert "payment_type" in tables

    context = build_schema_context(question)

    assert "analytics.fact_payments" in context
    assert "analytics.dim_payment_type" in context


def test_review_score_by_product_category():
    question = "What is the average review score by product category?"

    tables = find_relevant_tables(question)

    assert "reviews" in tables
    assert "products" in tables
    assert "order_items" in tables

    context = build_schema_context(question)

    assert "analytics.fact_reviews" in context
    assert "analytics.dim_product" in context
    assert "analytics.fact_order_items" in context


def test_delivered_orders_by_month():
    question = "How many orders were delivered each month?"

    tables = find_relevant_tables(question)

    assert "orders" in tables
    assert "date" in tables
    assert "order_status" in tables

    context = build_schema_context(question)

    assert "analytics.fact_orders" in context
    assert "analytics.dim_date" in context
    assert "analytics.dim_order_status" in context


def test_focused_schema_excludes_global_sections():
    question = "Which payment type has the highest payment value?"

    context = build_schema_context(question)

    assert "## Relationships" not in context
    assert "## Query Rules" not in context
    assert "## Facts" not in context