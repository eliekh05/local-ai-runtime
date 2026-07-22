"""Conversation history routes with full CRUD."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.services.conversation_service import (
    create_conversation,
    get_conversation,
    list_conversations,
    delete_conversation,
    add_message_to_conversation,
    update_conversation_title,
)

router = APIRouter()


class ConversationCreate(BaseModel):
    title: str | None = None


class ConversationRename(BaseModel):
    title: str


class MessageAdd(BaseModel):
    role: str
    content: str


@router.get("/")
async def get_all_conversations():
    return {"conversations": list_conversations()}


@router.post("/")
async def create_new_conversation(body: ConversationCreate):
    conv = create_conversation(title=body.title)
    return conv


@router.get("/{conversation_id}")
async def get_conversation_detail(conversation_id: str):
    conv = get_conversation(conversation_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conv


@router.patch("/{conversation_id}")
async def rename_conversation(conversation_id: str, body: ConversationRename):
    result = update_conversation_title(conversation_id, body.title)
    if result is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return result


@router.delete("/{conversation_id}")
async def delete_conversation_route(conversation_id: str):
    ok = delete_conversation(conversation_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return {"message": "Deleted"}


@router.post("/{conversation_id}/messages")
async def add_message(conversation_id: str, body: MessageAdd):
    msg = add_message_to_conversation(conversation_id, body.role, body.content)
    if msg is None:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return msg
