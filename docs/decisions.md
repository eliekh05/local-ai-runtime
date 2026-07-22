# Architecture Decision Log

---

## ADR-001: Python (FastAPI) as backend

**Status:** Decided  
**Date:** 2025

**Decision:** Python with FastAPI.

**Rationale:** Mature llama-cpp-python binding, strong AI/ML ecosystem, async support via uvicorn.

---

## ADR-002: Vite for frontend

**Status:** Decided  
**Date:** 2025

**Decision:** Vite + React, not CRA.

**Rationale:** Faster dev server, smaller bundle, ESM-native. CRA is deprecated.

---

## ADR-003: GGUF as exclusive local model format

**Status:** Decided  
**Date:** 2025

**Decision:** GGUF only for local inference. No safetensors/GPTQ/AWQ.

**Rationale:** Standard for llama.cpp, self-contained tokenizer, CPU-friendly.

---

## ADR-004: BYOK hybrid — all backends

**Status:** Decided  
**Date:** 2025

**Decision:** Support 7 backends: llama-cpp, ollama, vLLM, OpenAI, Anthropic, Gemini, OpenAI-compatible.

**Rationale:** Users want local privacy AND access to paid/free APIs. One app, any model source.

---

## ADR-005: JSON config format

**Status:** Decided  
**Date:** 2025

**Decision:** JSON for all config. Zero hardcoded values.

**Rationale:** Universal, no extra deps, easy to parse. Config files: `server.config.json`, `model.config.json`.

---

## ADR-006: Auto chat templates

**Status:** Decided  
**Date:** 2025

**Decision:** Chat templates auto-detected from GGUF metadata (architecture mapping) and conversation patterns (`[INST]`, `<|im_start|>`, etc.). Default: `auto`.

**Rationale:** Eliminates manual config. Users don't need to know which template their model uses.

---

## ADR-007: uv package manager

**Status:** Decided  
**Date:** 2025

**Decision:** Use uv, not pip. pyproject.toml with `dependency-groups` (not deprecated `tool.uv.dev-dependencies`).

**Rationale:** 10-100x faster installs, Astral-backed, native Python version management.

---

## ADR-008: src-layout for packaging

**Status:** Decided  
**Date:** 2025

**Decision:** `src/` layout for `uv build`. Packages under `src/local_ai_runtime`, `src/model_runtime`, `src/backend`.

**Rationale:** Prevents accidental import of uninstalled packages. Standard Python packaging best practice.

---

## ADR-009: SSE for streaming

**Status:** Decided  
**Date:** 2025

**Decision:** Server-Sent Events (SSE) at `/chat/stream`, not WebSocket.

**Rationale:** Simpler protocol, works with all backends, no WS upgrade needed, native `EventSource` in browsers.

---

## ADR-010: macOS brew detection

**Status:** Decided  
**Date:** 2025

**Decision:** On macOS, `uvx local-ai-runtime` detects uvx and recommends `brew install` instead.

**Rationale:** Homebrew gives better native Apple Silicon support. uvx is a fallback.
