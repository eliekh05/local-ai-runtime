"""POST /chat and POST /chat/stream — Chat endpoints with streaming."""

import sys
from pathlib import Path

_project_root = str(Path(__file__).resolve().parent.parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from controllers.chat_controller import handle_chat_request

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int
    finish_reason: str = "stop"


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and receive a response from any backend."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    return await handle_chat_request(request)


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Stream a response token-by-token using SSE."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    from models.chat_message import ChatMessage, Role
    from services.inference_service import generate_stream_response
    from services.conversation_service import (
        get_conversation,
        add_message_to_conversation,
    )

    conversation_history = None
    if request.conversation_id:
        conv = get_conversation(request.conversation_id)
        if conv:
            conversation_history = [
                ChatMessage(role=Role(m["role"]), content=m["content"])
                for m in conv["messages"]
            ]

    user_message = ChatMessage(role=Role.USER, content=request.message)

    def event_generator():
        full_response = []
        try:
            for token in generate_stream_response(
                message=user_message,
                conversation_history=conversation_history,
            ):
                full_response.append(token)
                yield f"data: {json.dumps({'token': token, 'done': False})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
            return

        # Save to conversation
        if request.conversation_id:
            add_message_to_conversation(request.conversation_id, "user", request.message)
            add_message_to_conversation(request.conversation_id, "assistant", "".join(full_response))

        yield f"data: {json.dumps({'token': '', 'done': True})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
