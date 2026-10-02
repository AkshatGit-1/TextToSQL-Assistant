from typing import Any

from sqlglot import exp, parse_one
from sqlalchemy import text
from sqlalchemy.engine import Engine

from core.db_connection import get_engine
from core.query_cost_guard import (
    DEFAULT_MAX_QUERY_COST,
    QueryCostGuard,
    QueryCostError,
)
from core.sql_validator import validate_sql


DEFAULT_MAX_ROWS = 1000
DEFAULT_STATEMENT_TIMEOUT_MS = 10000


class QueryExecutionError(RuntimeError):
    """Raised when a validated SQL query cannot be executed."""


def _apply_row_limit(sql: str, max_rows: int) -> str:
    """Add or tighten a server-side LIMIT."""
    expression = parse_one(sql, read="postgres")

    if not isinstance(expression, exp.Select):
        raise QueryExecutionError(
            "Only SELECT queries can be executed."
        )

    existing_limit = expression.args.get("limit")

    if existing_limit is None:
        expression = expression.limit(max_rows)
    else:
        limit_expression = existing_limit.expression

        if isinstance(limit_expression, exp.Literal):
            try:
                existing_value = int(limit_expression.this)
            except (TypeError, ValueError):
                raise QueryExecutionError(
                    "Only numeric LIMIT values are supported."
                )

            if existing_value > max_rows:
                expression = expression.limit(max_rows)

    return expression.sql(dialect="postgres")


class QueryExecutor:
    """Execute validated read-only SQL queries safely."""

    def __init__(
        self,
        engine: Engine | None = None,
        max_rows: int = DEFAULT_MAX_ROWS,
        statement_timeout_ms: int = DEFAULT_STATEMENT_TIMEOUT_MS,
        max_query_cost: float = DEFAULT_MAX_QUERY_COST,
    ):
        if not isinstance(max_rows, int) or isinstance(max_rows, bool):
            raise TypeError("max_rows must be an integer.")

        if max_rows <= 0:
            raise ValueError("max_rows must be greater than zero.")

        if not isinstance(statement_timeout_ms, int) or isinstance(
            statement_timeout_ms, bool
        ):
            raise TypeError("statement_timeout_ms must be an integer.")

        if statement_timeout_ms <= 0:
            raise ValueError(
                "statement_timeout_ms must be greater than zero."
            )

        self.engine = engine or get_engine()
        self.max_rows = max_rows
        self.statement_timeout_ms = statement_timeout_ms
        self.cost_guard = QueryCostGuard(
            max_query_cost=max_query_cost,
        )

    def execute(self, sql: str) -> list[dict[str, Any]]:
        """
        Validate, cost-check, and execute a SQL query.

        The database receives a server-side LIMIT and statement
        timeout before results are returned.
        """
        validated_sql = validate_sql(sql)

        limited_sql = _apply_row_limit(
            validated_sql,
            self.max_rows,
        )

        try:
            with self.engine.connect() as connection:
                connection.execute(
                    text(
                        f"SET LOCAL statement_timeout = "
                        f"{self.statement_timeout_ms}"
                    )
                )

                self.cost_guard.check(
                    connection,
                    limited_sql,
                )

                result = connection.execute(
                    text(limited_sql)
                )

                rows = result.mappings().fetchmany(
                    self.max_rows
                )

                return [dict(row) for row in rows]

        except QueryCostError as exc:
            raise QueryExecutionError(
                f"Query rejected by cost guard: {exc}"
            ) from exc

        except QueryExecutionError:
            raise

        except Exception as exc:
            raise QueryExecutionError(
                f"Query execution failed: {exc}"
            ) from exc


if __name__ == "__main__":
    executor = QueryExecutor()

    sql = """
    SELECT
        COUNT(DISTINCT order_id) AS order_count
    FROM analytics.fact_orders;
    """

    results = executor.execute(sql)

    print("Query results:")
    for row in results:
        print(row)