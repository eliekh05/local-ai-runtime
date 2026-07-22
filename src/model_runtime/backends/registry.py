"""
Backend registry — dynamically loads backends based on config.
"""

from model_runtime.backends.base import Backend

_backend_instances: dict[str, Backend] = {}


def _get_all_backend_classes() -> dict[str, type[Backend]]:
    """Lazy-load all backend classes. Returns {name: class}."""
    classes = {}

    # Local backends
    try:
        from model_runtime.backends.llama_cpp import LlamaCppBackend
        classes["llama-cpp"] = LlamaCppBackend
    except ImportError:
        pass

    try:
        from model_runtime.backends.ollama import OllamaBackend
        classes["ollama"] = OllamaBackend
    except ImportError:
        pass

    try:
        from model_runtime.backends.vllm import VLLMBackend
        classes["vllm"] = VLLMBackend
    except ImportError:
        pass

    # API backends
    try:
        from model_runtime.backends.openai_backend import OpenAIBackend
        classes["openai"] = OpenAIBackend
    except ImportError:
        pass

    try:
        from model_runtime.backends.anthropic_backend import AnthropicBackend
        classes["anthropic"] = AnthropicBackend
    except ImportError:
        pass

    try:
        from model_runtime.backends.gemini_backend import GeminiBackend
        classes["gemini"] = GeminiBackend
    except ImportError:
        pass

    try:
        from model_runtime.backends.openai_compatible import OpenAICompatibleBackend
        classes["openai_compatible"] = OpenAICompatibleBackend
    except ImportError:
        pass

    return classes


def get_backend(name: str, config: dict | None = None) -> Backend:
    """Get or create a backend instance by name."""
    if name not in _backend_instances:
        classes = _get_all_backend_classes()
        if name not in classes:
            raise ValueError(f"Unknown backend: '{name}'. Available: {list(classes.keys())}")
        _backend_instances[name] = classes[name](config=config or {})
    return _backend_instances[name]


def list_backends() -> list[dict]:
    """List all available backends and their status."""
    classes = _get_all_backend_classes()
    result = []
    for name, cls in classes.items():
        try:
            instance = cls(config={})
            result.append({
                "name": name,
                "available": instance.is_available(),
                "type": "local" if name in ("llama-cpp", "ollama", "vllm") else "api",
            })
        except Exception:
            result.append({"name": name, "available": False, "type": "unknown"})
    return result


def is_backend_available(name: str) -> bool:
    """Check if a backend can be used."""
    try:
        backend = get_backend(name)
        return backend.is_available()
    except (ValueError, Exception):
        return False
