# local-ai-runtime

> BYOK hybrid local AI chat runtime — run any model from anywhere.
> Local GGUF (llama.cpp), Ollama, vLLM, OpenAI, Anthropic, Gemini, or any OpenAI-compatible endpoint.

---

## Quick Start

### macOS (recommended via Homebrew)

```bash
brew install local-ai-runtime
local-ai-runtime
```

### Any platform (uvx)

```bash
uvx local-ai-runtime
```

On macOS, you'll be prompted to use Homebrew instead for better native performance.

### Development

```bash
git clone https://github.com/youruser/local-ai-runtime.git
cd local-ai-runtime

# Install dependencies with uv
uv sync

# Start the backend
uv run local-ai-runtime

# Start the frontend (separate terminal)
cd frontend && npm install && npm run dev
```

---

## What This Is

A self-hosted AI chat application that supports **any inference backend** via BYOK (Bring Your Own Key):

| Backend | Type | Config |
|---------|------|--------|
| **llama-cpp** | Local GGUF | `model_file` in config |
| **Ollama** | Local | `ollama` running locally |
| **vLLM** | Local | `vllm serve` running |
| **OpenAI** | API (paid) | `OPENAI_API_KEY` env var |
| **Anthropic** | API (paid) | `ANTHROPIC_API_KEY` env var |
| **Gemini** | API (free tier) | `GEMINI_API_KEY` env var |
| **OpenAI-compatible** | API (any) | Any LiteLLM/LM Studio/etc. |

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   FRONTEND                      │
│        Vite + React (dark theme chat UI)        │
└────────────────────┬────────────────────────────┘
                     │  HTTP + SSE
                     ▼
┌─────────────────────────────────────────────────┐
│                 BACKEND API                     │
│              FastAPI (Python)                   │
│  Routes: /chat /chat/stream /models /config     │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│              BYOK BACKEND SYSTEM                │
│  ┌───────────┐ ┌─────────┐ ┌─────────────────┐ │
│  │ llama-cpp │ │ ollama  │ │   openai/anthropic│
│  └───────────┘ └─────────┘ └─────────────────┘ │
│  ┌─────────┐ ┌───────┐ ┌────────────────────┐  │
│  │  vLLM   │ │ gemini│ │ openai_compatible  │  │
│  └─────────┘ └───────┘ └────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Configuration

All configuration lives in `config/`. **Zero hardcoded values.**

### server.config.json

```json
{
  "host": "0.0.0.0",
  "port": 8000,
  "log_level": "info",
  "cors_origins": ["http://localhost:5173"],
  "models_dir": "./models"
}
```

### model.config.json

```json
{
  "backend_type": "llama-cpp",
  "model_file": "mistral-7b-instruct.Q4_K_M.gguf",
  "chat_template": "auto",
  "context_length": 4096,
  "system_prompt": "You are a helpful assistant.",
  "generation": {
    "temperature": 0.7,
    "max_new_tokens": 512
  }
}
```

Set `backend_type` to any supported backend. For API backends, configure in `api_backends` section and set the corresponding API key environment variable.

---

## Model Detection

Models are auto-detected from GGUF metadata:

- Architecture (llama, mistral, phi, qwen, etc.)
- Chat template (auto-mapped from architecture)
- Context length
- Quantization level
- Parameter count

No manual configuration needed — drop a `.gguf` file in `models/` and it works.

---

## Chat Templates

Chat templates are auto-detected from:

1. **Model metadata** — GGUF files contain architecture info that maps to templates
2. **Conversation patterns** — the system detects `[INST]`, `<|im_start|>`, etc. from messages

Supported templates: `chatml`, `llama3`, `llama2`, `mistral`, `alpaca`, `raw`, or `auto`.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/status` | Health check, model state |
| `GET` | `/models` | List available model files |
| `GET` | `/models/detect` | Auto-detect model metadata |
| `GET` | `/config` | Get active configuration |
| `PUT` | `/config` | Update configuration |
| `GET` | `/config/backends` | List available backends |
| `POST` | `/chat` | Send message, get response |
| `POST` | `/chat/stream` | Stream response (SSE) |
| `GET` | `/conversations` | List conversations |
| `POST` | `/conversations` | Create conversation |
| `GET` | `/metrics` | Performance metrics |

---

## Directory Structure

```
local-ai-runtime/
├── local_ai_runtime/          # New CLI + config system
│   ├── cli.py                 # Entry point (uvx local-ai-runtime)
│   ├── config.py              # Config loader
│   └── server.py              # FastAPI app factory
├── backend/                   # API routes + services
│   ├── routes/                # FastAPI routers
│   ├── services/              # Business logic
│   ├── controllers/           # Request handlers
│   └── models/                # Data classes
├── model_runtime/             # Inference layer
│   ├── backends/              # BYOK adapter system
│   │   ├── base.py            # Abstract Backend interface
│   │   ├── registry.py        # Dynamic backend loading
│   │   ├── llama_cpp.py       # llama.cpp backend
│   │   ├── ollama.py          # Ollama backend
│   │   ├── vllm.py            # vLLM backend
│   │   ├── openai_backend.py  # OpenAI API
│   │   ├── anthropic_backend.py # Anthropic API
│   │   ├── gemini_backend.py  # Google Gemini
│   │   └── openai_compatible.py # Any OpenAI-compatible
│   ├── detector.py            # GGUF metadata detection
│   ├── chat_template_auto.py  # Auto chat template
│   ├── prompt_formatter.py    # Template formatting
│   └── inference_engine.py    # Legacy engine wrapper
├── frontend/                  # Vite + React UI
│   ├── app.jsx                # Root component
│   ├── components/            # ChatWindow, InputBar, ModelSelector
│   └── styles/                # Dark theme CSS
├── config/                    # JSON config files
├── models/                    # GGUF files (gitignored)
├── huggingface/               # HF download support
├── pyproject.toml             # uv project config
└── .python-version            # Python 3.12
```

---

## Requirements

- Python 3.11+
- Node.js 18+ (for frontend)
- uv (package manager)
- For local inference: llama-cpp-python, ollama, or vllm
- For API inference: API keys as environment variables
