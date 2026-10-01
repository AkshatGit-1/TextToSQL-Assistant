import os

from dotenv import load_dotenv


load_dotenv()


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")


def get_llm_provider() -> str:
    """Return the configured LLM provider."""
    return LLM_PROVIDER