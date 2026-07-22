"""
Service layer for model file management — config-driven, no hardcoded values.
"""

import json
from pathlib import Path

from backend.models.model_config import ModelConfig

# Config lives in ~/.config/local-ai-runtime/
_USER_CONFIG_DIR = Path.home() / ".config" / "local-ai-runtime"
_MODEL_CONFIG_PATH = _USER_CONFIG_DIR / "model.config.json"
_MODELS_DIR = None


def _ensure_config():
    _USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _get_models_dir() -> Path:
    global _MODELS_DIR
    if _MODELS_DIR is not None:
        return _MODELS_DIR
    if _MODEL_CONFIG_PATH.exists():
        with open(_MODEL_CONFIG_PATH) as f:
            config = json.load(f)
        models_str = config.get("models_dir", "./models")
        _MODELS_DIR = Path(models_str)
        if not _MODELS_DIR.is_absolute():
            _MODELS_DIR = Path.cwd() / _MODELS_DIR
    else:
        _MODELS_DIR = Path.cwd() / "models"
    return _MODELS_DIR


_current_model_name: str | None = None
_model_is_loaded: bool = False
_active_config: ModelConfig | None = None


def is_model_loaded() -> bool:
    return _model_is_loaded


def get_current_model_name() -> str | None:
    return _current_model_name


def get_active_config() -> ModelConfig | None:
    global _active_config
    if _active_config is not None:
        return _active_config
    if _MODEL_CONFIG_PATH.exists():
        with open(_MODEL_CONFIG_PATH) as f:
            data = json.load(f)
        _active_config = ModelConfig.from_dict(data)
        return _active_config
    return None


def set_active_config(config: ModelConfig) -> None:
    global _active_config
    _active_config = config
    _ensure_config()
    with open(_MODEL_CONFIG_PATH, "w") as f:
        json.dump(config.to_dict(), f, indent=2)


def scan_model_directory() -> list:
    models_dir = _get_models_dir()
    if not models_dir.exists():
        return []
    return [
        {"filename": f.name, "size_bytes": f.stat().st_size, "path": str(f)}
        for f in sorted(models_dir.glob("*.gguf"))
    ]


def set_model_loaded(name: str) -> None:
    global _current_model_name, _model_is_loaded
    _current_model_name = name
    _model_is_loaded = True


def set_model_unloaded() -> None:
    global _current_model_name, _model_is_loaded
    _current_model_name = None
    _model_is_loaded = False
