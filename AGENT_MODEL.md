# AGENT_MODEL.md — Conceptual Model Specification

> **STATUS: ABSTRACT CONCEPT DOCUMENT**
>
> This document describes the conceptual specification for the AI model(s) that
> will be used in this system. It is not a technical specification for a specific
> model, and it does not correspond to any currently loaded or configured model.
>
> It exists to give developers shared vocabulary when discussing model behavior,
> configuration, and integration. Fill in the bracketed fields as decisions are made.

---

## 1. Model Identity

| Field | Value | Notes |
|---|---|---|
| Model Name | `[TO BE DEFINED]` | e.g. "Mistral-7B-Instruct-v0.3" |
| Model Family | `[UNKNOWN / FUTURE DESIGN]` | e.g. LLaMA, Mistral, Phi, Gemma |
| Parameter Count | `[TBD]` | e.g. 3B, 7B, 13B |
| Base Model | `[TBD]` | The foundation model before instruction tuning |
| Instruction Tuned? | `[TBD]` | Yes / No |
| Source | `[TBD]` | e.g. HuggingFace hub URL |
| License | `[TBD]` | e.g. MIT, Llama Community License, Apache 2.0 |

---

## 2. GGUF File Specification

| Field | Value | Notes |
|---|---|---|
| File Name | `[TBD]` | e.g. `model-7b-q4_k_m.gguf` |
| Quantization | `[TBD]` | GGUF variants supported (Q4_K_M, Q5_K_M, Q8_0, F16…) |
| File Size | `[TBD]` | Approximate size on disk |
| Embedded Tokenizer | `[TBD]` | Most GGUF files include tokenizer; confirm |
| Source URL | `[TBD]` | Where to download this file |
| SHA256 Checksum | `[TBD]` | For integrity verification after download |

### About Quantization Options

GGUF models are distributed at multiple quantization levels. The trade-offs:

| Quant Level | Size (7B) | Quality | Speed | RAM Needed |
|---|---|---|---|---|
| Q2_K | ~2.5 GB | Poor | Fastest | ~3.5 GB |
| Q4_0 | ~3.8 GB | Acceptable | Fast | ~5 GB |
| Q4_K_M | ~4.1 GB | Good | Fast | ~5.5 GB |
| Q5_K_M | ~4.8 GB | Very Good | Moderate | ~6 GB |
| Q8_0 | ~7.2 GB | Near-lossless | Slower | ~9 GB |
| F16 | ~14 GB | Lossless | Slow | ~16 GB |

**Recommendation:** Start with Q4_K_M for general use. Use Q5_K_M or Q8_0 if
quality is noticeably insufficient.

---

## 3. Architecture Details

> These fields describe the model's transformer architecture. They matter for
> advanced configuration but are not required to run basic inference.

| Field | Value | Notes |
|---|---|---|
| Architecture Family | `[UNKNOWN]` | e.g. LLaMA, Mistral, Falcon, Phi |
| Attention Mechanism | `[UNKNOWN]` | e.g. Multi-Head, Grouped-Query, Multi-Query |
| Number of Layers | `[TBD]` | e.g. 32 for most 7B models |
| Hidden Dimension | `[TBD]` | e.g. 4096 |
| Number of Attention Heads | `[TBD]` | e.g. 32 |
| Vocabulary Size | `[TBD]` | e.g. 32000, 128256 |
| Positional Encoding | `[TBD]` | e.g. RoPE, ALiBi |
| Activation Function | `[TBD]` | e.g. SwiGLU, GELU |

---

## 4. Context Window

| Field | Value | Notes |
|---|---|---|
| Maximum Context Length | `[TBD]` | In tokens — check model card |
| Practical Context Length | `[TBD]` | Lower limit for reliable behavior |
| Recommended Chat Context | `[TBD]` | How many tokens to keep in history |
| Context Overflow Strategy | `[NOT IMPLEMENTED]` | Truncate / Summarize / Sliding window |

**Important:** The context length in the GGUF file is the hard maximum. The
inference engine must be initialized with this value. Exceeding it causes
undefined behavior (corruption or crash, not a graceful error).

---

## 5. Tokenizer

| Field | Value | Notes |
|---|---|---|
| Tokenizer Type | `[TBD]` | e.g. BPE, Unigram, SentencePiece |
| Vocab File Embedded? | `[TBD]` | GGUF usually embeds tokenizer |
| Special Tokens | `[TBD]` | BOS, EOS, PAD, UNK token IDs |
| BOS Token | `[TBD]` | e.g. `<s>`, `<|begin_of_text|>` |
| EOS Token | `[TBD]` | e.g. `</s>`, `<|eot_id|>`, `<|im_end|>` |
| Pad Token | `[TBD]` | May be same as EOS or undefined |

---

## 6. Chat Template (CRITICAL)

> Using the wrong chat template with a model produces nonsensical or degraded
> output. This is one of the most common configuration mistakes.

| Field | Value | Notes |
|---|---|---|
| Template Format | `[TBD]` | See options below |
| System Prompt Support | `[TBD]` | Some models ignore system prompts |
| Tool Call Format | `[NOT IMPLEMENTED]` | For future plugin/tool use |

### Supported Template Formats

**ChatML** (used by many models including Phi-3, Mistral, Qwen):

```
<|im_start|>system
{system_prompt}<|im_end|>
<|im_start|>user
{user_message}<|im_end|>
<|im_start|>assistant
{assistant_response}<|im_end|>
```

**Llama 3** (used by Meta Llama 3.x):

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{assistant_response}<|eot_id|>
```

**Mistral** (used by Mistral v0.1/v0.2 instruct):

```
<s>[INST] {user_message} [/INST]{assistant_response}</s>[INST] {next_message} [/INST]
```

*Note: Original Mistral format does not support system prompts in the same way.*

**Llama 2** (used by older Meta Llama 2 chat models):

```
<s>[INST] <<SYS>>
{system_prompt}
<</SYS>>

{user_message} [/INST] {assistant_response} </s><s>[INST] {next_message} [/INST]
```

**Alpaca** (older instruction-following format):

```
### Instruction:
{user_message}

### Response:
{assistant_response}
```

> **Rule:** The `prompt_formatter` module must implement ALL of these. When
> in doubt about which template a model uses, check the model card on Hugging
> Face or look for a `tokenizer_config.json` in the source repository.

---

## 7. Default System Prompt

> The system prompt sets the model's behavior and persona. It consumes tokens
> from the context window, so keep it concise.

```
[TO BE DEFINED]

Placeholder concept:
"You are a helpful, harmless, and honest assistant running locally on the user's
machine. You have no access to the internet, real-time data, or external tools
unless explicitly provided. Be concise and accurate."
```

**Note:** Some models respond better to a minimal system prompt or no system
prompt at all. This should be configurable per model profile.

---

## 8. Default Generation Parameters

> These are starting-point defaults. They should be tunable per request and
> per model profile.

| Parameter | Placeholder Default | Range | Notes |
|---|---|---|---|
| Temperature | `0.7` | 0.0 – 2.0 | Lower = more deterministic |
| Top-P | `0.9` | 0.0 – 1.0 | Nucleus sampling |
| Top-K | `40` | 0 – ∞ | 0 = disabled |
| Repeat Penalty | `1.1` | 1.0 – 2.0 | Penalizes token repetition |
| Max New Tokens | `512` | 1 – context_length | Hard output length limit |
| Min New Tokens | `1` | 0 – max_new_tokens | Optional minimum output |
| Seed | `-1` | -1 = random | Set for reproducibility |

---

## 9. Safety Layer

> **STATUS: CONCEPT ONLY — NOT IMPLEMENTED**

A safety layer would inspect or filter model inputs and/or outputs. Options:

| Approach | Description | Status |
|---|---|---|
| None | Pass through everything | Default (current) |
| Keyword filter | Block specific terms in input or output | Not implemented |
| Classifier-based | Run a small classifier on output | Not implemented |
| Constitutional AI | Use the model itself to self-critique | Not implemented |
| External moderation | Call an external API | Explicitly excluded (no external APIs) |

**Decision:** Safety filtering is out of scope for this project phase. It may
be added as a plugin in Phase 4. The model runs without guardrails by default.
Users are responsible for model behavior on their own hardware.

---

## 10. Reasoning Module

> **STATUS: CONCEPT ONLY — NOT IMPLEMENTED**

Some models support structured reasoning before providing a final answer (e.g.
chain-of-thought, scratchpad reasoning, "thinking" modes).

| Field | Value | Notes |
|---|---|---|
| Reasoning Support | `[UNKNOWN — model dependent]` | Check model card |
| Reasoning Format | `[TBD]` | e.g. `<think>...</think>` tags |
| Reasoning Token Budget | `[TBD]` | How many tokens to allow for reasoning |
| Expose Reasoning in UI | `[TBD]` | Show or hide reasoning steps |

---

## 11. Known Limitations

> Fill this in as model-specific quirks are discovered during testing.

| Limitation | Description | Workaround |
|---|---|---|
| `[TBD]` | `[TBD]` | `[TBD]` |

---

## 12. Model Profile JSON (Future Format)

This is the intended structure for a model profile config file.
**Not yet parsed or used by any code.**

```json
{
  "profile_name": "[TO BE DEFINED]",
  "model_file": "[TBD].gguf",
  "architecture": "[TBD]",
  "chat_template": "[TBD]",
  "context_length": 4096,
  "system_prompt": "[TO BE DEFINED]",
  "generation_defaults": {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 40,
    "repeat_penalty": 1.1,
    "max_new_tokens": 512,
    "seed": -1
  },
  "tokenizer": {
    "embedded_in_gguf": true,
    "bos_token": "[TBD]",
    "eos_token": "[TBD]"
  },
  "notes": ""
}
```

---

*This document should be updated whenever a real model is chosen and tested.*
*It is a living specification, not a frozen contract.*
