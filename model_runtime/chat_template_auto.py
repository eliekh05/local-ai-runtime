"""
Auto-generate chat template names from conversation patterns.
No manual selection needed — detects the format from the messages themselves.
"""

import re


def auto_detect_template(messages: list[dict]) -> str:
    """
    Analyze conversation messages and detect which chat template format
    is being used based on patterns in the content.

    Returns template name: 'chatml', 'llama3', 'llama2', 'mistral', 'alpaca', 'raw'
    """
    if not messages:
        return "chatml"

    # Check for explicit template markers in any message content
    for msg in messages:
        content = msg.get("content", "")

        if "<|start_header_id|>" in content or "<|end_header_id|>" in content:
            return "llama3"
        if "<|start|>" in content and "<|end|>" in content:
            return "chatml"
        if "[INST]" in content and "[/INST]" in content:
            if "<<SYS>>" in content:
                return "llama2"
            return "mistral"
        if "### Instruction:" in content or "### Response:" in content:
            return "alpaca"

    # Check for system message patterns
    for msg in messages:
        if msg.get("role") == "system":
            content = msg.get("content", "")
            # If system message is plain text without special tokens, likely chatml or raw
            if not any(marker in content for marker in ["<|", "[INST]", "###"]):
                continue

    # Default to chatml (most universal)
    return "chatml"


def get_template_display_name(template: str) -> str:
    """Human-readable name for a template."""
    names = {
        "chatml": "ChatML (Mistral, Phi-3, Qwen)",
        "llama3": "Llama 3 (Meta)",
        "llama2": "Llama 2 (Meta)",
        "mistral": "Mistral Instruct",
        "alpaca": "Alpaca",
        "raw": "Raw (no template)",
    }
    return names.get(template, template)


def get_template_for_model(architecture: str) -> str:
    """Get the recommended template for a detected architecture."""
    arch_lower = architecture.lower()
    mapping = {
        "llama": "llama3",
        "mistral": "mistral",
        "mixtral": "mistral",
        "phi": "chatml",
        "qwen": "chatml",
        "gemma": "chatml",
        "command-r": "chatml",
        "deepseek": "chatml",
        "codellama": "llama3",
        "falcon": "chatml",
        "yi": "chatml",
    }
    for key, template in mapping.items():
        if key in arch_lower:
            return template
    return "chatml"
