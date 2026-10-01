import pytest

from core.llm_client import LLMClient, create_provider
from core.providers.mock import MockProvider


def test_create_provider_returns_mock_provider():
    provider = create_provider()

    assert isinstance(provider, MockProvider)


def test_llm_client_uses_configured_provider():
    client = LLMClient()

    assert isinstance(client.provider, MockProvider)


def test_llm_client_generates_sql():
    client = LLMClient()

    sql = client.generate(
        "How many orders are there?"
    )

    assert isinstance(sql, str)
    assert sql.strip().upper().startswith("SELECT")
    assert "analytics." in sql


def test_unsupported_provider_raises_error(monkeypatch):
    monkeypatch.setattr(
        "core.llm_client.get_llm_provider",
        lambda: "unsupported_provider",
    )

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        create_provider()