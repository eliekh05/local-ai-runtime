"""
CLI entry point for `uvx local-ai-runtime` or `local-ai-runtime`.

On macOS: detects if running via uvx and recommends brew install instead.
"""

import sys
import platform
import subprocess
import shutil
from pathlib import Path


BREW_INSTALL_MSG = """
┌─────────────────────────────────────────────────────────┐
│  On macOS, we recommend installing via Homebrew:        │
│                                                         │
│    brew install local-ai-runtime                        │
│                                                         │
│  From: https://brew.sh                                  │
│                                                         │
│  This gives better native performance on Apple Silicon. │
│  To install Homebrew:                                   │
│    /bin/bash -c "$(curl -fsSL                           │
│      https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"  │
│                                                         │
│  Then: brew install local-ai-runtime                    │
│  Or to skip this and run anyway:                        │
│    local-ai-runtime --force-uvx                        │
└─────────────────────────────────────────────────────────┘
"""


def _is_macos() -> bool:
    return platform.system() == "Darwin"


def _is_running_via_uvx() -> bool:
    """Detect if we were invoked via uvx (temp venv, not brew)."""
    executable = sys.executable or ""
    # uvx runs from a temp dir like /Users/.../.local/share/uv/tools/...
    return "uv" in executable or "uvx" in executable or "/tools/" in executable


def _is_brew_installed() -> bool:
    """Check if local-ai-runtime is available via brew."""
    return shutil.which("brew") is not None


def main():
    args = sys.argv[1:]

    # macOS + uvx detection: recommend brew
    if _is_macos() and _is_running_via_uvx() and "--force-uvx" not in args:
        print(BREW_INSTALL_MSG)
        if _is_brew_installed():
            print("  Run: brew install local-ai-runtime\n")
        else:
            print("  Install Homebrew first, then brew install local-ai-runtime\n")
            print("  Or re-run with --force-uvx to continue anyway.\n")
        sys.exit(0)

    # Remove --force-uvx from args before passing to uvicorn
    args = [a for a in args if a != "--force-uvx"]

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
