"""OpenAI API backend — httpx only, no SDK."""

import json
import os
import time
from typing import Generator

import httpx

from model_runtime.backends.base import Backend, BackendError, GenerationResult


class OpenAIBackend(Backend):
    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._api_key = ""
        self._base_url = "https://api.openai.com/v1"
        self._model = "gpt-4o-mini"

    @property
    def name(self) -> str:
        return "openai"

    def is_available(self) -> bool:
        return True

    def load_model(self, model_config: dict) -> None:
        self._api_key = os.environ.get(self._config.get("api_key_env", "OPENAI_API_KEY"), "")
        self._base_url = self._config.get("base_url", "https://api.openai.com/v1").rstrip("/")
        self._model = (
            model_config.get("openai_model")
            or model_config.get("model_file")
            or self._config.get("model")
            or "gpt-4o-mini"
        )
        if not self._api_key:
            raise BackendError("Set OPENAI_API_KEY env var")

    def unload_model(self) -> None:
        self._api_key = ""

    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"}

    def _body(self, messages: list[dict], params: dict, stream: bool = False) -> dict:
        body = {
            "model": self._model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
            "max_tokens": params.get("max_new_tokens", 512),
            "stream": stream,
        }
        if params.get("seed", -1) >= 0:
            body["seed"] = params["seed"]
        return body

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._api_key:
            raise BackendError("No API key")
        params = params or {}
        start = time.time()
        resp = httpx.post(
            f"{self._base_url}/chat/completions",
            json=self._body(messages, params),
            headers=self._headers(),
            timeout=120,
        )
        if resp.status_code != 200:
            raise BackendError(f"OpenAI {resp.status_code}: {resp.text[:200]}")
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
        if not self._api_key:
            raise BackendError("No API key")
        params = params or {}
        with httpx.stream(
            "POST",
            f"{self._base_url}/chat/completions",
            json=self._body(messages, params, stream=True),
            headers=self._headers(),
            timeout=120,
        ) as resp:
            if resp.status_code != 200:
                raise BackendError(f"OpenAI stream {resp.status_code}: {resp.read().decode()[:200]}")
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
            "model_loaded": bool(self._api_key),
            "model": self._model,
        }
