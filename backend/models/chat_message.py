# backend/models/chat_message.py
#
# Data model for a single chat message.
#
# STATUS: DEFINED — This can be used now even before inference works.
# It's a plain data class with no dependencies.
#
# Usage:
#   from models.chat_message import ChatMessage, Role
#   msg = ChatMessage(role=Role.USER, content="Hello!")

from enum import Enum
from datetime import datetime, timezone


class Role(str, Enum):
    """
    The role of the entity producing a message.
    Mirrors the convention used in most chat template formats.
    """
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

    # Future: tool call results
    # TOOL = "tool"


class ChatMessage:
    """
    Represents a single message in a conversation.

    Attributes:
        role      (Role)     — Who produced this message
        content   (str)      — The text content
        timestamp (datetime) — When this message was created (UTC)
        id        (str|None) — Optional unique ID for this message
    """

    def __init__(self, role: Role, content: str, timestamp: datetime | None = None, id: str | None = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now(timezone.utc)
        self.id = id

    def to_dict(self) -> dict:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "id": self.id,
        }

    def __repr__(self) -> str:
        preview = self.content[:60] + "..." if len(self.content) > 60 else self.content
        return f"ChatMessage(role={self.role.value}, content='{preview}')"


class Conversation:
    """
    A list of ChatMessages forming a conversation thread.

    TODO (Phase 4.1): Add persistence, conversation ID, title generation.
    """

    def __init__(self, id: str | None = None):
        self.id = id
        self.messages: list[ChatMessage] = []

    def add_message(self, message: ChatMessage) -> None:
        self.messages.append(message)

    def get_messages(self) -> list[ChatMessage]:
        return self.messages

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "messages": [m.to_dict() for m in self.messages],
        }
