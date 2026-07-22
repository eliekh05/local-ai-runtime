"""
Applies model-specific chat template formatting to a conversation history.
Supports: chatml, llama3, llama2, mistral, alpaca, raw
"""

TEMPLATE_CHATML = "chatml"
TEMPLATE_LLAMA3 = "llama3"
TEMPLATE_LLAMA2 = "llama2"
TEMPLATE_MISTRAL = "mistral"
TEMPLATE_ALPACA = "alpaca"
TEMPLATE_RAW = "raw"


class PromptFormatterError(Exception):
    pass


def format_prompt(messages: list, template: str, add_generation_prompt: bool = True) -> str:
    if not messages:
        raise PromptFormatterError("Cannot format an empty message list.")
    _formatters = {
        TEMPLATE_CHATML: _format_chatml,
        TEMPLATE_LLAMA3: _format_llama3,
        TEMPLATE_LLAMA2: _format_llama2,
        TEMPLATE_MISTRAL: _format_mistral,
        TEMPLATE_ALPACA: _format_alpaca,
        TEMPLATE_RAW: _format_raw,
    }
    formatter = _formatters.get(template)
    if formatter is None:
        supported = ", ".join(sorted(_formatters.keys()))
        raise PromptFormatterError(f"Unknown template: '{template}'. Supported: {supported}")
    return formatter(messages, add_generation_prompt)


def _get_content(msg) -> str:
    return msg.content if hasattr(msg, "content") else str(msg)


def _get_role(msg) -> str:
    if hasattr(msg, "role"):
        return msg.role.value if hasattr(msg.role, "value") else str(msg.role)
    return str(getattr(msg, "role", "user"))


def _format_chatml(messages: list, add_generation_prompt: bool) -> str:
    """ChatML: <|start|>role\ncontent<|end|>"""
    parts = []
    for msg in messages:
        role = _get_role(msg)
        content = _get_content(msg)
        parts.append(f"<|start|>{role}\n{content}<|end|>")
    if add_generation_prompt:
        parts.append("<|start|>assistant\n")
    return "\n".join(parts)


def _format_llama3(messages: list, add_generation_prompt: bool) -> str:
    """Llama 3: <|begin_of_text|><|start_header_id|>role<|end_header_id|>\n\ncontent<|eot_id|>"""
    parts = ["<|begin_of_text|>"]
    for msg in messages:
        role = _get_role(msg)
        content = _get_content(msg)
        parts.append(f"<|start_header_id|>{role}<|end_header_id|>\n\n{content}<|eot_id|>")
    if add_generation_prompt:
        parts.append("<|start_header_id|>assistant<|end_header_id|>\n\n")
    return "".join(parts)


def _format_llama2(messages: list, add_generation_prompt: bool) -> str:
    """Llama 2: <s>[INST] <<SYS>>\nsys\n<</SYS>>\n\nuser [/INST] assistant </s>"""
    system_parts = []
    user_parts = []
    assistant_parts = []
    for msg in messages:
        role = _get_role(msg)
        content = _get_content(msg)
        if role == "system":
            system_parts.append(content)
        elif role == "user":
            user_parts.append(content)
        elif role == "assistant":
            assistant_parts.append(content)

    sys_block = ""
    if system_parts:
        sys_block = "<<SYS>>\n" + "\n".join(system_parts) + "\n<</SYS>>\n\n"

    parts = []
    for i, user_msg in enumerate(user_parts):
        inst = f"<s>[INST] {sys_block}{user_msg} [/INST]"
        if i < len(assistant_parts):
            inst += f" {assistant_parts[i]} </s>"
        parts.append(inst)

    if add_generation_prompt:
        parts.append("<s>[INST] ")
    return "".join(parts)


def _format_mistral(messages: list, add_generation_prompt: bool) -> str:
    """Mistral: <s>[INST] content [/INST]"""
    system_content = ""
    conversation = []
    for msg in messages:
        role = _get_role(msg)
        content = _get_content(msg)
        if role == "system":
            system_content = content
        else:
            conversation.append((role, content))

    parts = []
    first_user = True
    for role, content in conversation:
        if role == "user":
            prefix = ""
            if first_user and system_content:
                prefix = system_content + "\n\n"
            parts.append(f"<s>[INST] {prefix}{content} [/INST]")
            first_user = False
        elif role == "assistant":
            parts.append(f" {content}</s>")

    if add_generation_prompt:
        parts.append("<s>[INST] ")
    return "".join(parts)


def _format_alpaca(messages: list, add_generation_prompt: bool) -> str:
    """Alpaca: ### Instruction:\ncontent\n\n### Response:"""
    parts = []
    for msg in messages:
        role = _get_role(msg)
        content = _get_content(msg)
        if role == "system":
            parts.append(content)
        elif role == "user":
            parts.append(f"### Instruction:\n{content}\n")
        elif role == "assistant":
            parts.append(f"### Response:\n{content}\n")
    if add_generation_prompt:
        parts.append("### Response:\n")
    return "\n".join(parts)


def _format_raw(messages: list, add_generation_prompt: bool) -> str:
    """Raw passthrough."""
    return "\n".join(_get_content(msg) for msg in messages)
