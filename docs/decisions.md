# docs/decisions.md — Architecture Decision Log

This document records significant design decisions made during the project.
Each entry explains what was decided, why, and what alternatives were considered.

Add a new entry whenever a meaningful decision is made that future developers
should understand the reasoning behind.

---

## ADR-001: Python as primary backend language (PENDING)

**Status:** Not yet decided  
**Date:** TBD  

**Decision:** [TBD — choose Python or Node.js]

**Options considered:**
- Python with FastAPI
  - Pro: llama-cpp-python binding is mature and well-documented
  - Pro: Strong ecosystem for AI/ML adjacent tooling
  - Con: Slightly more complex async handling
- Node.js with Express/Fastify
  - Pro: Same language as frontend (React)
  - Pro: Simpler async model (native promises)
  - Con: llama.cpp Node bindings are less mature
  - Con: More complex to integrate Python-adjacent model tooling

**Decision criteria:** Which binding to llama.cpp is more reliable and
better maintained at the time this decision is made.

---

## ADR-002: GGUF as the exclusive model format (DECIDED)

**Status:** Decided — initial scaffold  
**Date:** 2025  

**Decision:** The system is designed exclusively around GGUF format models.
No support for HuggingFace `.safetensors`, GPTQ, AWQ, or other formats
is planned in the initial phases.

**Rationale:**
- GGUF is the standard for llama.cpp, the most widely supported local inference runtime
- GGUF files are self-contained (tokenizer embedded)
- GGUF supports CPU inference without requiring a GPU
- Most popular open-weight models have GGUF versions available
- Adding other formats later is possible by extending the model_loader abstraction

**Alternatives considered:**
- Supporting Hugging Face Transformers directly: rejected because it requires
  a full Python + PyTorch stack, much higher RAM requirements, and is not
  practical for CPU inference on consumer hardware.

---

## ADR-003: No external AI API dependencies (DECIDED)

**Status:** Decided — initial scaffold  
**Date:** 2025  

**Decision:** The system must never call any external AI inference API.
All inference is local.

**Rationale:**
- The entire purpose of this project is local, private AI inference
- External API calls would defeat that purpose and add internet dependency
- No API keys, no rate limits, no privacy concerns

**This decision is non-negotiable and should not be revisited.**

---

## ADR-004: Chat template format handling (DECIDED — design only)

**Status:** Decided in design, not yet implemented  
**Date:** 2025  

**Decision:** Chat template formatting is handled by a dedicated
`prompt_formatter` module in `model_runtime/`, not inline in the service layer.

**Rationale:**
- Different models require different prompt formats
- Centralizing this logic makes it testable in isolation (no model needed)
- New template formats can be added without touching the inference logic
- The formatter can be unit tested with simple string comparisons

---

## ADR-005: Configuration file format (PENDING)

**Status:** Not yet decided  
**Date:** TBD  

**Decision:** [TBD — choose JSON, TOML, or YAML]

**Options:**
- JSON: Simple, no extra library needed, but no comments allowed
- TOML: Human-friendly, comments allowed, small stdlib module in Python 3.11+
- YAML: Very human-friendly but has parsing footguns

**Current state:** Example files use JSON with `_comment` keys as a workaround.
This should be revisited once the config system is being implemented.

---

*Add new ADR entries here as decisions are made.*
