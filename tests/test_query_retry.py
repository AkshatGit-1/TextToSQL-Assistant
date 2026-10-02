import pytest

from core.query_retry import (
    QueryRetryController,
    QueryRetryError,
)


def test_retry_controller_returns_successful_result():
    controller = QueryRetryController(
        max_retries=2,
    )

    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1
        return "success"

    result = controller.run(operation)

    assert result == "success"
    assert attempts == 1


def test_retry_controller_retries_failed_operation():
    controller = QueryRetryController(
        max_retries=2,
    )

    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1

        if attempts < 3:
            raise ValueError("temporary failure")

        return "success"

    result = controller.run(operation)

    assert result == "success"
    assert attempts == 3


def test_retry_controller_stops_after_max_retries():
    controller = QueryRetryController(
        max_retries=2,
    )

    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1
        raise ValueError("permanent failure")

    with pytest.raises(
        QueryRetryError,
        match="failed after 3 attempts",
    ):
        controller.run(operation)

    assert attempts == 3


def test_zero_retries_means_one_attempt():
    controller = QueryRetryController(
        max_retries=0,
    )

    attempts = 0

    def operation():
        nonlocal attempts
        attempts += 1
        raise ValueError("failure")

    with pytest.raises(QueryRetryError):
        controller.run(operation)

    assert attempts == 1


def test_negative_retries_are_rejected():
    with pytest.raises(ValueError):
        QueryRetryController(
            max_retries=-1,
        )


def test_non_integer_retries_are_rejected():
    with pytest.raises(TypeError):
        QueryRetryController(
            max_retries="2",
        )


def test_non_callable_operation_is_rejected():
    controller = QueryRetryController()

    with pytest.raises(TypeError):
        controller.run("not callable")