"""
BYOK provider catalog — 10+ backends for the hybrid runtime.

Each provider maps to an inference backend (llama-cpp, ollama, vllm,
openai, anthropic, gemini, or openai_compatible) plus defaults for
base URL, env var, and suggested models. Presets that speak OpenAI's
HTTP API reuse the openai_compatible engine.
"""

from __future__ import annotations

from typing import Any

# Native engines (own Python backends)
NATIVE_BACKENDS = frozenset({
    "llama-cpp",
    "ollama",
    "vllm",
    "openai",
    "anthropic",
    "gemini",
    "openai_compatible",
})

PROVIDERS: list[dict[str, Any]] = [
    # --- Local ---
    {
        "id": "ollama",
        "name": "Ollama",
        "desc": "Local models via ollama serve",
        "kind": "local",
        "backend": "ollama",
        "needs_key": False,
        "needs_url": False,
        "needs_model": True,
        "base_url": "http://localhost:11434",
        "api_key_env": "",
        "default_model": "llama3.2",
        "models": ["llama3.2", "llama3.1", "mistral", "phi3", "qwen2.5", "codellama"],
        "placeholder": "",
    },
    {
        "id": "llama-cpp",
        "name": "llama.cpp",
        "desc": "Local GGUF files in models/",
        "kind": "local",
        "backend": "llama-cpp",
        "needs_key": False,
        "needs_url": False,
        "needs_model": True,
        "base_url": "",
        "api_key_env": "",
        "default_model": "",
        "models": [],
        "placeholder": "",
    },
    {
        "id": "vllm",
        "name": "vLLM",
        "desc": "High-throughput local OpenAI-compatible server",
        "kind": "local",
        "backend": "vllm",
        "needs_key": False,
        "needs_url": False,
        "needs_model": True,
        "base_url": "http://localhost:8000",
        "api_key_env": "",
        "default_model": "",
        "models": [],
        "placeholder": "",
    },
    {
        "id": "lmstudio",
        "name": "LM Studio",
        "desc": "Local LM Studio OpenAI server",
        "kind": "local",
        "backend": "openai_compatible",
        "needs_key": False,
        "needs_url": False,
        "needs_model": False,
        "base_url": "http://127.0.0.1:1234/v1",
        "api_key_env": "",
        "default_model": "",
        "models": [],
        "placeholder": "",
    },
    # --- Cloud / BYOK (native) ---
    {
        "id": "openai",
        "name": "OpenAI",
        "desc": "GPT-4o, o-series",
        "kind": "api",
        "backend": "openai",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.openai.com/v1",
        "api_key_env": "OPENAI_API_KEY",
        "default_model": "gpt-4o-mini",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1", "gpt-4.1-mini", "o3-mini", "o4-mini"],
        "placeholder": "sk-...",
    },
    {
        "id": "anthropic",
        "name": "Anthropic",
        "desc": "Claude Opus, Sonnet, Haiku",
        "kind": "api",
        "backend": "anthropic",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.anthropic.com",
        "api_key_env": "ANTHROPIC_API_KEY",
        "default_model": "claude-sonnet-4-20250514",
        "models": [
            "claude-opus-4-20250514",
            "claude-sonnet-4-20250514",
            "claude-haiku-4-5-20251001",
        ],
        "placeholder": "sk-ant-...",
    },
    {
        "id": "gemini",
        "name": "Google Gemini",
        "desc": "Gemini Flash / Pro",
        "kind": "api",
        "backend": "gemini",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://generativelanguage.googleapis.com",
        "api_key_env": "GEMINI_API_KEY",
        "default_model": "gemini-2.0-flash",
        "models": ["gemini-2.0-flash", "gemini-2.5-flash", "gemini-2.5-pro"],
        "placeholder": "AIza...",
    },
    # --- Cloud / BYOK (OpenAI-compatible presets) ---
    {
        "id": "openrouter",
        "name": "OpenRouter",
        "desc": "Multi-model router (hundreds of models)",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_env": "OPENROUTER_API_KEY",
        "default_model": "openai/gpt-4o-mini",
        "models": [
            "openai/gpt-4o-mini",
            "anthropic/claude-sonnet-4",
            "google/gemini-2.0-flash-001",
            "meta-llama/llama-3.3-70b-instruct",
        ],
        "placeholder": "sk-or-...",
    },
    {
        "id": "groq",
        "name": "Groq",
        "desc": "Fast Llama / Mixtral inference",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_env": "GROQ_API_KEY",
        "default_model": "llama-3.3-70b-versatile",
        "models": [
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it",
        ],
        "placeholder": "gsk_...",
    },
    {
        "id": "deepseek",
        "name": "DeepSeek",
        "desc": "DeepSeek Chat / Reasoner",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.deepseek.com/v1",
        "api_key_env": "DEEPSEEK_API_KEY",
        "default_model": "deepseek-chat",
        "models": ["deepseek-chat", "deepseek-reasoner"],
        "placeholder": "sk-...",
    },
    {
        "id": "mistral",
        "name": "Mistral",
        "desc": "Mistral Large / Small / Codestral",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.mistral.ai/v1",
        "api_key_env": "MISTRAL_API_KEY",
        "default_model": "mistral-small-latest",
        "models": [
            "mistral-large-latest",
            "mistral-small-latest",
            "codestral-latest",
            "open-mistral-nemo",
        ],
        "placeholder": "...",
    },
    {
        "id": "together",
        "name": "Together AI",
        "desc": "Open models via Together",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.together.xyz/v1",
        "api_key_env": "TOGETHER_API_KEY",
        "default_model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "models": [
            "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
            "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "Qwen/Qwen2.5-72B-Instruct-Turbo",
        ],
        "placeholder": "...",
    },
    {
        "id": "fireworks",
        "name": "Fireworks",
        "desc": "Fast open-model inference",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.fireworks.ai/inference/v1",
        "api_key_env": "FIREWORKS_API_KEY",
        "default_model": "accounts/fireworks/models/llama-v3p1-8b-instruct",
        "models": [
            "accounts/fireworks/models/llama-v3p1-8b-instruct",
            "accounts/fireworks/models/llama-v3p3-70b-instruct",
        ],
        "placeholder": "...",
    },
    {
        "id": "xai",
        "name": "xAI",
        "desc": "Grok models",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": True,
        "needs_url": False,
        "needs_model": True,
        "base_url": "https://api.x.ai/v1",
        "api_key_env": "XAI_API_KEY",
        "default_model": "grok-3-mini",
        "models": ["grok-3", "grok-3-mini", "grok-2-latest"],
        "placeholder": "xai-...",
    },
    {
        "id": "nine_router",
        "name": "9router",
        "desc": "Local 9router OpenAI-compatible gateway",
        "kind": "router",
        "backend": "openai_compatible",
        "needs_key": False,
        "needs_url": False,
        "needs_model": False,
        "base_url": "http://127.0.0.1:20128/api/v1",
        "api_key_env": "NINE_ROUTER_API_KEY",
        "default_model": "claude-my-combo",
        "models": ["claude-my-combo"],
        "placeholder": "sk-... (optional)",
    },
    {
        "id": "custom",
        "name": "Custom OpenAI-compatible",
        "desc": "Any /v1 endpoint (LiteLLM, proxy, self-hosted)",
        "kind": "api",
        "backend": "openai_compatible",
        "needs_key": False,
        "needs_url": True,
        "needs_model": False,
        "base_url": "",
        "api_key_env": "OPENAI_COMPATIBLE_API_KEY",
        "default_model": "",
        "models": [],
        "placeholder": "API key (optional)",
    },
]

_BY_ID = {p["id"]: p for p in PROVIDERS}


def list_providers() -> list[dict[str, Any]]:
    """Public catalog for onboarding UI and docs."""
    return [dict(p) for p in PROVIDERS]


def get_provider(provider_id: str) -> dict[str, Any] | None:
    return dict(_BY_ID[provider_id]) if provider_id in _BY_ID else None


def resolve_provider_config(
    provider_id: str,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """
    Resolve a provider selection into ModelConfig fields + env to set.

    Returns:
      {
        "provider_id", "backend_type", "model_file",
        "compatible_base_url", "compatible_model",
        "openai_model" | "anthropic_model" | ...,
        "api_backends": {...},
        "env": {ENV: key}  # keys to set in process env
      }
    """
    provider = get_provider(provider_id)
    if not provider:
        raise ValueError(f"Unknown provider: {provider_id}")

    backend = provider["backend"]
    chosen_model = (model or provider.get("default_model") or "").strip()
    chosen_url = (base_url or provider.get("base_url") or "").rstrip("/")
    env_name = provider.get("api_key_env") or ""
    env: dict[str, str] = {}
    if api_key and env_name:
        env[env_name] = api_key

    result: dict[str, Any] = {
        "provider_id": provider_id,
        "backend_type": backend,
        "model_file": chosen_model or provider_id,
        "api_backends": {},
        "env": env,
    }

    if backend == "openai":
        result["openai_model"] = chosen_model or "gpt-4o-mini"
        result["api_backends"]["openai"] = {
            "enabled": True,
            "api_key_env": env_name or "OPENAI_API_KEY",
            "base_url": chosen_url or "https://api.openai.com/v1",
            "model": result["openai_model"],
        }
    elif backend == "anthropic":
        result["anthropic_model"] = chosen_model or "claude-sonnet-4-20250514"
        result["api_backends"]["anthropic"] = {
            "enabled": True,
            "api_key_env": env_name or "ANTHROPIC_API_KEY",
            "model": result["anthropic_model"],
        }
    elif backend == "gemini":
        result["gemini_model"] = chosen_model or "gemini-2.0-flash"
        result["api_backends"]["gemini"] = {
            "enabled": True,
            "api_key_env": env_name or "GEMINI_API_KEY",
            "model": result["gemini_model"],
        }
    elif backend == "ollama":
        result["ollama_model"] = chosen_model
        result["api_backends"]["ollama"] = {
            "enabled": True,
            "base_url": chosen_url or "http://localhost:11434",
            "model": chosen_model,
        }
    elif backend == "vllm":
        result["vllm_model"] = chosen_model
        result["api_backends"]["vllm"] = {
            "enabled": True,
            "base_url": chosen_url or "http://localhost:8000",
            "model": chosen_model,
        }
    elif backend == "llama-cpp":
        pass
    elif backend == "openai_compatible":
        if not chosen_url:
            raise ValueError(f"Provider '{provider_id}' requires a base_url")
        result["compatible_base_url"] = chosen_url
        result["compatible_model"] = chosen_model
        result["api_backends"]["openai_compatible"] = {
            "enabled": True,
            "base_url": chosen_url,
            "api_key_env": env_name if (api_key or env_name) else "",
            "model": chosen_model,
        }
        # Always stash key under a stable env when provided
        if api_key:
            key_env = env_name or "OPENAI_COMPATIBLE_API_KEY"
            env[key_env] = api_key
            result["env"] = env
            result["api_backends"]["openai_compatible"]["api_key_env"] = key_env
    else:
        raise ValueError(f"Unsupported backend for provider: {backend}")

    return result
