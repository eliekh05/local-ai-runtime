"""
CLI entry point for `uvx local-ai-runtime` or `local-ai-runtime`.
"""

import sys
import json
import logging
from pathlib import Path


def main():
    args = sys.argv[1:]

    # Load config and start server
    from local_ai_runtime.config import load_server_config
    from local_ai_runtime.server import create_app

    config = load_server_config()
    app = create_app(config)

    import uvicorn
    uvicorn.run(
        app,
        host=config.get("host", "0.0.0.0"),
        port=config.get("port", 8000),
        log_level=config.get("log_level", "info"),
    )


if __name__ == "__main__":
    main()
