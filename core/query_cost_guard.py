from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Connection


DEFAULT_MAX_QUERY_COST = 100000.0


class QueryCostError(RuntimeError):
    """Raised when a query exceeds the allowed PostgreSQL cost."""


class QueryCostGuard:
    """Check PostgreSQL estimated query cost before execution."""

    def __init__(
        self,
        max_query_cost: float = DEFAULT_MAX_QUERY_COST,
    ):
        if not isinstance(max_query_cost, (int, float)) or isinstance(
            max_query_cost, bool
        ):
            raise TypeError("max_query_cost must be a number.")

        if max_query_cost <= 0:
            raise ValueError(
                "max_query_cost must be greater than zero."
            )

        self.max_query_cost = float(max_query_cost)

    def check(
        self,
        connection: Connection,
        sql: str,
    ) -> float:
        """Return estimated total cost or raise QueryCostError."""
        explain_sql = f"EXPLAIN (FORMAT JSON, COSTS TRUE) {sql}"

        result = connection.execute(text(explain_sql))
        row = result.fetchone()

        if row is None:
            raise QueryCostError(
                "PostgreSQL returned no EXPLAIN plan."
            )

        plan_data: Any = row[0]

        if isinstance(plan_data, str):
            import json

            plan_data = json.loads(plan_data)

        if not isinstance(plan_data, list) or not plan_data:
            raise QueryCostError(
                "Invalid EXPLAIN plan returned by PostgreSQL."
            )

        plan = plan_data[0].get("Plan")

        if not isinstance(plan, dict):
            raise QueryCostError(
                "EXPLAIN plan does not contain a valid Plan."
            )

        total_cost = plan.get("Total Cost")

        if not isinstance(total_cost, (int, float)):
            raise QueryCostError(
                "EXPLAIN plan does not contain Total Cost."
            )

        total_cost = float(total_cost)

        if total_cost > self.max_query_cost:
            raise QueryCostError(
                f"Query cost {total_cost:.2f} exceeds the "
                f"maximum allowed cost "
                f"{self.max_query_cost:.2f}."
            )

        return total_cost