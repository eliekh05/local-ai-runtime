"""
Config loader — ALL values come from JSON config files.
Looks in ~/.config/local-ai-runtime/ first, falls back to package dir.
"""

import json
import shutil
from pathlib import Path

# User config dir: ~/.config/local-ai-runtime/
USER_CONFIG_DIR = Path.home() / ".config" / "local-ai-runtime"

# Package bundled defaults
_BUNDLED_DIR = Path(__file__).resolve().parent.parent.parent / "config"

DEFAULT_SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "log_level": "info",
    "cors_origins": ["http://localhost:5173", "http://localhost:3000"],
    "api_prefix": "",
    "timeouts": {"inference_seconds": 120, "startup_seconds": 30},
    "models_dir": "./models",
}

DEFAULT_MODEL_CONFIG = {
    "backend_type": "llama-cpp",
    "model_file": "",
    "chat_template": "auto",
    "context_length": 4096,
    "system_prompt": "You are a helpful assistant.",
    "n_gpu_layers": 0,
    "models_dir": "./models",
    "generation": {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "repeat_penalty": 1.1,
        "max_new_tokens": 512,
        "seed": -1,
    },
    "api_backends": {
        "openai": {"enabled": False, "api_key_env": "OPENAI_API_KEY", "model": "gpt-4o-mini"},
        "anthropic": {"enabled": False, "api_key_env": "ANTHROPIC_API_KEY", "model": "claude-sonnet-4-20250514"},
        "gemini": {"enabled": False, "api_key_env": "GEMINI_API_KEY", "model": "gemini-2.0-flash"},
        "ollama": {"enabled": False, "base_url": "http://localhost:11434", "model": ""},
        "openai_compatible": {"enabled": False, "base_url": "", "api_key_env": "", "model": ""},
    },
}


def _ensure_user_config():
    """Create ~/.config/local-ai-runtime/ with defaults if missing."""
    USER_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    for name, defaults in [("server.config.json", DEFAULT_SERVER_CONFIG), ("model.config.json", DEFAULT_MODEL_CONFIG)]:
        dest = USER_CONFIG_DIR / name
        if not dest.exists():
            # Try bundled first
            bundled = _BUNDLED_DIR / name
            if bundled.exists():
                shutil.copy2(bundled, dest)
            else:
                with open(dest, "w") as f:
                    json.dump(defaults, f, indent=2)


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path) as f:
        return json.load(f)


def load_server_config() -> dict:
    """Load server.config.json from ~/.config/local-ai-runtime/."""
    _ensure_user_config()
    return _load_json(USER_CONFIG_DIR / "server.config.json")


def load_model_config() -> dict:
    """Load model.config.json from ~/.config/local-ai-runtime/."""
    _ensure_user_config()
    return _load_json(USER_CONFIG_DIR / "model.config.json")


def save_model_config(config: dict) -> None:
    _ensure_user_config()
    with open(USER_CONFIG_DIR / "model.config.json", "w") as f:
        json.dump(config, f, indent=2)


def save_server_config(config: dict) -> None:
    _ensure_user_config()
    with open(USER_CONFIG_DIR / "server.config.json", "w") as f:
        json.dump(config, f, indent=2)
