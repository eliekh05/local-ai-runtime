"""
Ollama backend — local inference via ollama serve.
"""

import time
import json
import subprocess
from typing import Generator

import httpx

from model_runtime.backends.base import Backend, GenerationResult, BackendError


class OllamaBackend(Backend):
    """Local inference via Ollama."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._base_url = self._config.get("base_url", "http://localhost:11434")
        self._model = self._config.get("model", "")
        self._loaded = False

    @property
    def name(self) -> str:
        return "ollama"

    def is_available(self) -> bool:
        try:
            resp = httpx.get(f"{self._base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def load_model(self, model_config: dict) -> None:
        self._model = model_config.get("ollama_model", self._config.get("model", ""))
        if not self._model:
            raise BackendError("No ollama model specified. Set 'ollama_model' in config.")

        # Check if model exists locally
        try:
            resp = httpx.get(f"{self._base_url}/api/tags", timeout=10)
            models = resp.json().get("models", [])
            available = [m["name"] for m in models]
            if self._model not in available and f"{self._model}:latest" not in available:
                raise BackendError(
                    f"Model '{self._model}' not found in Ollama. "
                    f"Available: {available}. Run: ollama pull {self._model}"
                )
        except httpx.ConnectError:
            raise BackendError(f"Cannot connect to Ollama at {self._base_url}. Is 'ollama serve' running?")

        self._loaded = True

    def unload_model(self) -> None:
        self._loaded = False

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._loaded:
            raise BackendError("No model loaded")

        params = params or {}
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.9),
                "top_k": params.get("top_k", 40),
                "repeat_penalty": params.get("repeat_penalty", 1.1),
                "num_predict": params.get("max_new_tokens", 512),
            },
        }
        seed = params.get("seed", -1)
        if seed >= 0:
            payload["options"]["seed"] = seed

        start = time.time()
        try:
            resp = httpx.post(f"{self._base_url}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise BackendError(f"Ollama generation failed: {e}")

        elapsed = time.time() - start
        message = data.get("message", {})
        text = message.get("content", "")
        prompt_eval = data.get("prompt_eval_count", 0)
        eval_count = data.get("eval_count", 0)

        return GenerationResult(
            text=text,
            tokens_prompt=prompt_eval,
            tokens_gen=eval_count,
            finish_reason="stop" if data.get("done") else "length",
            elapsed=elapsed,
            backend=self.name,
        )

    def generate_stream(self, messages: list[dict], params: dict | None = None) -> Generator[str, None, None]:
        if not self._loaded:
            raise BackendError("No model loaded")

        params = params or {}
        payload = {
            "model": self._model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 0.9),
                "top_k": params.get("top_k", 40),
                "repeat_penalty": params.get("repeat_penalty", 1.1),
                "num_predict": params.get("max_new_tokens", 512),
            },
        }

        try:
            with httpx.stream("POST", f"{self._base_url}/api/chat", json=payload, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        data = json.loads(line)
                        chunk = data.get("message", {}).get("content", "")
                        if chunk:
                            yield chunk
        except Exception as e:
            raise BackendError(f"Ollama stream failed: {e}")

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": self._loaded,
            "model": self._model,
            "base_url": self._base_url,
        }
