"""
OpenAI API backend — GPT-4o, GPT-4o-mini, etc.
"""

import os
import time
from typing import Generator

from model_runtime.backends.base import Backend, GenerationResult, BackendError


class OpenAIBackend(Backend):
    """OpenAI API backend (BYOK)."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._client = None
        self._model = self._config.get("model", "gpt-4o-mini")

    @property
    def name(self) -> str:
        return "openai"

    def is_available(self) -> bool:
        try:
            import openai  # noqa: F401
            return True
        except ImportError:
            return False

    def load_model(self, model_config: dict) -> None:
        if not self.is_available():
            api_key_env = self._config.get("api_key_env", "OPENAI_API_KEY")
            raise BackendError(f"OpenAI API key not found. Set {api_key_env} environment variable.")

        try:
            from openai import OpenAI
        except ImportError:
            raise BackendError("openai package not installed. Run: uv pip install openai")

        api_key_env = self._config.get("api_key_env", "OPENAI_API_KEY")
        base_url = self._config.get("base_url", "https://api.openai.com/v1")

        self._client = OpenAI(
            api_key=os.environ.get(api_key_env),
            base_url=base_url,
        )
        self._model = model_config.get("openai_model", self._config.get("model", "gpt-4o-mini"))

    def unload_model(self) -> None:
        self._client = None

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._client:
            raise BackendError("OpenAI client not initialized. Call load_model() first.")

        params = params or {}
        start = time.time()

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 0.9),
                max_tokens=params.get("max_new_tokens", 512),
                seed=params.get("seed", None) if params.get("seed", -1) >= 0 else None,
            )
        except Exception as e:
            raise BackendError(f"OpenAI API error: {e}")

        elapsed = time.time() - start
        choice = response.choices[0]
        usage = response.usage

        return GenerationResult(
            text=choice.message.content or "",
            tokens_prompt=usage.prompt_tokens if usage else 0,
            tokens_gen=usage.completion_tokens if usage else 0,
            finish_reason=choice.finish_reason or "stop",
            elapsed=elapsed,
            backend=self.name,
        )

    def generate_stream(self, messages: list[dict], params: dict | None = None) -> Generator[str, None, None]:
        if not self._client:
            raise BackendError("OpenAI client not initialized. Call load_model() first.")

        params = params or {}

        try:
            stream = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 0.9),
                max_tokens=params.get("max_new_tokens", 512),
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield delta.content
        except Exception as e:
            raise BackendError(f"OpenAI stream error: {e}")

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": self._client is not None,
            "model": self._model,
        }
