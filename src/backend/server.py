"""
Legacy server.py — kept for backward compat.
The real entry point is local_ai_runtime/cli.py -> local_ai_runtime/server.py.
This file exists so `python backend/server.py` still works.
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import uvicorn

CONFIG_DIR = _PROJECT_ROOT / "config"
SERVER_CONFIG_PATH = CONFIG_DIR / "server.config.json"


def load_server_config() -> dict:
    if SERVER_CONFIG_PATH.exists():
        with open(SERVER_CONFIG_PATH) as f:
            return json.load(f)
    raise FileNotFoundError(f"Config not found: {SERVER_CONFIG_PATH}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    config = load_server_config()
    uvicorn.run(
        "backend.server:app",
        host=config.get("host", "0.0.0.0"),
        port=config.get("port", 8000),
        log_level=config.get("log_level", "info"),
    )
