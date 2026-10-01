class LLMClient:
    """Provider-independent interface for the LLM."""

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the LLM.

        Actual provider integration will be added later.
        """
        raise NotImplementedError(
            "LLM provider integration is not configured yet."
        )


class MockLLMClient(LLMClient):
    """Mock LLM used for local development and testing."""

    def generate(self, prompt: str) -> str:
        """Return a fixed SQL response for pipeline testing."""
        return (
            "SELECT "
            "COUNT(DISTINCT order_id) AS order_count "
            "FROM analytics.fact_orders;"
        )


if __name__ == "__main__":
    client = MockLLMClient()

    response = client.generate(
        "How many orders are there?"
    )

    print("Mock LLM response:")
    print(response)