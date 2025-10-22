from sqlalchemy import Column, String, Text, ForeignKey, Boolean, Numeric, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import enum
from app.core.database import Base
from .base import BaseModel


class ContextType(str, enum.Enum):
    """Tipos de contexto"""
    FUELING = "fueling"
    MAINTENANCE = "maintenance"
    ODOMETER = "odometer"
    VEHICLE_UPDATE = "vehicle_update"
    VEHICLE_REGISTER = "vehicle_register"
    DOCUMENT = "document"
    INSURANCE = "insurance"
    ISSUE = "issue"
    GENERAL = "general"


class ContextStatus(str, enum.Enum):
    """Status do contexto"""
    DRAFT = "draft"  # IA identificou, aguarda confirmação
    CONFIRMED = "confirmed"  # Usuário confirmou
    COMPLETED = "completed"  # Contexto finalizado (registro criado)
    CANCELLED = "cancelled"  # Usuário cancelou


class ConversationContext(Base, BaseModel):
    """Contexto de uma conversa (agrupa mensagens relacionadas)"""

    __tablename__ = "conversation_contexts"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)

    context_type = Column(SQLEnum(ContextType), nullable=False)
    status = Column(SQLEnum(ContextStatus), nullable=False, default=ContextStatus.DRAFT)

    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)

    # Metadata específico por tipo (JSONB para flexibilidade)
    metadata = Column(JSONB, default={}, nullable=False)

    # Hint inicial do contexto
    context_hint = Column(String, nullable=True)

    # Confiança da IA (0.00 a 1.00)
    ai_confidence = Column(Numeric(3, 2), nullable=True)

    # Confirmação do usuário
    confirmed_by_user = Column(Boolean, default=False)
    requires_user_confirmation = Column(Boolean, default=False)

    # Timestamps importantes
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Início do contexto
    completed_at = Column(DateTime, nullable=True)  # Quando foi finalizado

    # Soft delete
    active = Column(Boolean, default=True)

    # Raciocínio da IA
    reasoning = Column(Text, nullable=True)
    needs_clarification = Column(Boolean, default=False)

    # Relacionamentos
    conversation = relationship("Conversation", back_populates="contexts")
    messages = relationship("Message", back_populates="context")

    def __repr__(self):
        return f"<Context {self.context_type} - {self.title}>"
