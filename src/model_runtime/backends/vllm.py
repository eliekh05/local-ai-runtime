"""
vLLM backend — high-throughput local inference.
Runs vllm serve as a subprocess or connects to an existing vLLM server.
"""

import time
import subprocess
import signal
from pathlib import Path
from typing import Generator

import httpx

from model_runtime.backends.base import Backend, GenerationResult, BackendError


class VLLMBackend(Backend):
    """vLLM backend — local high-throughput inference."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._base_url = self._config.get("base_url", "http://localhost:8000")
        self._model = self._config.get("model", "")
        self._process = None
        self._loaded = False

    @property
    def name(self) -> str:
        return "vllm"

    def is_available(self) -> bool:
        # Check if vllm is installed or if server is already running
        try:
            resp = httpx.get(f"{self._base_url}/v1/models", timeout=5)
            return resp.status_code == 200
        except Exception:
            pass

        # Check if vllm Python package is available
        try:
            import vllm
            return True
        except ImportError:
            return False

    def load_model(self, model_config: dict) -> None:
        self._model = model_config.get("vllm_model", self._config.get("model", ""))
        if not self._model:
            raise BackendError("No vLLM model specified.")

        # Try connecting to existing server first
        try:
            resp = httpx.get(f"{self._base_url}/v1/models", timeout=5)
            if resp.status_code == 200:
                self._loaded = True
                return
        except Exception:
            pass

        # Start vllm serve as subprocess
        try:
            cmd = [
                "python", "-m", "vllm.entrypoints.openai.api_server",
                "--model", self._model,
                "--port", str(self._base_url.split(":")[-1]) if ":" in self._base_url else "8000",
            ]
            gpu_layers = model_config.get("n_gpu_layers", 0)
            if gpu_layers > 0:
                cmd.extend(["--tensor-parallel-size", str(gpu_layers)])

            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Wait for server to be ready
            for _ in range(30):
                try:
                    resp = httpx.get(f"{self._base_url}/v1/models", timeout=2)
                    if resp.status_code == 200:
                        self._loaded = True
                        return
                except Exception:
                    time.sleep(1)

            raise BackendError("vLLM server failed to start within 30 seconds.")

        except FileNotFoundError:
            raise BackendError("vllm not installed. Run: uv pip install vllm")

    def unload_model(self) -> None:
        if self._process:
            self._process.send_signal(signal.SIGTERM)
            try:
                self._process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._process.kill()
            self._process = None
        self._loaded = False

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._loaded:
            raise BackendError("vLLM server not running.")

        params = params or {}
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
            "max_tokens": params.get("max_new_tokens", 512),
        }

        start = time.time()
        try:
            resp = httpx.post(f"{self._base_url}/v1/chat/completions", json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            raise BackendError(f"vLLM API error: {e}")

        elapsed = time.time() - start
        choice = data["choices"][0]
        usage = data.get("usage", {})

        return GenerationResult(
            text=choice["message"]["content"],
            tokens_prompt=usage.get("prompt_tokens", 0),
            tokens_gen=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
            elapsed=elapsed,
            backend=self.name,
        )

    def generate_stream(self, messages: list[dict], params: dict | None = None) -> Generator[str, None, None]:
        if not self._loaded:
            raise BackendError("vLLM server not running.")

        params = params or {}
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
            "max_tokens": params.get("max_new_tokens", 512),
            "stream": True,
        }

        try:
            with httpx.stream("POST", f"{self._base_url}/v1/chat/completions", json=payload, timeout=120) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line and line.startswith("data: "):
                        import json
                        data = json.loads(line[6:])
                        delta = data["choices"][0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            yield content
        except Exception as e:
            raise BackendError(f"vLLM stream error: {e}")

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": self._loaded,
            "model": self._model,
            "base_url": self._base_url,
        }
