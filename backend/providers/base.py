"""Abstract base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers.

    All LLM providers (Groq, local, etc.) must implement this interface.
    """

    @abstractmethod
    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> str:
        """Generate a completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.
            json_mode: If True, request JSON output format.

        Returns:
            Generated text response.
        """
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Generate a streaming completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            temperature: Sampling temperature (0-2).
            max_tokens: Maximum tokens to generate.

        Yields:
            Generated text chunks.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and can respond.

        Returns:
            True if healthy, False otherwise.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass
