from core.providers.mock import MockProvider


def test_mock_provider_returns_sql():
    provider = MockProvider()

    sql = provider.generate(
        "How many orders are there?"
    )

    assert isinstance(sql, str)
    assert sql.strip() != ""


def test_mock_provider_returns_select():
    provider = MockProvider()

    sql = provider.generate(
        "How many orders are there?"
    )

    assert sql.strip().upper().startswith("SELECT")


def test_mock_provider_uses_analytics_schema():
    provider = MockProvider()

    sql = provider.generate(
        "How many orders are there?"
    )

    assert "analytics." in sql