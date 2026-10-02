import pytest

from core.sql_validator import SQLValidationError, validate_sql


@pytest.mark.parametrize(
    "malicious_sql",
    [
        """
        SELECT *
        FROM analytics.fact_orders;
        DROP TABLE analytics.fact_orders;
        """,
        """
        DELETE FROM analytics.fact_orders;
        """,
        """
        UPDATE analytics.fact_orders
        SET order_id = 'malicious';
        """,
        """
        INSERT INTO analytics.fact_orders (order_id)
        VALUES ('malicious');
        """,
        """
        DROP TABLE analytics.fact_orders;
        """,
    ],
)
def test_destructive_or_multiple_statements_are_blocked(
    malicious_sql,
):
    with pytest.raises(SQLValidationError):
        validate_sql(malicious_sql)


@pytest.mark.parametrize(
    "injection_sql",
    [
        """
        SELECT *
        FROM public.users;
        """,
        """
        SELECT *
        FROM pg_catalog.pg_tables;
        """,
        """
        SELECT *
        FROM information_schema.tables;
        """,
        """
        SELECT *
        FROM analytics.fact_orders
        WHERE order_id = '1'
        OR 1 = 1;
        """,
    ],
)
def test_schema_and_injection_attempts_are_blocked(
    injection_sql,
):
    with pytest.raises(SQLValidationError):
        validate_sql(injection_sql)


@pytest.mark.parametrize(
    "injection_sql",
    [
        """
        SELECT *
        FROM public.users;
        """,
        """
        SELECT *
        FROM pg_catalog.pg_tables;
        """,
        """
        SELECT *
        FROM information_schema.tables;
        """,
        """
        SELECT *
        FROM analytics.fact_orders
        WHERE order_id = '1';
        DROP TABLE analytics.fact_orders;
        """,
    ],
)
def test_schema_and_injection_attempts_are_blocked(
    injection_sql,
):
    with pytest.raises(SQLValidationError):
        validate_sql(injection_sql)


def test_valid_read_only_query_is_allowed():
    sql = """
    SELECT
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM analytics.fact_orders o
    JOIN analytics.dim_customer c
        ON o.customer_key = c.customer_key
    GROUP BY c.customer_state;
    """

    validated_sql = validate_sql(sql)

    assert "SELECT" in validated_sql.upper()
    assert "analytics.fact_orders" in validated_sql
    assert "analytics.dim_customer" in validated_sql


def test_unknown_table_is_blocked():
    sql = """
    SELECT *
    FROM analytics.secret_table;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)


def test_unknown_column_is_blocked():
    sql = """
    SELECT
        password
    FROM analytics.dim_customer;
    """

    with pytest.raises(SQLValidationError):
        validate_sql(sql)