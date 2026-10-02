from collections.abc import Callable
from typing import Any


DEFAULT_MAX_RETRIES = 2


class QueryRetryError(RuntimeError):
    """Raised when query generation cannot succeed within retry limits."""


class QueryRetryController:
    """Control bounded retries for query generation and execution."""

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ):
        if not isinstance(max_retries, int) or isinstance(
            max_retries, bool
        ):
            raise TypeError("max_retries must be an integer.")

        if max_retries < 0:
            raise ValueError(
                "max_retries cannot be negative."
            )

        self.max_retries = max_retries

    def run(
        self,
        operation: Callable[[], Any],
    ) -> Any:
        """
        Execute an operation with a bounded number of retries.

        max_retries=2 means at most 3 total attempts.
        """
        if not callable(operation):
            raise TypeError("operation must be callable.")

        last_error: Exception | None = None

        for _ in range(self.max_retries + 1):
            try:
                return operation()
            except Exception as exc:
                last_error = exc

        error_message = (
            f"Operation failed after "
            f"{self.max_retries + 1} attempts."
        )

        if last_error is not None:
            error_message += f" Last error: {last_error}"

        raise QueryRetryError(error_message) from last_error