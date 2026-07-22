"""GET /config and PUT /config — Read/update active model configuration."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.models.model_config import ModelConfig, GenerationParams
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
    ollama_model: str | None = None
    vllm_model: str | None = None


@router.get("/")
async def get_config():
    config = get_active_config()
    if config is None:
        raise HTTPException(status_code=404, detail="No active model configuration.")
    return config.to_dict()


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

    set_active_config(config)
    return {"message": "Config updated", "config": config.to_dict()}


@router.get("/backends")
async def list_backends():
    from model_runtime.backends import list_backends as _list
    return {"backends": _list()}
