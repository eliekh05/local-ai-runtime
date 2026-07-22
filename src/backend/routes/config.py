"""GET /config and PUT /config — Read/update active model configuration."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.model_config import ModelConfig
from backend.services.model_service import get_active_config, set_active_config, scan_model_directory

router = APIRouter()


class ConfigUpdate(BaseModel):
    backend_type: str | None = None
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


class APIKeySet(BaseModel):
    backend: str
    api_key: str
    base_url: str | None = None
    model: str | None = None


@router.post("/apikey")
async def set_api_key(body: APIKeySet):
    """Store API key in process env for the session (and optional compatible settings)."""
    import os

    env_map = {
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "gemini": "GEMINI_API_KEY",
    }
    env_var = env_map.get(body.backend)
    if env_var:
        os.environ[env_var] = body.api_key
        return {"message": f"API key set for {body.backend}"}

    config = get_active_config() or ModelConfig(model_file="")
    if body.backend == "openai_compatible":
        config.backend_type = "openai_compatible"
        if body.base_url:
            config.compatible_base_url = body.base_url
            config.api_backends.setdefault("openai_compatible", {})
            config.api_backends["openai_compatible"]["base_url"] = body.base_url
            config.api_backends["openai_compatible"]["enabled"] = True
        if body.model:
            config.compatible_model = body.model
            config.model_file = body.model
            config.api_backends["openai_compatible"]["model"] = body.model
        if body.api_key:
            os.environ["OPENAI_COMPATIBLE_API_KEY"] = body.api_key
            config.api_backends["openai_compatible"]["api_key_env"] = "OPENAI_COMPATIBLE_API_KEY"
        set_active_config(config)
        return {"message": "OpenAI-compatible backend configured"}
    if body.backend == "ollama":
        return {"message": "Ollama uses local connection, no API key needed"}
    if body.backend == "vllm":
        return {"message": "vLLM uses local connection, no API key needed"}
    raise HTTPException(status_code=400, detail=f"Unknown backend: {body.backend}")
