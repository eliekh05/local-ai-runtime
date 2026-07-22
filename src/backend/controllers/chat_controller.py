"""Controller for chat request handling."""

from fastapi import HTTPException

from backend.services.inference_service import generate_response, InferenceError
from backend.models.chat_message import ChatMessage, Role
from backend.services.conversation_service import get_conversation


async def handle_chat_request(request) -> dict:
    user_message = ChatMessage(role=Role.USER, content=request.message)

    conversation_history = None
    if request.conversation_id:
        conv = get_conversation(request.conversation_id)
        if conv:
            conversation_history = [
                ChatMessage(role=Role(m["role"]), content=m["content"])
                for m in conv["messages"]
            ]

    try:
        result = await generate_response(
            message=user_message,
            conversation_id=request.conversation_id,
            conversation_history=conversation_history,
        )
    except InferenceError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Auto-save user message and assistant response to conversation
    if request.conversation_id:
        from backend.services.conversation_service import add_message_to_conversation
        add_message_to_conversation(request.conversation_id, "user", request.message)
        add_message_to_conversation(request.conversation_id, "assistant", result.content)

    return {
        "response": result.content,
        "model": result.model_name,
        "tokens_used": result.tokens_used,
        "finish_reason": result.finish_reason,
    }
