from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from app.models.message import MessageType, SenderType


class MessageBase(BaseModel):
    content: str
    message_type: MessageType = MessageType.TEXT
    context_hint: Optional[str] = None
    media_url: Optional[str] = None


class MessageCreate(MessageBase):
    conversation_id: UUID
    sender_type: SenderType = SenderType.USER


class MessageUpdate(BaseModel):
    content: Optional[str] = None
    context_id: Optional[UUID] = None


class Message(MessageBase):
    id: UUID
    conversation_id: UUID
    context_id: Optional[UUID] = None
    sender_type: SenderType
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
