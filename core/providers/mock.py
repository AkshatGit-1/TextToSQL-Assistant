from core.providers.base import LLMProvider


class MockProvider(LLMProvider):
    """Mock provider for local development and testing."""

    def generate(self, prompt: str) -> str:
        """Return a fixed SQL response for pipeline testing."""
        return (
            "SELECT "
            "COUNT(DISTINCT order_id) AS order_count "
            "FROM analytics.fact_orders;"
        )