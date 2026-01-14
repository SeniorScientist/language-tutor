"""Local LLM provider using llama-cpp-python."""

import logging
import asyncio
from typing import AsyncIterator, Optional
from pathlib import Path

from .base import BaseLLMProvider
from config import Settings

logger = logging.getLogger(__name__)


class LocalProvider(BaseLLMProvider):
    """LLM provider using local GGUF models via llama-cpp-python.

    This provider loads a GGUF model locally and runs inference.
    Designed for GPU-enabled deployments.
    """

    def __init__(self, settings: Settings):
        """Initialize the local LLM provider.

        Args:
            settings: Application settings containing model configuration.
        """
        self.settings = settings
        self.model_path = settings.local_model_path
        self.gpu_layers = settings.gpu_layers
        self.context_length = settings.context_length
        self._llm: Optional["Llama"] = None
        self._lock = asyncio.Lock()
        logger.info(f"Initialized Local provider (model will be loaded on first use)")

    def _load_model(self):
        """Load the GGUF model if not already loaded."""
        if self._llm is None:
            try:
                from llama_cpp import Llama

                model_path = Path(self.model_path)
                if not model_path.exists():
                    raise FileNotFoundError(f"Model not found: {model_path}")

                logger.info(f"Loading model from: {model_path}")
                self._llm = Llama(
                    model_path=str(model_path),
                    n_ctx=self.context_length,
                    n_gpu_layers=self.gpu_layers,
                    verbose=False,
                )
                logger.info("Model loaded successfully")

            except ImportError:
                logger.error("llama-cpp-python not installed")
                raise RuntimeError(
                    "llama-cpp-python is required for local LLM. "
                    "Install with: pip install llama-cpp-python"
                )
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise

    def _format_messages(self, messages: list[dict]) -> str:
        """Format messages into a prompt string.

        Args:
            messages: List of message dicts.

        Returns:
            Formatted prompt string.
        """
        # Use ChatML format
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"<|im_start|>system\n{content}<|im_end|>")
            elif role == "user":
                prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
            elif role == "assistant":
                prompt_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")

        prompt_parts.append("<|im_start|>assistant\n")
        return "\n".join(prompt_parts)

    async def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        json_mode: bool = False,
    ) -> str:
        """Generate a completion using local LLM.

        Args:
            messages: List of message dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.
            json_mode: If True, try to constrain output to JSON.

        Returns:
            Generated text response.
        """
        async with self._lock:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self._generate_sync,
                messages,
                temperature,
                max_tokens,
                json_mode,
            )

    def _generate_sync(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
        json_mode: bool,
    ) -> str:
        """Synchronous generation method."""
        self._load_model()

        prompt = self._format_messages(messages)

        # Add JSON instruction if needed
        if json_mode:
            prompt = prompt.rstrip() + " Output valid JSON:\n"

        response = self._llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=["<|im_end|>", "<|im_start|>"],
            echo=False,
        )

        return response["choices"][0]["text"].strip()

    async def generate_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """Generate a streaming completion using local LLM.

        Args:
            messages: List of message dicts.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens to generate.

        Yields:
            Generated text chunks.
        """
        # For local LLM, we simulate streaming by generating in chunks
        async with self._lock:
            loop = asyncio.get_event_loop()

            def generate_with_stream():
                self._load_model()
                prompt = self._format_messages(messages)

                return self._llm(
                    prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stop=["<|im_end|>", "<|im_start|>"],
                    echo=False,
                    stream=True,
                )

            stream = await loop.run_in_executor(None, generate_with_stream)

            for chunk in stream:
                text = chunk["choices"][0]["text"]
                if text:
                    yield text
                    await asyncio.sleep(0)  # Allow other tasks to run

    async def health_check(self) -> bool:
        """Check if local LLM is available.

        Returns:
            True if model exists and can be loaded, False otherwise.
        """
        try:
            model_path = Path(self.model_path)
            if not model_path.exists():
                logger.warning(f"Model file not found: {model_path}")
                return False

            # Try to load the model
            self._load_model()
            return self._llm is not None

        except Exception as e:
            logger.error(f"Local LLM health check failed: {e}")
            return False

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "local"
