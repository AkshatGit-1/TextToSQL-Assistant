import json

import pytest

from core.query_cost_guard import (
    QueryCostError,
    QueryCostGuard,
)


class FakeResult:
    def __init__(self, plan):
        self.plan = plan

    def fetchone(self):
        return (json.dumps(self.plan),)


class FakeConnection:
    def __init__(self, plan):
        self.plan = plan
        self.executed_sql = None

    def execute(self, query):
        self.executed_sql = str(query)
        return FakeResult(self.plan)


def make_plan(total_cost):
    return [
        {
            "Plan": {
                "Node Type": "Seq Scan",
                "Relation Name": "fact_orders",
                "Total Cost": total_cost,
            }
        }
    ]


def test_query_cost_under_limit_is_allowed():
    connection = FakeConnection(
        make_plan(500.0)
    )

    guard = QueryCostGuard(
        max_query_cost=1000.0
    )

    cost = guard.check(
        connection,
        """
        SELECT *
        FROM analytics.fact_orders;
        """,
    )

    assert cost == 500.0
    assert "EXPLAIN" in connection.executed_sql.upper()


def test_query_cost_over_limit_is_rejected():
    connection = FakeConnection(
        make_plan(5000.0)
    )

    guard = QueryCostGuard(
        max_query_cost=1000.0
    )

    with pytest.raises(
        QueryCostError,
        match="exceeds the maximum allowed cost",
    ):
        guard.check(
            connection,
            """
            SELECT *
            FROM analytics.fact_orders;
            """,
        )


def test_query_cost_equal_to_limit_is_allowed():
    connection = FakeConnection(
        make_plan(1000.0)
    )

    guard = QueryCostGuard(
        max_query_cost=1000.0
    )

    cost = guard.check(
        connection,
        """
        SELECT *
        FROM analytics.fact_orders;
        """,
    )

    assert cost == 1000.0


def test_invalid_max_query_cost_is_rejected():
    with pytest.raises(ValueError):
        QueryCostGuard(max_query_cost=0)


def test_non_numeric_max_query_cost_is_rejected():
    with pytest.raises(TypeError):
        QueryCostGuard(max_query_cost="1000")


def test_missing_explain_plan_is_rejected():
    class EmptyResult:
        def fetchone(self):
            return None

    class EmptyConnection:
        def execute(self, query):
            return EmptyResult()

    guard = QueryCostGuard()

    with pytest.raises(
        QueryCostError,
        match="no EXPLAIN plan",
    ):
        guard.check(
            EmptyConnection(),
            """
            SELECT COUNT(*)
            FROM analytics.fact_orders;
            """,
        )


def test_invalid_explain_plan_is_rejected():
    connection = FakeConnection(
        {"invalid": "plan"}
    )

    guard = QueryCostGuard()

    with pytest.raises(
        QueryCostError,
        match="Invalid EXPLAIN plan",
    ):
        guard.check(
            connection,
            """
            SELECT COUNT(*)
            FROM analytics.fact_orders;
            """,
        )