import pandas as pd

from app.visualization import (
    _find_chart_columns,
    _is_date_like_series,
    _is_numeric_series,
)


def test_numeric_series_is_detected():
    series = pd.Series([10, 20, 30])

    assert _is_numeric_series(series)


def test_non_numeric_series_is_not_numeric():
    series = pd.Series(["SP", "RJ", "MG"])

    assert not _is_numeric_series(series)


def test_date_series_is_detected():
    series = pd.Series(
        pd.to_datetime(
            ["2026-01-01", "2026-02-01", "2026-03-01"]
        )
    )

    assert _is_date_like_series(series)


def test_customer_state_and_sales_columns_are_detected():
    dataframe = pd.DataFrame(
        {
            "customer_state": ["SP", "RJ", "MG"],
            "total_sales": [1000.0, 800.0, 600.0],
        }
    )

    dimension, value = _find_chart_columns(dataframe)

    assert dimension == "customer_state"
    assert value == "total_sales"


def test_date_and_value_columns_are_detected():
    dataframe = pd.DataFrame(
        {
            "order_month": pd.to_datetime(
                [
                    "2026-01-01",
                    "2026-02-01",
                    "2026-03-01",
                ]
            ),
            "order_count": [100, 150, 200],
        }
    )

    dimension, value = _find_chart_columns(dataframe)

    assert dimension == "order_month"
    assert value == "order_count"


def test_single_column_result_has_no_chart():
    dataframe = pd.DataFrame(
        {
            "total_sales": [1000000.0],
        }
    )

    dimension, value = _find_chart_columns(dataframe)

    assert dimension is None
    assert value is None