"""In-memory conversation storage with auto-generated titles."""

import uuid
from datetime import datetime, timezone

_conversations: dict[str, dict] = {}


def create_conversation(title: str | None = None) -> dict:
    conv_id = str(uuid.uuid4())[:8]
    conv = {
        "id": conv_id,
        "title": title or "New conversation",
        "messages": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    _conversations[conv_id] = conv
    return conv


def get_conversation(conv_id: str) -> dict | None:
    return _conversations.get(conv_id)


def list_conversations() -> list:
    return [
        {
            "id": c["id"],
            "title": c["title"],
            "created_at": c["created_at"],
            "updated_at": c.get("updated_at", c["created_at"]),
            "message_count": len(c["messages"]),
        }
        for c in sorted(_conversations.values(), key=lambda x: x.get("updated_at", ""), reverse=True)
    ]


def delete_conversation(conv_id: str) -> bool:
    if conv_id in _conversations:
        del _conversations[conv_id]
        return True
    return False


def add_message_to_conversation(conv_id: str, role: str, content: str) -> dict | None:
    conv = _conversations.get(conv_id)
    if conv is None:
        return None
    msg = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    conv["messages"].append(msg)
    conv["updated_at"] = datetime.now(timezone.utc).isoformat()
    # Auto-generate title from first user message
    if len(conv["messages"]) == 1 and role == "user":
        conv["title"] = content[:60] + ("..." if len(content) > 60 else "")
    return msg


def update_conversation_title(conv_id: str, title: str) -> dict | None:
    conv = _conversations.get(conv_id)
    if conv is None:
        return None
    conv["title"] = title
    conv["updated_at"] = datetime.now(timezone.utc).isoformat()
    return {"id": conv["id"], "title": conv["title"]}


def get_conversation_messages(conv_id: str) -> list | None:
    conv = _conversations.get(conv_id)
    if conv is None:
        return None
    return conv["messages"]