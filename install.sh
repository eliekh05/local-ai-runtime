#!/bin/bash
set -e

# local-ai-runtime installer
# Works on macOS and Linux with uv + Python 3.11+

echo "local-ai-runtime installer"
echo "========================="
echo ""

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Check uv is available
if ! command -v uv &> /dev/null; then
    echo "ERROR: uv not found after install. Add ~/.local/bin to PATH"
    echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
    exit 1
fi

echo "Using uv: $(uv --version)"
echo "Using Python: $(python3 --version 2>/dev/null || echo 'not found')"
echo ""

# Determine install method
if [[ "$1" == "--brew" ]]; then
    echo "Installing via Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Install it first:"
        echo '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        exit 1
    fi
    brew install local-ai-runtime
    exit 0
fi

# uvx method (recommended for quick install)
if [[ "$1" == "--uvx" ]] || [[ -z "$1" ]]; then
    echo "Starting local-ai-runtime via uvx..."
    echo "  Press Ctrl+C to stop"
    echo ""
    uvx --from local-ai-runtime local-ai-runtime "${@:2}"
    exit $?
fi

# Development install
if [[ "$1" == "--dev" ]]; then
    echo "Setting up development environment..."
    cd "$(dirname "$0")"
    uv sync
    echo ""
    echo "Dev setup complete. Run:"
    echo "  uv run local-ai-runtime"
    echo "  # or in another terminal:"
    echo "  cd frontend && npm install && npm run dev"
    exit 0
fi

echo "Usage:"
echo "  install.sh          # Run via uvx (quick start)"
echo "  install.sh --brew   # Install via Homebrew"
echo "  install.sh --dev    # Development setup"
echo ""
echo "Or directly:"
echo "  uvx local-ai-runtime"
echo "  brew install local-ai-runtime"
