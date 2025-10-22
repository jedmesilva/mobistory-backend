from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from .base import BaseModel


class Conversation(Base, BaseModel):
    """Conversa entre usuário e IA sobre um veículo"""

    __tablename__ = "conversations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    title = Column(String, nullable=True)  # Título gerado automaticamente
    is_active = Column(Boolean, default=True)

    # Relacionamentos
    user = relationship("User", back_populates="conversations")
    vehicle = relationship("Vehicle", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    contexts = relationship("ConversationContext", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation {self.id}>"
