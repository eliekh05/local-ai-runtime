"""OpenAI-compatible backend — httpx only. Works with any /v1 endpoint."""

import json
import os
import time
from typing import Generator

import httpx

from model_runtime.backends.base import Backend, BackendError, GenerationResult


class OpenAICompatibleBackend(Backend):
    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._api_key = ""
        self._base_url = ""
        self._model = ""

    @property
    def name(self) -> str:
        return "openai_compatible"

    def is_available(self) -> bool:
        return True

    def load_model(self, model_config: dict) -> None:
        self._base_url = (
            self._config.get("base_url")
            or model_config.get("compatible_base_url")
            or ""
        ).rstrip("/")
        api_key_env = self._config.get("api_key_env") or model_config.get("compatible_api_key_env") or ""
        self._api_key = os.environ.get(api_key_env, "") if api_key_env else self._config.get("api_key", "")
        self._model = (
            model_config.get("compatible_model")
            or model_config.get("model_file")
            or self._config.get("model")
            or ""
        )
        if not self._base_url:
            raise BackendError("Set base_url for openai_compatible backend")
        if not self._model:
            try:
                resp = httpx.get(f"{self._base_url}/models", headers=self._headers(), timeout=10)
                models = resp.json().get("data", [])
                if models:
                    self._model = models[0]["id"]
            except Exception:
                pass
            if not self._model:
                raise BackendError("No model specified and couldn't auto-detect")

    def unload_model(self) -> None:
        self._api_key = ""
        self._base_url = ""
        self._model = ""

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        params = params or {}
        body = {
            "model": self._model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
            "max_tokens": params.get("max_new_tokens", 512),
        }
        start = time.time()
        resp = httpx.post(
            f"{self._base_url}/chat/completions",
            json=body,
            headers=self._headers(),
            timeout=120,
        )
        if resp.status_code != 200:
            raise BackendError(f"API {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        choice = data["choices"][0]
        usage = data.get("usage", {})
        return GenerationResult(
            text=choice["message"]["content"],
            tokens_prompt=usage.get("prompt_tokens", 0),
            tokens_gen=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
            elapsed=time.time() - start,
            backend=self.name,
        )

    def generate_stream(
        self, messages: list[dict], params: dict | None = None
    ) -> Generator[str, None, None]:
        params = params or {}
        body = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
            "max_tokens": params.get("max_new_tokens", 512),
        }
        with httpx.stream(
            "POST",
            f"{self._base_url}/chat/completions",
            json=body,
            headers=self._headers(),
            timeout=120,
        ) as resp:
            if resp.status_code != 200:
                raise BackendError(f"API stream {resp.status_code}: {resp.read().decode()[:200]}")
            for line in resp.iter_lines():
                if not line.startswith("data: ") or line == "data: [DONE]":
                    continue
                data = json.loads(line[6:])
                delta = data["choices"][0].get("delta", {})
                if delta.get("content"):
                    yield delta["content"]

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": bool(self._base_url and self._model),
            "model": self._model,
            "base_url": self._base_url,
        }
