from config.llm_config import get_llm_provider


def test_default_llm_provider():
    provider = get_llm_provider()

    assert provider == "mock"


def test_llm_provider_is_string():
    provider = get_llm_provider()

    assert isinstance(provider, str)
    assert provider.strip() != ""