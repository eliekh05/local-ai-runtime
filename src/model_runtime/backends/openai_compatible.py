"""
OpenAI-compatible backend — works with any OpenAI API-compatible server.
Examples: LiteLLM, LM Studio, vLLM (OpenAI mode), text-generation-webui, etc.
"""

import os
import time
from typing import Generator

from model_runtime.backends.base import Backend, GenerationResult, BackendError


class OpenAICompatibleBackend(Backend):
    """Any OpenAI-compatible API endpoint (BYOK)."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._client = None
        self._model = self._config.get("model", "")

    @property
    def name(self) -> str:
        return "openai_compatible"

    def is_available(self) -> bool:
        return True  # Always available — user provides base_url at config time

    def load_model(self, model_config: dict) -> None:
        base_url = self._config.get("base_url", "")
        if not base_url:
            raise BackendError("No base_url specified for openai_compatible backend.")

        try:
            from openai import OpenAI
        except ImportError:
            raise BackendError("openai package not installed. Run: uv pip install openai")

        api_key_env = self._config.get("api_key_env", "")
        api_key = os.environ.get(api_key_env, "sk-no-key-required") if api_key_env else "sk-no-key-required"

        self._client = OpenAI(api_key=api_key, base_url=base_url)
        self._model = model_config.get("compatible_model", self._config.get("model", ""))

        if not self._model:
            # Try to list models and pick the first one
            try:
                models = self._client.models.list()
                if models.data:
                    self._model = models.data[0].id
            except Exception:
                raise BackendError("No model specified and couldn't auto-detect from server.")

    def unload_model(self) -> None:
        self._client = None

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._client:
            raise BackendError("Client not initialized.")

        params = params or {}
        start = time.time()

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 0.9),
                max_tokens=params.get("max_new_tokens", 512),
            )
        except Exception as e:
            raise BackendError(f"API error: {e}")

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
            raise BackendError("Client not initialized.")

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
            raise BackendError(f"Stream error: {e}")

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": self._client is not None,
            "model": self._model,
            "base_url": self._config.get("base_url", ""),
        }
