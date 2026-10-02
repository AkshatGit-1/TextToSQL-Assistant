from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd
import streamlit as st


def _is_numeric_series(series: pd.Series) -> bool:
    """Return True when a series contains numeric values."""
    if pd.api.types.is_numeric_dtype(series):
        return True

    sample = series.dropna()

    if sample.empty:
        return False

    return all(
        isinstance(value, (int, float, Decimal))
        and not isinstance(value, bool)
        for value in sample
    )


def _is_date_like_series(series: pd.Series) -> bool:
    """Return True when a series represents dates or timestamps."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    if series.empty:
        return False

    sample = series.dropna()

    if sample.empty:
        return False

    if all(
        isinstance(value, (date, datetime, pd.Timestamp))
        for value in sample
    ):
        return True

    return False


def _find_chart_columns(
    dataframe: pd.DataFrame,
) -> tuple[str | None, str | None]:
    """Find the dimension and numeric value columns."""
    if dataframe.shape[1] < 2:
        return None, None

    columns = list(dataframe.columns)

    numeric_columns = [
        column
        for column in columns
        if _is_numeric_series(dataframe[column])
    ]

    if not numeric_columns:
        return None, None

    value_column = numeric_columns[0]

    date_columns = [
        column
        for column in columns
        if column != value_column
        and _is_date_like_series(dataframe[column])
    ]

    if date_columns:
        return date_columns[0], value_column

    dimension_columns = [
        column
        for column in columns
        if column != value_column
    ]

    if dimension_columns:
        return dimension_columns[0], value_column

    return None, None


def render_visualization(results: list[dict[str, Any]]) -> None:
    """Render a chart when the query result supports visualization."""
    if not results:
        return

    dataframe = pd.DataFrame(results)

    if dataframe.empty or dataframe.shape[1] < 2:
        return

    dimension_column, value_column = _find_chart_columns(dataframe)

    if dimension_column is None or value_column is None:
        return

    chart_data = dataframe[
        [dimension_column, value_column]
    ].copy()

    chart_data[value_column] = pd.to_numeric(
        chart_data[value_column],
        errors="coerce",
    )

    chart_data = chart_data.dropna(
        subset=[dimension_column, value_column]
    )

    if chart_data.empty:
        return

    is_time_series = _is_date_like_series(
        chart_data[dimension_column]
    )

    st.subheader("Visualization")

    if is_time_series:
        chart_data[dimension_column] = pd.to_datetime(
            chart_data[dimension_column],
            errors="coerce",
        )

        chart_data = chart_data.dropna(
            subset=[dimension_column]
        )

        chart_data = chart_data.sort_values(
            dimension_column
        )

        st.line_chart(
            chart_data,
            x=dimension_column,
            y=value_column,
            use_container_width=True,
        )

        return

    chart_data = chart_data.sort_values(
        value_column,
        ascending=False,
    )

    st.bar_chart(
        chart_data,
        x=dimension_column,
        y=value_column,
        horizontal=True,
        use_container_width=True,
    )