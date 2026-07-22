"""Anthropic API backend — httpx only, no SDK."""

import json
import os
import time
from typing import Generator

import httpx

from model_runtime.backends.base import Backend, BackendError, GenerationResult


class AnthropicBackend(Backend):
    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._api_key = ""
        self._model = "claude-sonnet-4-20250514"

    @property
    def name(self) -> str:
        return "anthropic"

    def is_available(self) -> bool:
        return True

    def load_model(self, model_config: dict) -> None:
        self._api_key = os.environ.get(self._config.get("api_key_env", "ANTHROPIC_API_KEY"), "")
        self._model = (
            model_config.get("anthropic_model")
            or model_config.get("model_file")
            or self._config.get("model")
            or "claude-sonnet-4-20250514"
        )
        if not self._api_key:
            raise BackendError("Set ANTHROPIC_API_KEY env var")

    def unload_model(self) -> None:
        self._api_key = ""

    def _headers(self) -> dict:
        return {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

    def _split_messages(self, messages: list[dict]) -> tuple[str, list[dict]]:
        system = ""
        chat = []
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content", "")
            else:
                chat.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        if not chat:
            chat = [{"role": "user", "content": ""}]
        return system, chat

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._api_key:
            raise BackendError("No API key")
        params = params or {}
        system, chat = self._split_messages(messages)
        body = {
            "model": self._model,
            "max_tokens": params.get("max_new_tokens", 512),
            "messages": chat,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
        }
        if system:
            body["system"] = system
        start = time.time()
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            json=body,
            headers=self._headers(),
            timeout=120,
        )
        if resp.status_code != 200:
            raise BackendError(f"Anthropic {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        text = data["content"][0]["text"] if data.get("content") else ""
        usage = data.get("usage", {})
        return GenerationResult(
            text=text,
            tokens_prompt=usage.get("input_tokens", 0),
            tokens_gen=usage.get("output_tokens", 0),
            finish_reason=data.get("stop_reason", "stop"),
            elapsed=time.time() - start,
            backend=self.name,
        )

    def generate_stream(
        self, messages: list[dict], params: dict | None = None
    ) -> Generator[str, None, None]:
        if not self._api_key:
            raise BackendError("No API key")
        params = params or {}
        system, chat = self._split_messages(messages)
        body = {
            "model": self._model,
            "max_tokens": params.get("max_new_tokens", 512),
            "messages": chat,
            "temperature": params.get("temperature", 0.7),
            "stream": True,
        }
        if system:
            body["system"] = system
        with httpx.stream(
            "POST",
            "https://api.anthropic.com/v1/messages",
            json=body,
            headers=self._headers(),
            timeout=120,
        ) as resp:
            if resp.status_code != 200:
                raise BackendError(f"Anthropic stream {resp.status_code}: {resp.read().decode()[:200]}")
            for line in resp.iter_lines():
                if not line.startswith("data: "):
                    continue
                data = json.loads(line[6:])
                if data.get("type") == "content_block_delta":
                    text = data.get("delta", {}).get("text", "")
                    if text:
                        yield text

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": bool(self._api_key),
            "model": self._model,
        }
