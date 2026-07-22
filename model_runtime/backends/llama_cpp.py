"""
llama.cpp backend — local GGUF inference via llama-cpp-python.
"""

import time
from pathlib import Path
from typing import Generator

from model_runtime.backends.base import Backend, GenerationResult, BackendError


class LlamaCppBackend(Backend):
    """Local GGUF inference via llama-cpp-python."""

    def __init__(self, config: dict | None = None):
        self._config = config or {}
        self._llm = None
        self._model_path = None

    @property
    def name(self) -> str:
        return "llama-cpp"

    def is_available(self) -> bool:
        try:
            import llama_cpp
            return True
        except ImportError:
            return False

    def load_model(self, model_config: dict) -> None:
        if not self.is_available():
            raise BackendError("llama-cpp-python not installed. Run: uv pip install llama-cpp-python")

        from llama_cpp import Llama

        model_file = model_config.get("model_file", "")
        if not model_file:
            raise BackendError("No model_file specified in config")

        models_dir = Path(self._config.get("models_dir", "./models"))
        model_path = models_dir / model_file

        if not model_path.exists():
            raise BackendError(f"Model file not found: {model_path}")

        file_size_gb = model_path.stat().st_size / (1024 ** 3)
        print(f"Loading {model_path.name} ({file_size_gb:.2f} GB) via llama.cpp...")

        start = time.time()
        try:
            self._llm = Llama(
                model_path=str(model_path),
                n_ctx=model_config.get("context_length", 4096),
                n_gpu_layers=model_config.get("n_gpu_layers", 0),
                verbose=False,
            )
        except Exception as e:
            raise BackendError(f"Failed to load model: {e}")

        self._model_path = model_path
        elapsed = time.time() - start
        print(f"Model loaded in {elapsed:.2f}s")

    def unload_model(self) -> None:
        self._llm = None
        self._model_path = None

    def generate(self, messages: list[dict], params: dict | None = None) -> GenerationResult:
        if not self._llm:
            raise BackendError("No model loaded")

        params = params or {}
        prompt = self._format_prompt(messages, params)

        gen_kwargs = {
            "max_tokens": params.get("max_new_tokens", 512),
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
            "top_k": params.get("top_k", 40),
            "repeat_penalty": params.get("repeat_penalty", 1.1),
            "stop": params.get("stop", ["</s>", "<|eot_id|>", "</output>", "[/INST]"]),
        }
        seed = params.get("seed", -1)
        if seed >= 0:
            gen_kwargs["seed"] = seed

        start = time.time()
        try:
            result = self._llm(prompt, **gen_kwargs)
            ttft = time.time() - start
        except Exception as e:
            raise BackendError(f"Generation failed: {e}")

        elapsed = time.time() - start
        choice = result["choices"][0]
        text = choice["text"]
        usage = result.get("usage", {})

        return GenerationResult(
            text=text,
            tokens_prompt=usage.get("prompt_tokens", 0),
            tokens_gen=usage.get("completion_tokens", 0),
            finish_reason=choice.get("finish_reason", "stop"),
            elapsed=elapsed,
            ttft=ttft,
            backend=self.name,
        )

    def generate_stream(self, messages: list[dict], params: dict | None = None) -> Generator[str, None, None]:
        if not self._llm:
            raise BackendError("No model loaded")

        params = params or {}
        prompt = self._format_prompt(messages, params)

        gen_kwargs = {
            "max_tokens": params.get("max_new_tokens", 512),
            "temperature": params.get("temperature", 0.7),
            "top_p": params.get("top_p", 0.9),
            "top_k": params.get("top_k", 40),
            "repeat_penalty": params.get("repeat_penalty", 1.1),
            "stop": params.get("stop", ["</s>", "<|eot_id|>", "</output>", "[/INST]"]),
            "stream": True,
        }
        seed = params.get("seed", -1)
        if seed >= 0:
            gen_kwargs["seed"] = seed

        try:
            for chunk in self._llm(prompt, **gen_kwargs):
                delta = chunk["choices"][0].get("delta", {})
                text = delta.get("content", "")
                if text:
                    yield text
        except Exception as e:
            raise BackendError(f"Stream generation failed: {e}")

    def _format_prompt(self, messages: list[dict], params: dict) -> str:
        """Format messages into a prompt string using the chat template."""
        from model_runtime.prompt_formatter import format_prompt
        template = params.get("chat_template", "chatml")
        return format_prompt(messages, template)

    def health_check(self) -> dict:
        return {
            "backend": self.name,
            "available": self.is_available(),
            "model_loaded": self._llm is not None,
            "model_path": str(self._model_path) if self._model_path else None,
        }
