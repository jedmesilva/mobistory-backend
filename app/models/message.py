from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import enum
from datetime import datetime

from app.core.database import Base
from .base import BaseModel


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"


class SenderType(str, enum.Enum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class Message(Base, BaseModel):
    __tablename__ = "messages"

    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT)
    sender_type = Column(SQLEnum(SenderType), default=SenderType.USER)
    context_hint = Column(String, nullable=True)
    media_url = Column(Text, nullable=True)

    # Relationships
    # conversation = relationship("Conversation", back_populates="messages")
