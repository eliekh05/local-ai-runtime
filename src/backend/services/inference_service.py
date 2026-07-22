"""
Service layer between controllers and the BYOK backend system.
Routes requests to the correct backend based on config.
"""

from typing import Generator

from model_runtime.backends import get_backend, BackendError
from model_runtime.chat_template_auto import auto_detect_template
from backend.services.model_service import get_active_config


class InferenceError(Exception):
    pass


class InferenceResult:
    def __init__(self, content: str, model_name: str, tokens_used: int,
                 finish_reason: str = "stop", backend: str = ""):
        self.content = content
        self.model_name = model_name
        self.tokens_used = tokens_used
        self.finish_reason = finish_reason
        self.backend = backend


def _build_messages(message, conversation_history=None, config=None) -> list[dict]:
    """Build OpenAI-format message list from ChatMessage objects."""
    messages = []
    if config and config.get("system_prompt"):
        messages.append({"role": "system", "content": config["system_prompt"]})
    if conversation_history:
        for msg in conversation_history:
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            messages.append({"role": role, "content": msg.content})
    role = message.role.value if hasattr(message.role, "value") else str(message.role)
    messages.append({"role": role, "content": message.content})
    return messages


def _get_backend_and_config():
    """Get the active backend and config."""
    config = get_active_config()
    if not config:
        raise InferenceError("No active model configuration. Set one via PUT /config.")

    config_dict = config.to_dict() if hasattr(config, "to_dict") else dict(config)
    backend_type = config_dict.get("backend_type", "llama-cpp")
    api_backends = config_dict.get("api_backends", {}) or {}
    backend_config = dict(api_backends.get(backend_type, {}))

    if backend_type == "llama-cpp":
        backend_config["models_dir"] = config_dict.get("models_dir", "./models")
    elif backend_type == "openai_compatible":
        if config_dict.get("compatible_base_url"):
            backend_config["base_url"] = config_dict["compatible_base_url"]
        if config_dict.get("compatible_model"):
            backend_config["model"] = config_dict["compatible_model"]

    return backend_type, backend_config, config_dict


def _prepare_model_config(backend_type: str, config_dict: dict) -> dict:
    """Ensure provider-specific model fields are populated for backends."""
    prepared = dict(config_dict)
    model_file = prepared.get("model_file", "")

    if backend_type == "llama-cpp":
        prepared["model_file"] = model_file
        prepared["models_dir"] = prepared.get("models_dir", "./models")
    elif backend_type == "ollama":
        prepared["ollama_model"] = prepared.get("ollama_model") or model_file
    elif backend_type == "vllm":
        prepared["vllm_model"] = prepared.get("vllm_model") or model_file
    elif backend_type == "openai":
        prepared["openai_model"] = prepared.get("openai_model") or model_file
    elif backend_type == "anthropic":
        prepared["anthropic_model"] = prepared.get("anthropic_model") or model_file
    elif backend_type == "gemini":
        prepared["gemini_model"] = prepared.get("gemini_model") or model_file
    elif backend_type == "openai_compatible":
        prepared["compatible_model"] = prepared.get("compatible_model") or model_file
        prepared["compatible_base_url"] = (
            prepared.get("compatible_base_url")
            or (prepared.get("api_backends") or {}).get("openai_compatible", {}).get("base_url", "")
        )

    return prepared


async def generate_response(message, conversation_id=None, conversation_history=None) -> InferenceResult:
    """Generate a response using the configured BYOK backend."""
    try:
        backend_type, backend_config, config_dict = _get_backend_and_config()
    except InferenceError:
        raise
    except Exception as e:
        raise InferenceError(f"Failed to load config: {e}")

    model_config = _prepare_model_config(backend_type, config_dict)

    try:
        backend = get_backend(backend_type, config=backend_config)
    except ValueError as e:
        raise InferenceError(str(e))

    if not backend.is_available():
        raise InferenceError(f"Backend '{backend_type}' is not available.")

    try:
        backend.load_model(model_config)
    except BackendError as e:
        raise InferenceError(f"Failed to load model: {e}")

    messages = _build_messages(message, conversation_history, config_dict)

    template = config_dict.get("chat_template", "chatml")
    if template == "auto":
        template = auto_detect_template(messages)

    gen_params = dict(config_dict.get("generation", {}) or {})
    gen_params["chat_template"] = template

    try:
        result = backend.generate(messages, params=gen_params)
        return InferenceResult(
            content=result.text,
            model_name=model_config.get("model_file") or backend_type,
            tokens_used=result.total_tokens,
            finish_reason=result.finish_reason,
            backend=result.backend,
        )
    except BackendError as e:
        raise InferenceError(f"Inference failed: {e}")


def generate_stream_response(message, conversation_history=None) -> Generator[str, None, None]:
    """Stream tokens from the configured BYOK backend."""
    try:
        backend_type, backend_config, config_dict = _get_backend_and_config()
    except InferenceError:
        yield "[Error: No config loaded]"
        return

    model_config = _prepare_model_config(backend_type, config_dict)

    try:
        backend = get_backend(backend_type, config=backend_config)
    except ValueError as e:
        yield f"[Error: {e}]"
        return

    if not backend.is_available():
        yield f"[Error: Backend '{backend_type}' not available]"
        return

    try:
        backend.load_model(model_config)
    except BackendError as e:
        yield f"[Error: {e}]"
        return

    messages = _build_messages(message, conversation_history, config_dict)

    template = config_dict.get("chat_template", "chatml")
    if template == "auto":
        template = auto_detect_template(messages)

    gen_params = dict(config_dict.get("generation", {}) or {})
    gen_params["chat_template"] = template

    try:
        yield from backend.generate_stream(messages, params=gen_params)
    except BackendError as e:
        yield f"\n[Error: {e}]"
