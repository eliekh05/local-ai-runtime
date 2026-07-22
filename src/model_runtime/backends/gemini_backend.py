"""Google Gemini API backend — httpx only, no SDK."""

import json
import os
import time
from typing import Generator

import httpx

from model_runtime.backends.base import Backend, BackendError, GenerationResult


class GeminiBackend(Backend):
    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._api_key = ""
        self._model = "gemini-2.0-flash"

    @property
    def name(self) -> str:
        return "gemini"

    def is_available(self) -> bool:
        return True

    def load_model(self, model_config: dict) -> None:
        self._api_key = os.environ.get(self._config.get("api_key_env", "GEMINI_API_KEY"), "")
        self._model = (
            model_config.get("gemini_model")
            or model_config.get("model_file")
            or self._config.get("model")
            or "gemini-2.0-flash"
        )
        if not self._api_key:
            raise BackendError("Set GEMINI_API_KEY env var")

    def unload_model(self) -> None:
        self._api_key = ""

    def _url(self, method: str = "generateContent", extra_query: str = "") -> str:
        q = f"key={self._api_key}"
        if extra_query:
            q = f"{extra_query}&{q}"
        return (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:{method}?{q}"
        )

    def _build_body(self, messages: list[dict], params: dict) -> dict:
        system = ""
        parts = []
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content", "")
            else:
                parts.append({"text": f"{m.get('role', 'user')}: {m.get('content', '')}"})
        body: dict = {"contents": [{"parts": parts or [{"text": ""}]}]}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        body["generationConfig"] = {
            "temperature": params.get("temperature", 0.7),
            "topP": params.get("top_p", 0.9),
            "maxOutputTokens": params.get("max_new_tokens", 512),
        }
        return body

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._api_key:
            raise BackendError("No API key")
        params = params or {}
        body = self._build_body(messages, params)
        start = time.time()
        resp = httpx.post(self._url(), json=body, timeout=120)
        if resp.status_code != 200:
            raise BackendError(f"Gemini {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        usage = data.get("usageMetadata", {})
        return GenerationResult(
            text=text,
            tokens_prompt=usage.get("promptTokenCount", 0),
            tokens_gen=usage.get("candidatesTokenCount", 0),
            finish_reason="stop",
            elapsed=time.time() - start,
            backend=self.name,
        )

    def generate_stream(
        self, messages: list[dict], params: dict | None = None
    ) -> Generator[str, None, None]:
        if not self._api_key:
            raise BackendError("No API key")
        params = params or {}
        body = self._build_body(messages, params)
        with httpx.stream(
            "POST",
            self._url("streamGenerateContent", extra_query="alt=sse"),
            json=body,
            timeout=120,
        ) as resp:
            if resp.status_code != 200:
                raise BackendError(f"Gemini stream {resp.status_code}: {resp.read().decode()[:200]}")
            for line in resp.iter_lines():
                if not line.startswith("data: "):
                    continue
                data = json.loads(line[6:])
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                if text:
                    yield text

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": bool(self._api_key),
            "model": self._model,
        }
