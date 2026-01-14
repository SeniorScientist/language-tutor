"""Groq API provider implementation."""

import logging
from typing import AsyncIterator
from openai import AsyncOpenAI

from .base import BaseLLMProvider
from config import Settings

logger = logging.getLogger(__name__)


class GroqProvider(BaseLLMProvider):
    """LLM provider using Groq API (OpenAI-compatible).

    Groq provides fast inference for open-source models via their API.
    Uses the OpenAI Python SDK for compatibility.
    """

    def __init__(self, settings: Settings):
        """Initialize the Groq provider.

        Args:
            settings: Application settings containing Groq configuration.
        """
        self.settings = settings
        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url=settings.groq_base_url,
        )
        self.model = settings.groq_model
        logger.info(f"Initialized Groq provider with model: {self.model}")

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> str:
        """Generate a completion using Groq API.

        Args:
            messages: List of message dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            json_mode: If True, request JSON output format.

        Returns:
            Generated text response.
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }

            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}

            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            raise

    async def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Generate a streaming completion using Groq API.

        Args:
            messages: List of message dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Yields:
            Generated text chunks.
        """
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Groq streaming error: {e}")
            raise

    async def health_check(self) -> bool:
        """Check if Groq API is accessible.

        Returns:
            True if healthy, False otherwise.
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5,
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Groq health check failed: {e}")
            return False

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "groq"
