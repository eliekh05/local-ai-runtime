"""
Google Gemini API backend.
"""

import os
import time
from typing import Generator

from model_runtime.backends.base import Backend, GenerationResult, BackendError


class GeminiBackend(Backend):
    """Google Gemini API backend (BYOK)."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._client = None
        self._model = self._config.get("model", "gemini-2.0-flash")

    @property
    def name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        return True  # API backend — always available, needs key at call time

    def load_model(self, model_config: dict) -> None:
        if not self.is_available():
            api_key_env = self._config.get("api_key_env", "GEMINI_API_KEY")
            raise BackendError(f"Gemini API key not found. Set {api_key_env} environment variable.")

        try:
            import google.generativeai as genai
        except ImportError:
            raise BackendError("google-generativeai not installed. Run: uv pip install google-generativeai")

        api_key_env = self._config.get("api_key_env", "GEMINI_API_KEY")
        genai.configure(api_key=os.environ.get(api_key_env))
        self._model = model_config.get("gemini_model", self._config.get("model", "gemini-2.0-flash"))
        self._client = genai.GenerativeModel(self._model)

    def unload_model(self) -> None:
        self._client = None

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._client:
            raise BackendError("Gemini client not initialized.")

        params = params or {}

        # Build prompt from messages
        system_msg = ""
        chat_parts = []
        for m in messages:
            if m.get("role") == "system":
                system_msg = m.get("content", "")
            else:
                chat_parts.append(f"{m.get('role', 'user')}: {m.get('content', '')}")

        prompt = ""
        if system_msg:
            prompt = f"System: {system_msg}\n\n"
        prompt += "\n".join(chat_parts)

        start = time.time()
        try:
            response = self._client.generate_content(
                prompt,
                generation_config={
                    "temperature": params.get("temperature", 0.7),
                    "top_p": params.get("top_p", 0.9),
                    "max_output_tokens": params.get("max_new_tokens", 512),
                },
            )
        except Exception as e:
            raise BackendError(f"Gemini API error: {e}")

        elapsed = time.time() - start
        text = response.text or ""
        usage = response.usage_metadata

        return GenerationResult(
            text=text,
            tokens_prompt=usage.prompt_token_count if usage else 0,
            tokens_gen=usage.candidates_token_count if usage else 0,
            finish_reason="stop",
            elapsed=elapsed,
            backend=self.name,
        )

    def generate_stream(self, messages: list[dict], params: dict | None = None) -> Generator[str, None, None]:
        if not self._client:
            raise BackendError("Gemini client not initialized.")

        params = params or {}

        system_msg = ""
        chat_parts = []
        for m in messages:
            if m.get("role") == "system":
                system_msg = m.get("content", "")
            else:
                chat_parts.append(f"{m.get('role', 'user')}: {m.get('content', '')}")

        prompt = ""
        if system_msg:
            prompt = f"System: {system_msg}\n\n"
        prompt += "\n".join(chat_parts)

        try:
            response = self._client.generate_content(
                prompt,
                generation_config={
                    "temperature": params.get("temperature", 0.7),
                    "top_p": params.get("top_p", 0.9),
                    "max_output_tokens": params.get("max_new_tokens", 512),
                },
                stream=True,
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            raise BackendError(f"Gemini stream error: {e}")

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": self._client is not None,
            "model": self._model,
        }
