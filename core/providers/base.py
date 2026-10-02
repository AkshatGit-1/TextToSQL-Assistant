from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the LLM."""
        raise NotImplementedError

    @staticmethod
    def validate_prompt(prompt: str) -> None:
        """Validate the prompt before sending it to a provider."""
        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")