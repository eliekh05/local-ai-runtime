"""
Anthropic API backend — Claude models.
"""

import os
import time
from typing import Generator

from model_runtime.backends.base import Backend, GenerationResult, BackendError


class AnthropicBackend(Backend):
    """Anthropic API backend (BYOK)."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._client = None
        self._model = self._config.get("model", "claude-sonnet-4-20250514")

    @property
    def name(self) -> str:
        return "anthropic"

    def is_available(self) -> bool:
        try:
            import anthropic  # noqa: F401
            return True
        except ImportError:
            return False

    def load_model(self, model_config: dict) -> None:
        if not self.is_available():
            api_key_env = self._config.get("api_key_env", "ANTHROPIC_API_KEY")
            raise BackendError(f"Anthropic API key not found. Set {api_key_env} environment variable.")

        try:
            import anthropic
        except ImportError:
            raise BackendError("anthropic package not installed. Run: uv pip install anthropic")

        api_key_env = self._config.get("api_key_env", "ANTHROPIC_API_KEY")
        self._client = anthropic.Anthropic(api_key=os.environ.get(api_key_env))
        self._model = model_config.get("anthropic_model", self._config.get("model", "claude-sonnet-4-20250514"))

    def unload_model(self) -> None:
        self._client = None

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._client:
            raise BackendError("Anthropic client not initialized.")

        params = params or {}

        # Separate system message
        system_msg = ""
        chat_messages = []
        for m in messages:
            if m.get("role") == "system":
                system_msg = m.get("content", "")
            else:
                chat_messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        if not chat_messages:
            chat_messages = [{"role": "user", "content": ""}]

        start = time.time()
        try:
            kwargs = {
                "model": self._model,
                "max_tokens": params.get("max_new_tokens", 512),
                "messages": chat_messages,
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.9),
            }
            if system_msg:
                kwargs["system"] = system_msg

            response = self._client.messages.create(**kwargs)
        except Exception as e:
            raise BackendError(f"Anthropic API error: {e}")

        elapsed = time.time() - start
        text = response.content[0].text if response.content else ""

        return GenerationResult(
            text=text,
            tokens_prompt=response.usage.input_tokens,
            tokens_gen=response.usage.output_tokens,
            finish_reason=response.stop_reason or "stop",
            elapsed=elapsed,
            backend=self.name,
        )

    def generate_stream(self, messages: list[dict], params: dict | None = None) -> Generator[str, None, None]:
        if not self._client:
            raise BackendError("Anthropic client not initialized.")

        params = params or {}

        system_msg = ""
        chat_messages = []
        for m in messages:
            if m.get("role") == "system":
                system_msg = m.get("content", "")
            else:
                chat_messages.append({"role": m.get("role", "user"), "content": m.get("content", "")})

        if not chat_messages:
            chat_messages = [{"role": "user", "content": ""}]

        try:
            kwargs = {
                "model": self._model,
                "max_tokens": params.get("max_new_tokens", 512),
                "messages": chat_messages,
                "temperature": params.get("temperature", 0.7),
            }
            if system_msg:
                kwargs["system"] = system_msg

            with self._client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise BackendError(f"Anthropic stream error: {e}")

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": self._client is not None,
            "model": self._model,
        }
