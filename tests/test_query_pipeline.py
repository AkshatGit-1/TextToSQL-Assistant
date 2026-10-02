import pytest

from core.query_pipeline import QueryPipeline
from core.query_retry import QueryRetryController


class FakeQueryGenerator:
    def __init__(self):
        self.feedback_history = []

    def generate_sql(
        self,
        question,
        error_feedback=None,
        conversation_context=None,
    ):
        self.feedback_history.append(error_feedback)

        return """
        SELECT
            COUNT(DISTINCT order_id) AS order_count
        FROM analytics.fact_orders;
        """


class FakeQueryExecutor:
    def execute(self, sql):
        return [
            {"order_count": 99441},
        ]


def test_query_pipeline_runs_end_to_end():
    pipeline = QueryPipeline(
        query_generator=FakeQueryGenerator(),
        query_executor=FakeQueryExecutor(),
    )

    result = pipeline.run("How many orders are there?")

    assert result["question"] == "How many orders are there?"
    assert "SELECT" in result["sql"]
    assert result["results"] == [{"order_count": 99441}]
    assert result["attempts"] == 1


def test_query_pipeline_strips_question():
    pipeline = QueryPipeline(
        query_generator=FakeQueryGenerator(),
        query_executor=FakeQueryExecutor(),
    )

    result = pipeline.run("  How many orders are there?  ")

    assert result["question"] == "How many orders are there?"


def test_query_pipeline_rejects_empty_question():
    pipeline = QueryPipeline(
        query_generator=FakeQueryGenerator(),
        query_executor=FakeQueryExecutor(),
    )

    with pytest.raises(ValueError, match="Question cannot be empty"):
        pipeline.run("")


def test_query_pipeline_rejects_non_string_question():
    pipeline = QueryPipeline(
        query_generator=FakeQueryGenerator(),
        query_executor=FakeQueryExecutor(),
    )

    with pytest.raises(TypeError, match="Question must be a string"):
        pipeline.run(None)


def test_query_pipeline_passes_generated_sql_to_executor():
    class TrackingGenerator:
        def generate_sql(
            self,
            question,
            error_feedback=None,
            conversation_context=None,
        ):
            return """
            SELECT
                COUNT(*) AS item_count
            FROM analytics.fact_order_items;
            """

    class TrackingExecutor:
        def __init__(self):
            self.received_sql = None

        def execute(self, sql):
            self.received_sql = sql
            return [{"item_count": 112650}]

    executor = TrackingExecutor()

    pipeline = QueryPipeline(
        query_generator=TrackingGenerator(),
        query_executor=executor,
    )

    result = pipeline.run(
        "How many order items are there?"
    )

    assert executor.received_sql == result["sql"]
    assert result["results"] == [{"item_count": 112650}]


def test_query_pipeline_retries_after_execution_failure():
    class RetryGenerator:
        def __init__(self):
            self.feedback_history = []

        def generate_sql(
            self,
            question,
            error_feedback=None,
            conversation_context=None,
        ):
            self.feedback_history.append(error_feedback)

            return f"""
            SELECT
                COUNT(DISTINCT order_id) AS order_count
            FROM analytics.fact_orders;
            """

    class RetryExecutor:
        def __init__(self):
            self.attempts = 0

        def execute(self, sql):
            self.attempts += 1

            if self.attempts == 1:
                raise RuntimeError(
                    "Query cost exceeded."
                )

            return [{"order_count": 99441}]

    generator = RetryGenerator()
    executor = RetryExecutor()

    pipeline = QueryPipeline(
        query_generator=generator,
        query_executor=executor,
        retry_controller=QueryRetryController(
            max_retries=2,
        ),
    )

    result = pipeline.run(
        "How many orders are there?"
    )

    assert result["results"] == [
        {"order_count": 99441}
    ]
    assert result["attempts"] == 2
    assert generator.feedback_history[0] is None
    assert (
        generator.feedback_history[1]
        == "Query cost exceeded."
    )


def test_query_pipeline_fails_after_retry_limit():
    class FailingGenerator:
        def generate_sql(
            self,
            question,
            error_feedback=None,
            conversation_context=None,
        ):
            return """
            SELECT
                COUNT(DISTINCT order_id) AS order_count
            FROM analytics.fact_orders;
            """

    class FailingExecutor:
        def __init__(self):
            self.attempts = 0

        def execute(self, sql):
            self.attempts += 1
            raise RuntimeError("Execution failed.")

    executor = FailingExecutor()

    pipeline = QueryPipeline(
        query_generator=FailingGenerator(),
        query_executor=executor,
        retry_controller=QueryRetryController(
            max_retries=2,
        ),
    )

    with pytest.raises(
        RuntimeError,
        match="Execution failed",
    ):
        pipeline.run(
            "How many orders are there?"
        )

    assert executor.attempts == 3