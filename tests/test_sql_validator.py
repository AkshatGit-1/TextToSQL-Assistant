import pytest

from core.sql_validator import SQLValidationError, validate_sql


def test_valid_select_is_accepted():
    sql = """
    SELECT
        c.customer_state,
        SUM(i.price) AS total_sales
    FROM analytics.fact_order_items i
    JOIN analytics.fact_orders o
        ON i.order_id = o.order_id
    JOIN analytics.dim_customer c
        ON o.customer_key = c.customer_key
    GROUP BY c.customer_state;
    """

    result = validate_sql(sql)

    assert result.upper().startswith("SELECT")
    assert "analytics.fact_order_items" in result
    assert "analytics.fact_orders" in result
    assert "analytics.dim_customer" in result


@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO analytics.fact_orders (order_id) VALUES ('test');",
        "UPDATE analytics.fact_orders SET order_id = 'test';",
        "DELETE FROM analytics.fact_orders;",
        "DROP TABLE analytics.fact_orders;",
    ],
)
def test_non_select_statements_are_rejected(sql):
    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_multiple_statements_are_rejected():
    sql = """
    SELECT COUNT(*) FROM analytics.fact_orders;
    DELETE FROM analytics.fact_orders;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM analytics.fact_orders -- comment",
        "SELECT /* comment */ * FROM analytics.fact_orders",
    ],
)
def test_comments_are_rejected(sql):
    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_wrong_schema_is_rejected():
    sql = """
    SELECT *
    FROM public.orders;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_unqualified_table_is_rejected():
    sql = """
    SELECT *
    FROM fact_orders;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_empty_sql_is_rejected():
    with pytest.raises(SQLValidationError):
        validate_sql("")


def test_whitespace_sql_is_rejected():
    with pytest.raises(SQLValidationError):
        validate_sql("   ")


def test_cte_with_analytics_tables_is_allowed():
    sql = """
    WITH order_summary AS (
        SELECT
            order_id,
            customer_key
        FROM analytics.fact_orders
    )
    SELECT COUNT(*)
    FROM order_summary;
    """

    result = validate_sql(sql)

    assert result.upper().startswith("WITH")
    assert "analytics.fact_orders" in result


def test_invalid_sql_is_rejected():
    sql = """
    SELECT *
    analytics.fact_orders
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)
        
def test_unknown_table_is_rejected():
    sql = """
    SELECT *
    FROM analytics.fake_table;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_allowed_tables_are_accepted():
    sql = """
    SELECT
        c.customer_state,
        COUNT(*) AS customer_count
    FROM analytics.dim_customer AS c
    GROUP BY c.customer_state;
    """

    result = validate_sql(sql)

    assert "analytics.dim_customer" in result


def test_multiple_allowed_tables_are_accepted():
    sql = """
    SELECT
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM analytics.fact_orders AS o
    JOIN analytics.dim_customer AS c
        ON o.customer_key = c.customer_key
    GROUP BY c.customer_state;
    """

    result = validate_sql(sql)

    assert "analytics.fact_orders" in result
    assert "analytics.dim_customer" in result
    
def test_allowed_column_is_accepted():
    sql = """
    SELECT
        c.customer_state
    FROM analytics.dim_customer AS c;
    """

    result = validate_sql(sql)

    assert "c.customer_state" in result


def test_invalid_column_is_rejected():
    sql = """
    SELECT
        c.fake_column
    FROM analytics.dim_customer AS c;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_invalid_unqualified_column_is_rejected():
    sql = """
    SELECT
        fake_column
    FROM analytics.dim_customer;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_valid_join_columns_are_accepted():
    sql = """
    SELECT
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM analytics.fact_orders AS o
    JOIN analytics.dim_customer AS c
        ON o.customer_key = c.customer_key
    GROUP BY c.customer_state;
    """

    result = validate_sql(sql)

    assert "o.customer_key" in result
    assert "c.customer_key" in result
    assert "c.customer_state" in result


def test_select_star_is_allowed():
    sql = """
    SELECT *
    FROM analytics.dim_customer;
    """

    result = validate_sql(sql)

    assert "SELECT *" in result


def test_table_alias_with_valid_column_is_accepted():
    sql = """
    SELECT
        customer.customer_city
    FROM analytics.dim_customer AS customer;
    """

    result = validate_sql(sql)

    assert "customer.customer_city" in result
    
def test_cte_columns_are_allowed():
    sql = """
    WITH customer_orders AS (
        SELECT
            customer_key,
            COUNT(DISTINCT order_id) AS order_count
        FROM analytics.fact_orders
        GROUP BY customer_key
    )
    SELECT
        customer_key,
        order_count
    FROM customer_orders;
    """

    result = validate_sql(sql)

    assert "customer_key" in result
    assert "order_count" in result


def test_cte_with_invalid_source_column_is_rejected():
    sql = """
    WITH customer_orders AS (
        SELECT
            fake_column
        FROM analytics.fact_orders
    )
    SELECT *
    FROM customer_orders;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_subquery_with_valid_columns_is_accepted():
    sql = """
    SELECT
        x.customer_state,
        x.order_count
    FROM (
        SELECT
            c.customer_state,
            COUNT(DISTINCT o.order_id) AS order_count
        FROM analytics.fact_orders AS o
        JOIN analytics.dim_customer AS c
            ON o.customer_key = c.customer_key
        GROUP BY c.customer_state
    ) AS x;
    """

    result = validate_sql(sql)

    assert "c.customer_state" in result
    assert "o.order_id" in result


def test_subquery_with_invalid_column_is_rejected():
    sql = """
    SELECT *
    FROM (
        SELECT
            c.fake_column
        FROM analytics.dim_customer AS c
    ) AS x;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)