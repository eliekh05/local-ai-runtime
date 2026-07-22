"""GET /config and PUT /config — Read/update active model configuration."""

import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.model_config import ModelConfig
from backend.services.model_service import get_active_config, set_active_config, scan_model_directory
from model_runtime.providers import get_provider, list_providers, resolve_provider_config

router = APIRouter()


class ConfigUpdate(BaseModel):
    backend_type: str | None = None
    provider_id: str | None = None
    model_file: str | None = None
    chat_template: str | None = None
    context_length: int | None = None
    system_prompt: str | None = None
    n_gpu_layers: int | None = None
    generation: dict | None = None
    openai_model: str | None = None
    anthropic_model: str | None = None
    gemini_model: str | None = None
    ollama_model: str | None = None
    vllm_model: str | None = None
    compatible_model: str | None = None
    compatible_base_url: str | None = None
    api_backends: dict | None = None


@router.get("/")
async def get_config():
    config = get_active_config()
    if config is None:
        raise HTTPException(status_code=404, detail="No active model configuration.")
    data = config.to_dict()
    data["ready"] = config.is_ready()
    return data


@router.put("/")
async def update_config(update: ConfigUpdate):
    config = get_active_config()
    if config is None:
        config = ModelConfig(model_file="")

    if update.provider_id is not None:
        config.provider_id = update.provider_id
    if update.backend_type is not None:
        config.backend_type = update.backend_type
    if update.model_file is not None:
        # Only validate GGUF file existence for llama-cpp backend
        bt = update.backend_type or config.backend_type
        if bt == "llama-cpp":
            models = scan_model_directory()
            filenames = [m["filename"] for m in models]
            if update.model_file and update.model_file not in filenames:
                raise HTTPException(status_code=404, detail=f"Model not found: {update.model_file}")
        config.model_file = update.model_file
        # Keep provider-specific fields in sync when wizard only sends model_file
        bt = update.backend_type or config.backend_type
        if bt == "openai" and not update.openai_model:
            config.openai_model = update.model_file
        elif bt == "anthropic" and not update.anthropic_model:
            config.anthropic_model = update.model_file
        elif bt == "gemini" and not update.gemini_model:
            config.gemini_model = update.model_file
        elif bt == "ollama" and not update.ollama_model:
            config.ollama_model = update.model_file
        elif bt == "vllm" and not update.vllm_model:
            config.vllm_model = update.model_file
        elif bt == "openai_compatible" and not update.compatible_model:
            config.compatible_model = update.model_file
    if update.chat_template is not None:
        config.chat_template = update.chat_template
    if update.context_length is not None:
        config.context_length = update.context_length
    if update.system_prompt is not None:
        config.system_prompt = update.system_prompt
    if update.n_gpu_layers is not None:
        config.n_gpu_layers = update.n_gpu_layers
    if update.generation is not None:
        for key, val in update.generation.items():
            if hasattr(config.generation, key):
                setattr(config.generation, key, val)
    if update.openai_model is not None:
        config.openai_model = update.openai_model
        config.model_file = update.openai_model
    if update.anthropic_model is not None:
        config.anthropic_model = update.anthropic_model
        config.model_file = update.anthropic_model
    if update.gemini_model is not None:
        config.gemini_model = update.gemini_model
        config.model_file = update.gemini_model
    if update.ollama_model is not None:
        config.ollama_model = update.ollama_model
        config.model_file = update.ollama_model
    if update.vllm_model is not None:
        config.vllm_model = update.vllm_model
        config.model_file = update.vllm_model
    if update.compatible_model is not None:
        config.compatible_model = update.compatible_model
        config.model_file = update.compatible_model
    if update.compatible_base_url is not None:
        config.compatible_base_url = update.compatible_base_url
        config.api_backends.setdefault("openai_compatible", {})
        config.api_backends["openai_compatible"]["base_url"] = update.compatible_base_url
        config.api_backends["openai_compatible"]["enabled"] = True
    if update.api_backends is not None:
        for name, cfg in update.api_backends.items():
            config.api_backends[name] = {**config.api_backends.get(name, {}), **cfg}

    # Mark selected API backend enabled
    if config.backend_type in config.api_backends:
        config.api_backends[config.backend_type]["enabled"] = True

    set_active_config(config)
    data = config.to_dict()
    data["ready"] = config.is_ready()
    return {"message": "Config updated", "config": data}


@router.get("/backends")
async def list_backends():
    from model_runtime.backends import list_backends as _list
    return {"backends": _list()}


@router.get("/providers")
async def providers():
    """Onboarding catalog: 10+ BYOK / local / router providers."""
    return {"providers": list_providers()}


class APIKeySet(BaseModel):
    backend: str | None = None
    provider: str | None = None
    api_key: str = ""
    base_url: str | None = None
    model: str | None = None


def _apply_resolved(config: ModelConfig, resolved: dict) -> ModelConfig:
    config.provider_id = resolved["provider_id"]
    config.backend_type = resolved["backend_type"]
    config.model_file = resolved.get("model_file") or config.model_file
    for key in (
        "openai_model",
        "anthropic_model",
        "gemini_model",
        "ollama_model",
        "vllm_model",
        "compatible_model",
        "compatible_base_url",
    ):
        if key in resolved and resolved[key] is not None:
            setattr(config, key, resolved[key])
    for name, cfg in (resolved.get("api_backends") or {}).items():
        config.api_backends[name] = {**config.api_backends.get(name, {}), **cfg}
    for env_name, value in (resolved.get("env") or {}).items():
        os.environ[env_name] = value
    return config


@router.post("/apikey")
@router.post("/apikey/")
async def set_api_key(body: APIKeySet):
    """Configure a provider (BYOK) for the session and persist model settings."""
    provider_id = body.provider or body.backend
    if not provider_id:
        raise HTTPException(status_code=400, detail="provider or backend is required")

    # Legacy aliases
    if provider_id == "openai_compatible":
        provider_id = "custom"

    if get_provider(provider_id) is None:
        # Allow raw backend ids that match native engines
        if provider_id in ("openai", "anthropic", "gemini", "ollama", "vllm", "llama-cpp"):
            pass
        else:
            raise HTTPException(status_code=400, detail=f"Unknown provider: {provider_id}")

    try:
        resolved = resolve_provider_config(
            provider_id,
            api_key=body.api_key or None,
            base_url=body.base_url,
            model=body.model,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    provider = get_provider(provider_id)
    if provider and provider.get("needs_key") and not body.api_key:
        raise HTTPException(status_code=400, detail=f"API key required for {provider['name']}")

    config = get_active_config() or ModelConfig(model_file="")
    config = _apply_resolved(config, resolved)
    set_active_config(config)
    return {
        "message": f"Provider '{provider_id}' configured",
        "provider_id": provider_id,
        "backend_type": config.backend_type,
        "ready": config.is_ready(),
    }
