# docs/model_compatibility.md
#
# Tested Model Compatibility Notes
#
# STATUS: EMPTY — No models have been tested yet.
#
# When you test a model, add an entry here.
# This is a living document maintained by hand.
#
# Format for each entry:
#
#   ## [Model Name] — [Quantization]
#   - **File**: filename.gguf
#   - **Source**: HuggingFace URL
#   - **Tested on**: [hardware description]
#   - **Chat template**: [which template worked]
#   - **Context length used**: [value]
#   - **Inference speed**: [tokens/sec approx]
#   - **RAM used**: [approx GB]
#   - **Notes**: [any quirks, caveats, best settings]
#   - **Project version when tested**: [version from repo_metadata.py]
#
# -------------------------------------------------------------------------
# TESTED MODELS
# -------------------------------------------------------------------------
#
# (none yet — add entries as you test models)
#
# -------------------------------------------------------------------------
# KNOWN INCOMPATIBLE / UNTESTED
# -------------------------------------------------------------------------
#
# - Models requiring custom CUDA kernels not in llama.cpp
# - Models in formats other than GGUF (e.g. AWQ, GPTQ, EXL2)
#   These require different runtimes and are out of scope for now.
