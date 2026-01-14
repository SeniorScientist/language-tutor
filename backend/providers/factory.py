"""LLM Provider Factory."""

import logging
from functools import lru_cache

from .base import BaseLLMProvider
from .groq_provider import GroqProvider
from .local_provider import LocalProvider
from config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM provider instances.

    Uses the factory pattern to instantiate the correct provider
    based on the LLM_PROVIDER environment variable.
    """

    _providers = {
        "groq": GroqProvider,
        "local": LocalProvider,
    }

    @classmethod
    def create(cls, settings: Settings) -> BaseLLMProvider:
        """Create an LLM provider instance.

        Args:
            settings: Application settings.

        Returns:
            Configured LLM provider instance.

        Raises:
            ValueError: If provider type is not supported.
        """
        provider_type = settings.llm_provider.lower()

        if provider_type not in cls._providers:
            raise ValueError(
                f"Unknown LLM provider: {provider_type}. "
                f"Supported providers: {list(cls._providers.keys())}"
            )

        provider_class = cls._providers[provider_type]
        logger.info(f"Creating LLM provider: {provider_type}")

        return provider_class(settings)

    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a new provider type.

        Args:
            name: Provider name identifier.
            provider_class: Provider class implementing BaseLLMProvider.
        """
        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered new provider: {name}")


# Cached provider instance
_provider_instance: BaseLLMProvider | None = None


def get_llm_provider() -> BaseLLMProvider:
    """Get the configured LLM provider instance.

    Uses a cached singleton pattern to avoid recreating the provider.

    Returns:
        The configured LLM provider instance.
    """
    global _provider_instance

    if _provider_instance is None:
        settings = get_settings()
        _provider_instance = LLMProviderFactory.create(settings)

    return _provider_instance


def reset_provider():
    """Reset the cached provider instance.

    Useful for testing or when settings change.
    """
    global _provider_instance
    _provider_instance = None
