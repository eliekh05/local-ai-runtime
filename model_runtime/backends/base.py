"""
Abstract base for all inference backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Generator


class BackendError(Exception):
    """Raised when a backend fails during inference."""
    pass


@dataclass
class GenerationResult:
    """Unified result from any backend."""
    text: str
    tokens_prompt: int = 0
    tokens_gen: int = 0
    finish_reason: str = "stop"
    elapsed: float = 0.0
    ttft: float = 0.0
    backend: str = ""

    @property
    def total_tokens(self) -> int:
        return self.tokens_prompt + self.tokens_gen


class Backend(ABC):
    """Interface every inference backend must implement."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Backend identifier (e.g. 'llama-cpp', 'openai')."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Can this backend serve requests right now?"""
        ...

    @abstractmethod
    def load_model(self, model_config: dict) -> None:
        """Load/initialize the model for this backend."""
        ...

    @abstractmethod
    def unload_model(self) -> None:
        """Unload model and free resources."""
        ...

    @abstractmethod
    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        """Generate a complete response from messages."""
        ...

    @abstractmethod
    def generate_stream(self, messages: list[dict], params: dict | None = None) -> Generator[str, None, None]:
        """Generate tokens one by one for SSE streaming."""
        ...

    def health_check(self) -> dict:
        """Return backend health info."""
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": False,
        }
