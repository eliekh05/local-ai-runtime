"""OpenAI-compatible gateway — /v1/models and /v1/chat/completions.

Lets any OpenAI SDK client talk to the active BYOK backend
(local GGUF, Ollama, cloud APIs, or another router like 9router).
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.models.chat_message import ChatMessage, Role
from backend.services.inference_service import (
    InferenceError,
    generate_response,
    generate_stream_response,
)
from backend.services.model_service import get_active_config, set_model_loaded
from model_runtime.providers import list_providers

router = APIRouter()


class ChatMessageIn(BaseModel):
    role: str
    content: str | list[Any] = ""


class ChatCompletionsRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessageIn]
    stream: bool = False
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    seed: int | None = None


def _text_content(content: str | list[Any]) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for item in content:
        if isinstance(item, str):
            parts.append(item)
        elif isinstance(item, dict) and item.get("type") == "text":
            parts.append(str(item.get("text", "")))
    return "".join(parts)


def _apply_request_overrides(body: ChatCompletionsRequest) -> None:
    """Temporarily apply model/generation overrides from the OpenAI request."""
    config = get_active_config()
    if config is None:
        raise HTTPException(status_code=400, detail="No active model configuration. Complete onboarding first.")

    if body.model:
        config.model_file = body.model
        bt = config.backend_type
        if bt == "openai":
            config.openai_model = body.model
        elif bt == "anthropic":
            config.anthropic_model = body.model
        elif bt == "gemini":
            config.gemini_model = body.model
        elif bt == "ollama":
            config.ollama_model = body.model
        elif bt == "vllm":
            config.vllm_model = body.model
        elif bt == "openai_compatible":
            config.compatible_model = body.model

    if body.temperature is not None:
        config.generation.temperature = body.temperature
    if body.top_p is not None:
        config.generation.top_p = body.top_p
    if body.max_tokens is not None:
        config.generation.max_new_tokens = body.max_tokens
    if body.seed is not None:
        config.generation.seed = body.seed


def _split_history(messages: list[ChatMessageIn]) -> tuple[ChatMessage, list[ChatMessage] | None, str | None]:
    if not messages:
        raise HTTPException(status_code=400, detail="messages cannot be empty")

    system_prompt = None
    converted: list[ChatMessage] = []
    for msg in messages:
        role = msg.role
        text = _text_content(msg.content)
        if role == "system":
            system_prompt = text
            continue
        if role not in ("user", "assistant"):
            role = "user"
        converted.append(ChatMessage(role=Role(role), content=text))

    if not converted:
        raise HTTPException(status_code=400, detail="Need at least one user/assistant message")

    last = converted[-1]
    history = converted[:-1] or None
    return last, history, system_prompt


@router.get("/models")
async def list_models():
    config = get_active_config()
    data = []
    if config and config.is_ready():
        mid = config.model_file or config.compatible_model or config.backend_type
        data.append({
            "id": mid,
            "object": "model",
            "owned_by": config.provider_id or config.backend_type,
        })
    # Also advertise catalog defaults so clients can discover options
    for provider in list_providers():
        for model in provider.get("models") or []:
            data.append({
                "id": f"{provider['id']}/{model}" if "/" not in model else model,
                "object": "model",
                "owned_by": provider["id"],
            })
    # De-dupe by id preserving order
    seen = set()
    unique = []
    for item in data:
        if item["id"] in seen:
            continue
        seen.add(item["id"])
        unique.append(item)
    return {"object": "list", "data": unique}


@router.post("/chat/completions")
async def chat_completions(body: ChatCompletionsRequest, request: Request):
    _apply_request_overrides(body)
    config = get_active_config()
    assert config is not None

    last, history, system_prompt = _split_history(body.messages)
    if system_prompt is not None:
        config.system_prompt = system_prompt

    model_id = (
        body.model
        or config.model_file
        or config.compatible_model
        or config.backend_type
    )
    set_model_loaded(model_id)
    created = int(time.time())
    completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"

    if body.stream:
        def event_generator():
            full = []
            try:
                # Role chunk
                yield (
                    "data: "
                    + json.dumps({
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model_id,
                        "choices": [{
                            "index": 0,
                            "delta": {"role": "assistant"},
                            "finish_reason": None,
                        }],
                    })
                    + "\n\n"
                )
                for token in generate_stream_response(message=last, conversation_history=history):
                    full.append(token)
                    yield (
                        "data: "
                        + json.dumps({
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created,
                            "model": model_id,
                            "choices": [{
                                "index": 0,
                                "delta": {"content": token},
                                "finish_reason": None,
                            }],
                        })
                        + "\n\n"
                    )
                yield (
                    "data: "
                    + json.dumps({
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model_id,
                        "choices": [{
                            "index": 0,
                            "delta": {},
                            "finish_reason": "stop",
                        }],
                    })
                    + "\n\n"
                )
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield (
                    "data: "
                    + json.dumps({"error": {"message": str(e), "type": "server_error"}})
                    + "\n\n"
                )

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    try:
        result = await generate_response(message=last, conversation_history=history)
    except InferenceError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return {
        "id": completion_id,
        "object": "chat.completion",
        "created": created,
        "model": result.model_name or model_id,
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": result.content},
            "finish_reason": result.finish_reason or "stop",
        }],
        "usage": {
            "prompt_tokens": 0,
            "completion_tokens": result.tokens_used,
            "total_tokens": result.tokens_used,
        },
    }
