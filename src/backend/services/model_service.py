"""
Service layer for model file management — config-driven, no hardcoded values.
"""

import json
from pathlib import Path

from models.model_config import ModelConfig

# Load paths from config, not hardcoded
_CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
_MODEL_CONFIG_PATH = _CONFIG_DIR / "model.config.json"
_MODELS_DIR = None  # Loaded from config at runtime


def _get_models_dir() -> Path:
    """Get models directory from config."""
    global _MODELS_DIR
    if _MODELS_DIR is not None:
        return _MODELS_DIR
    if _MODEL_CONFIG_PATH.exists():
        with open(_MODEL_CONFIG_PATH) as f:
            config = json.load(f)
        # Models dir relative to project root
        project_root = Path(__file__).resolve().parent.parent.parent
        _MODELS_DIR = project_root / config.get("models_dir", "./models")
    else:
        _MODELS_DIR = Path(__file__).resolve().parent.parent.parent / "models"
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
    _MODEL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_MODEL_CONFIG_PATH, "w") as f:
        json.dump(config.to_dict(), f, indent=2)


def scan_model_directory() -> list:
    models_dir = _get_models_dir()
    if not models_dir.exists():
        return []
    return [
        {
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "path": str(f),
        }
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
