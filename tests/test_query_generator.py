from core.query_generator import QueryGenerator


def test_query_generator_returns_sql():
    generator = QueryGenerator()

    sql = generator.generate_sql(
        "How many orders are there?"
    )

    assert isinstance(sql, str)
    assert sql.strip() != ""


def test_query_generator_returns_select_statement():
    generator = QueryGenerator()

    sql = generator.generate_sql(
        "How many orders are there?"
    )

    assert sql.strip().upper().startswith("SELECT")


def test_query_generator_uses_analytics_schema():
    generator = QueryGenerator()

    sql = generator.generate_sql(
        "How many orders are there?"
    )

    assert "analytics." in sql