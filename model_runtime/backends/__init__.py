"""
BYOK Backend Adapters — bring your own key, bring your own model.

Supports:
  - llama-cpp: local GGUF via llama-cpp-python
  - ollama: local via ollama serve
  - vllm: local via vllm serve
  - openai: OpenAI API (GPT-4o, etc.)
  - anthropic: Anthropic API (Claude)
  - gemini: Google Gemini API
  - openai_compatible: any OpenAI-compatible endpoint (LiteLLM, LM Studio, etc.)

Each backend implements the same interface:
  - generate(messages, params) -> GenerationResult
  - generate_stream(messages, params) -> Generator[str]
  - is_available() -> bool
"""

from model_runtime.backends.base import Backend, GenerationResult, BackendError
from model_runtime.backends.registry import get_backend, list_backends, is_backend_available

__all__ = ["Backend", "GenerationResult", "BackendError", "get_backend", "list_backends", "is_backend_available"]
