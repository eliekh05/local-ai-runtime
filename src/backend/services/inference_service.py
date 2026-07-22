"""
Service layer between controllers and the BYOK backend system.
Routes requests to the correct backend based on config.
"""

import sys
from pathlib import Path
from typing import Generator

# Ensure project root is on sys.path
_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from model_runtime.backends import get_backend, BackendError
from model_runtime.chat_template_auto import auto_detect_template
from models.chat_message import ChatMessage, Role
from services.model_service import get_active_config


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

    # System prompt from config
    if config and config.get("system_prompt"):
        messages.append({"role": "system", "content": config["system_prompt"]})

    # Conversation history
    if conversation_history:
        for msg in conversation_history:
            role = msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            messages.append({"role": role, "content": msg.content})

    # Current user message
    role = message.role.value if hasattr(message.role, "value") else str(message.role)
    messages.append({"role": role, "content": message.content})

    return messages


def _get_backend_and_config():
    """Get the active backend and config."""
    config = get_active_config()
    if not config:
        raise InferenceError("No active model configuration. Set one via PUT /config.")

    config_dict = config.to_dict() if hasattr(config, "to_dict") else config

    # Determine which backend to use
    backend_type = config_dict.get("backend_type", "llama-cpp")

    # Get API backend config if using an API backend
    api_backends = config_dict.get("api_backends", {})
    backend_config = {}

    if backend_type in api_backends:
        backend_config = api_backends[backend_type]
    elif backend_type == "llama-cpp":
        backend_config = {
            "models_dir": config_dict.get("models_dir", "./models"),
        }
    elif backend_type == "ollama":
        backend_config = api_backends.get("ollama", {})
    elif backend_type == "vllm":
        backend_config = api_backends.get("vllm", {})

    return backend_type, backend_config, config_dict


async def generate_response(message, conversation_id=None, conversation_history=None) -> InferenceResult:
    """Generate a response using the configured BYOK backend."""
    try:
        backend_type, backend_config, config_dict = _get_backend_and_config()
    except InferenceError:
        raise
    except Exception as e:
        raise InferenceError(f"Failed to load config: {e}")

    # For local backends, pass model_file from config
    if backend_type == "llama-cpp":
        backend_config["model_file"] = config_dict.get("model_file", "")
        backend_config["models_dir"] = config_dict.get("models_dir", "./models")
    elif backend_type == "ollama":
        backend_config["model"] = config_dict.get("ollama_model", backend_config.get("model", ""))
    elif backend_type == "vllm":
        backend_config["model"] = config_dict.get("vllm_model", backend_config.get("model", ""))

    try:
        backend = get_backend(backend_type, config=backend_config)
    except ValueError as e:
        raise InferenceError(str(e))

    if not backend.is_available():
        raise InferenceError(
            f"Backend '{backend_type}' is not available. "
            f"Check your configuration and dependencies."
        )

    # Load model if not already loaded
    try:
        backend.load_model(config_dict)
    except BackendError as e:
        raise InferenceError(f"Failed to load model: {e}")

    # Build messages
    messages = _build_messages(message, conversation_history, config_dict)

    # Auto-detect chat template if set to "auto"
    template = config_dict.get("chat_template", "chatml")
    if template == "auto":
        template = auto_detect_template(messages)

    # Add template to params
    gen_params = config_dict.get("generation", {})
    gen_params["chat_template"] = template

    try:
        result = backend.generate(messages, params=gen_params)
        return InferenceResult(
            content=result.text,
            model_name=config_dict.get("model_file", backend_type),
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
        yield f"[Error: No config loaded]"
        return

    if backend_type == "llama-cpp":
        backend_config["model_file"] = config_dict.get("model_file", "")
        backend_config["models_dir"] = config_dict.get("models_dir", "./models")
    elif backend_type == "ollama":
        backend_config["model"] = config_dict.get("ollama_model", backend_config.get("model", ""))
    elif backend_type == "vllm":
        backend_config["model"] = config_dict.get("vllm_model", backend_config.get("model", ""))

    try:
        backend = get_backend(backend_type, config=backend_config)
    except ValueError as e:
        yield f"[Error: {e}]"
        return

    if not backend.is_available():
        yield f"[Error: Backend '{backend_type}' not available]"
        return

    try:
        backend.load_model(config_dict)
    except BackendError as e:
        yield f"[Error: {e}]"
        return

    messages = _build_messages(message, conversation_history, config_dict)

    template = config_dict.get("chat_template", "chatml")
    if template == "auto":
        template = auto_detect_template(messages)

    gen_params = config_dict.get("generation", {})
    gen_params["chat_template"] = template

    try:
        yield from backend.generate_stream(messages, params=gen_params)
    except BackendError as e:
        yield f"\n[Error: {e}]"
