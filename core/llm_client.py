from config.llm_config import get_llm_provider
from core.providers.base import LLMProvider
from core.providers.mock import MockProvider


def create_provider() -> LLMProvider:
    """Create the configured LLM provider."""
    provider_name = get_llm_provider().lower()

    if provider_name == "mock":
        return MockProvider()

    raise ValueError(
        f"Unsupported LLM provider: {provider_name}"
    )


class LLMClient:
    """Client that delegates generation to the configured provider."""

    def __init__(self, provider: LLMProvider | None = None):
        self.provider = provider or create_provider()

    def generate(self, prompt: str) -> str:
        """Generate a response using the configured provider."""
        return self.provider.generate(prompt)


if __name__ == "__main__":
    client = LLMClient()

    response = client.generate(
        "How many orders are there?"
    )

    print("LLM Client response:")
    print(response)