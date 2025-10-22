from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum
from app.core.database import Base
from .base import BaseModel


class MessageType(str, enum.Enum):
    """Tipos de mensagem"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class SenderType(str, enum.Enum):
    """Quem enviou a mensagem"""
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class Message(Base, BaseModel):
    """Mensagem em uma conversa"""

    __tablename__ = "messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    context_id = Column(UUID(as_uuid=True), ForeignKey("conversation_contexts.id"), nullable=True)

    sender_type = Column(SQLEnum(SenderType), nullable=False, default=SenderType.USER)
    message_type = Column(SQLEnum(MessageType), nullable=False, default=MessageType.TEXT)

    content = Column(Text, nullable=False)  # Texto da mensagem
    context_hint = Column(String, nullable=True)  # Hint de contexto enviado pelo app
    media_url = Column(String, nullable=True)  # URL do arquivo de mídia se houver

    # Relacionamentos
    conversation = relationship("Conversation", back_populates="messages")
    context = relationship("ConversationContext", back_populates="messages")

    def __repr__(self):
        return f"<Message {self.sender_type} - {self.content[:30]}...>"
