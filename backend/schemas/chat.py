from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class MessageSchema(BaseModel):
    role: MessageRole
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationHistory(BaseModel):
    session_id: str
    messages: list[MessageSchema]
