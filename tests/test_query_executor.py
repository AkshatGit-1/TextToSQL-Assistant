import pytest

from core.query_executor import QueryExecutionError, QueryExecutor


class FakeResult:
    def mappings(self):
        return self

    def fetchmany(self, size):
        return [
            {"order_count": 99441},
        ][:size]

    def fetchone(self):
        return (
            '[{"Plan": {"Node Type": "Aggregate", "Total Cost": 10.0}}]',
        )


class FakeConnection:
    def __init__(self):
        self.executed_queries = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query):
        self.executed_queries.append(str(query))
        return FakeResult()


class FakeEngine:
    def __init__(self):
        self.connection = FakeConnection()

    def connect(self):
        return self.connection


def test_query_executor_returns_results():
    engine = FakeEngine()

    executor = QueryExecutor(engine=engine)

    results = executor.execute(
        """
        SELECT
            COUNT(DISTINCT order_id) AS order_count
        FROM analytics.fact_orders;
        """
    )

    assert results == [{"order_count": 99441}]


def test_query_executor_adds_server_side_limit():
    engine = FakeEngine()

    executor = QueryExecutor(
        engine=engine,
        max_rows=100,
    )

    executor.execute(
        """
        SELECT
            customer_key
        FROM analytics.dim_customer;
        """
    )

    executed_sql = engine.connection.executed_queries[-1]

    assert "LIMIT 100" in executed_sql.upper()


def test_query_executor_tightens_large_existing_limit():
    engine = FakeEngine()

    executor = QueryExecutor(
        engine=engine,
        max_rows=100,
    )

    executor.execute(
        """
        SELECT
            customer_key
        FROM analytics.dim_customer
        LIMIT 5000;
        """
    )

    executed_sql = engine.connection.executed_queries[-1]

    assert "LIMIT 100" in executed_sql.upper()
    assert "LIMIT 5000" not in executed_sql.upper()


def test_query_executor_preserves_smaller_existing_limit():
    engine = FakeEngine()

    executor = QueryExecutor(
        engine=engine,
        max_rows=100,
    )

    executor.execute(
        """
        SELECT
            customer_key
        FROM analytics.dim_customer
        LIMIT 25;
        """
    )

    executed_sql = engine.connection.executed_queries[-1]

    assert "LIMIT 25" in executed_sql.upper()


def test_query_executor_runs_cost_check_before_query():
    engine = FakeEngine()

    executor = QueryExecutor(
        engine=engine,
        max_rows=100,
    )

    executor.execute(
        """
        SELECT
            COUNT(*)
        FROM analytics.fact_orders;
        """
    )

    queries = engine.connection.executed_queries

    assert len(queries) == 3
    assert "SET LOCAL" in queries[0].upper()
    assert "EXPLAIN" in queries[1].upper()
    assert "SELECT" in queries[2].upper()


def test_query_executor_respects_max_rows():
    class MultipleRowsResult:
        def mappings(self):
            return self

        def fetchmany(self, size):
            return [
                {"id": 1},
                {"id": 2},
                {"id": 3},
            ][:size]

        def fetchone(self):
            return (
                '[{"Plan": {"Node Type": "Seq Scan", '
                '"Total Cost": 10.0}}]',
            )

    class MultipleRowsConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, query):
            return MultipleRowsResult()

    class MultipleRowsEngine:
        def connect(self):
            return MultipleRowsConnection()

    executor = QueryExecutor(
        engine=MultipleRowsEngine(),
        max_rows=2,
    )

    results = executor.execute(
        """
        SELECT
            customer_key
        FROM analytics.dim_customer;
        """
    )

    assert results == [
        {"id": 1},
        {"id": 2},
    ]


def test_query_executor_validates_sql_before_execution():
    executor = QueryExecutor(engine=FakeEngine())

    with pytest.raises(ValueError):
        executor.execute(
            """
            DELETE FROM analytics.fact_orders;
            """
        )


class FailingConnection:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query):
        raise RuntimeError("database connection failed")


class FailingEngine:
    def connect(self):
        return FailingConnection()


def test_query_executor_wraps_execution_errors():
    executor = QueryExecutor(engine=FailingEngine())

    with pytest.raises(
        QueryExecutionError,
        match="Query execution failed",
    ):
        executor.execute(
            """
            SELECT COUNT(*)
            FROM analytics.fact_orders;
            """
        )


def test_invalid_max_rows_is_rejected():
    with pytest.raises(ValueError):
        QueryExecutor(
            engine=FakeEngine(),
            max_rows=0,
        )


def test_invalid_statement_timeout_is_rejected():
    with pytest.raises(ValueError):
        QueryExecutor(
            engine=FakeEngine(),
            statement_timeout_ms=0,
        )


def test_invalid_query_cost_is_rejected():
    with pytest.raises(ValueError):
        QueryExecutor(
            engine=FakeEngine(),
            max_query_cost=0,
        )