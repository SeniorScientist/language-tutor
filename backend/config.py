"""Application configuration."""

import json
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Literal, Union
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider settings
    llm_provider: Literal["groq", "local"] = "groq"

    # Groq settings
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    groq_base_url: str = "https://api.groq.com/openai/v1"

    # Local LLM settings
    local_model_path: str = "./models/model.gguf"
    gpu_layers: int = -1  # -1 = use all available GPU layers
    context_length: int = 8192  # Qwen2.5 supports up to 128K

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"

    # ChromaDB settings
    chroma_persist_directory: str = "./chroma_db"

    # App settings
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Union[str, list]) -> list[str]:
        """Parse CORS origins from JSON string or list."""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                # If it's a comma-separated string
                return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
