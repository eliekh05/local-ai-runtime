"""
Config loader — ALL values come from JSON config files.
Zero hardcoded defaults. If config is missing, fail loudly.
"""

import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
SERVER_CONFIG_PATH = CONFIG_DIR / "server.config.json"
MODEL_CONFIG_PATH = CONFIG_DIR / "model.config.json"


def _load_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path) as f:
        return json.load(f)


def load_server_config() -> dict:
    """Load server.config.json — host, port, cors, timeouts, all from file."""
    return _load_json(SERVER_CONFIG_PATH)


def load_model_config() -> dict:
    """Load model.config.json — model file, backend, template, generation params."""
    return _load_json(MODEL_CONFIG_PATH)


def save_model_config(config: dict) -> None:
    """Write model.config.json."""
    MODEL_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODEL_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def save_server_config(config: dict) -> None:
    """Write server.config.json."""
    SERVER_CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SERVER_CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
