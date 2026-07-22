# SETUP_TEMPLATE.md

> ⚠️ **STATUS: INCOMPLETE — DO NOT FOLLOW YET**
>
> This document is a placeholder setup guide. It describes the *intended* setup
> process for a future working state of the project. None of these commands will
> work until the corresponding Phase 1 and Phase 2 development is complete.
>
> When this document is updated to reflect a working system, this warning block
> should be removed or replaced with a version number and date.

---

## System Requirements

> TODO: Finalize these requirements once language choice (Python vs Node) is made.

### Minimum (CPU-only inference)

| Requirement | Minimum | Notes |
|---|---|---|
| Operating System | Linux, macOS, or Windows (WSL2) | Native Windows may work but is untested |
| RAM | 8 GB | Sufficient for 3B-4B parameter GGUF models |
| Disk Space | 20 GB free | Models are 2–8 GB each |
| CPU | x86_64 with AVX2 | Check: `grep avx2 /proc/cpuinfo` on Linux |
| Python | 3.10+ | If using Python backend |
| Node.js | 18+ | If using Node.js backend |
| Git | Any recent version | For cloning |

### Recommended (GPU-accelerated inference)

| Requirement | Recommended | Notes |
|---|---|---|
| RAM | 16 GB+ | Allows 7B+ parameter models |
| GPU | NVIDIA with 8GB+ VRAM | For CUDA offloading |
| GPU (Apple) | M1/M2/M3 | Metal acceleration works well |
| Disk Space | 50 GB free | Multiple models |

---

## Step 0: Clone the Repository

```bash
git clone https://github.com/[USERNAME]/local-ai-runtime.git
cd local-ai-runtime
```

---

## Step 1: Install Backend Dependencies

> ⚠️ NOT YET DEFINED — language choice is pending.

**If Python (FastAPI):**

```bash
# TODO: Create requirements.txt first
pip install -r requirements.txt
```

**Future Python dependencies (not yet in requirements.txt):**

```
fastapi
uvicorn[standard]
pydantic
llama-cpp-python    # requires llama.cpp build step first
```

**If Node.js (Express):**

```bash
# TODO: Create package.json first
npm install
```

**Future Node dependencies (not yet in package.json):**

```
express
cors
dotenv
node-llama-cpp    # conceptual; binding may differ
```

---

## Step 2: Build llama.cpp (NOT YET INTEGRATED)

> llama.cpp must be compiled separately. This step documents the intended process.

```bash
# Clone llama.cpp into a sibling directory (NOT inside this repo)
cd ..
git clone https://github.com/ggerganov/llama.cpp.git
cd llama.cpp

# Build — CPU only
make

# Build — with CUDA support (NVIDIA GPU)
# make LLAMA_CUDA=1

# Build — with Metal support (Apple Silicon)
# make LLAMA_METAL=1

cd ../local-ai-runtime
```

> TODO: Decide whether to vendor llama.cpp as a submodule or treat it as an
> external dependency. Document this decision in a commit message and here.

---

## Step 3: Obtain a GGUF Model

> Models are NOT included in this repository. You must obtain one separately.

**Recommended sources:**

- [TheBloke on Hugging Face](https://huggingface.co/TheBloke) — large collection
  of GGUF quantized models
- [bartowski on Hugging Face](https://huggingface.co/bartowski) — recent models
- Model authors who publish GGUF variants directly

**Recommended starter models (small enough for CPU-only testing):**

| Model | Size (Q4_K_M) | Context | Notes |
|---|---|---|---|
| Phi-3 Mini 3.8B | ~2.2 GB | 4K–128K | Fast, good quality for size |
| Mistral 7B Instruct v0.3 | ~4.1 GB | 32K | Solid all-around choice |
| Llama 3.2 3B | ~1.9 GB | 128K | Meta's efficient small model |

**Place the model file here:**

```
local-ai-runtime/
└── models/
    └── your-model-name.gguf    ← Put it here
```

> The `models/` directory is gitignored. Model files will never be committed.

---

## Step 4: Configure the Model Profile

> ⚠️ Configuration system NOT YET IMPLEMENTED.

```bash
# Copy the example config
cp config/model.config.example.json config/model.config.json

# Edit the config to point to your model file
# nano config/model.config.json
```

**Example model.config.json (future format):**

```json
{
  "active_model": "your-model-name.gguf",
  "models_dir": "./models/",
  "chat_template": "chatml",
  "context_length": 4096,
  "system_prompt": "You are a helpful assistant.",
  "generation": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "max_tokens": 512
  }
}
```

> TODO: Define valid values for `chat_template`. See `model_runtime/prompt_formatter.*`
> for the list of supported template names.

---

## Step 5: Configure the Server

> ⚠️ Configuration system NOT YET IMPLEMENTED.

```bash
cp config/server.config.example.json config/server.config.json
```

**Example server.config.json (future format):**

```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "debug": true,
  "cors_origins": ["http://localhost:3000"]
}
```

> Note: All defaults are localhost only. This system is not designed to be
> exposed to the internet.

---

## Step 6: Start the Backend

> ⚠️ NOT YET IMPLEMENTED.

**Python:**

```bash
# From the project root
python backend/server.py

# Expected output (future state):
# INFO: Starting local-ai-runtime backend
# INFO: Model not loaded (no model configured)
# INFO: Listening on http://127.0.0.1:8000
```

**Node.js:**

```bash
node backend/server.js
```

**Verify it works:**

```bash
curl http://localhost:8000/status
# Expected: {"status":"ok","model_loaded":false,"version":"0.0.1"}
```

---

## Step 7: Start the Frontend

> ⚠️ NOT YET IMPLEMENTED.

```bash
cd frontend
# npm run dev   (once package.json exists)
```

**Expected URL:** `http://localhost:3000`

---

## Verification Checklist

Once both steps 6 and 7 are implemented and working:

- [ ] `GET /status` returns `{"status":"ok"}`
- [ ] `GET /models` returns list of `.gguf` files in `models/`
- [ ] Frontend loads at `localhost:3000` without errors
- [ ] Typing a message and sending reaches the backend (check server logs)
- [ ] A response (even a fake placeholder) appears in the UI

---

## Troubleshooting

> TODO: Fill this section as real problems are encountered during development.

**Common anticipated issues:**

| Problem | Likely Cause | Resolution |
|---|---|---|
| `ModuleNotFoundError` | Dependencies not installed | Run install step |
| `FileNotFoundError` on model | Wrong path in config | Check `models_dir` in config |
| Out of memory | Model too large for RAM | Use smaller quantization (Q4 vs Q8) |
| Garbled model output | Wrong chat template | Check `chat_template` in model config |
| Frontend can't reach backend | CORS misconfigured | Check `cors_origins` in server config |
| Slow inference | CPU-only, no GPU offload | Expected; adjust `max_tokens` |

---

*This document will be updated to reflect reality as the project develops.*
*When you update it, remove the ⚠️ warning at the top and add a last-updated date.*
