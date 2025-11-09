from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Text, Boolean, Integer, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from datetime import datetime

from app.core.database import Base
from .base import BaseModel, BaseModelWithUpdate


class ConversationContext(Base, BaseModel):
    """Contextos disponíveis para conversas (ex: manutenção, abastecimento, etc.)"""
    __tablename__ = "conversation_contexts"

    code = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    keywords = Column(JSONB, nullable=True)  # Palavras-chave que ativam este contexto
    available_actions = Column(JSONB, nullable=True)  # Ações disponíveis neste contexto
    ai_instructions = Column(Text, nullable=True)  # Instruções para a IA neste contexto
    requires_link = Column(Boolean, nullable=True)  # Se requer vínculo com veículo
    required_permissions = Column(JSONB, nullable=True)  # Permissões necessárias
    active = Column(Boolean, nullable=True, default=True)

    # Timestamps adicionais
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    # Relationships
    conversations = relationship("Conversation", back_populates="main_context", foreign_keys="Conversation.main_context_id")
    messages = relationship("ConversationMessage", back_populates="context")


class Conversation(Base, BaseModelWithUpdate):
    """Conversas entre entidades e veículos"""
    __tablename__ = "conversations"

    conversation_code = Column(String, nullable=False, unique=True)
    primary_vehicle_id = Column(PGUUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    vehicle_ids = Column(Text, nullable=True)  # Lista de IDs de veículos (separados por vírgula)
    conversation_type = Column(String, nullable=True)  # private, group, support, etc.
    title = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(String, nullable=True)  # active, archived, closed
    main_context_id = Column(PGUUID(as_uuid=True), ForeignKey("conversation_contexts.id"), nullable=True)

    # Estatísticas
    total_participants = Column(Integer, nullable=True, default=0)
    active_participants = Column(Integer, nullable=True, default=0)
    total_messages = Column(Integer, nullable=True, default=0)
    total_actions_executed = Column(Integer, nullable=True, default=0)

    # Timestamps
    started_at = Column(DateTime, nullable=True)
    last_message_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    archived_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    primary_vehicle = relationship("Vehicle", foreign_keys=[primary_vehicle_id])
    main_context = relationship("ConversationContext", back_populates="conversations", foreign_keys=[main_context_id])
    participants = relationship("ConversationParticipant", back_populates="conversation")
    messages = relationship("ConversationMessage", back_populates="conversation")


class ConversationParticipant(Base, BaseModelWithUpdate):
    """Participantes de uma conversa"""
    __tablename__ = "conversation_participants"

    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    link_id = Column(PGUUID(as_uuid=True), ForeignKey("links.id"), nullable=True)
    role = Column(String, nullable=True)  # owner, driver, admin, viewer
    participant_type = Column(String, nullable=True)  # human, ai, system

    # Timestamps de participação
    joined_at = Column(DateTime, nullable=True)
    left_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=True, default=True)

    # Convite/Remoção
    invited_by_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    invited_by_participant_id = Column(PGUUID(as_uuid=True), ForeignKey("conversation_participants.id"), nullable=True)
    invitation_reason = Column(String, nullable=True)
    removed_by_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    removal_reason = Column(String, nullable=True)

    # Configurações
    permissions = Column(JSONB, nullable=True)
    context_summary_at_join = Column(Text, nullable=True)
    auto_leave_config = Column(JSONB, nullable=True)
    notification_enabled = Column(Boolean, nullable=True, default=True)

    # Leitura
    last_read_message_id = Column(PGUUID(as_uuid=True), ForeignKey("conversation_messages.id"), nullable=True)
    last_read_at = Column(DateTime, nullable=True)
    unread_count = Column(Integer, nullable=True, default=0)

    # Metadados extras
    participant_metadata = Column('metadata', JSONB, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="participants")
    entity = relationship("Entity", foreign_keys=[entity_id])
    link = relationship("Link", foreign_keys=[link_id])
    invited_by_entity = relationship("Entity", foreign_keys=[invited_by_entity_id])
    invited_by_participant = relationship("ConversationParticipant", remote_side="ConversationParticipant.id", foreign_keys=[invited_by_participant_id])
    removed_by_entity = relationship("Entity", foreign_keys=[removed_by_entity_id])
    last_read_message = relationship("ConversationMessage", foreign_keys=[last_read_message_id])


class ConversationMessage(Base, BaseModel):
    """Mensagens trocadas em conversas"""
    __tablename__ = "conversation_messages"

    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)

    # Remetente
    sender_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    sender_participant_id = Column(PGUUID(as_uuid=True), ForeignKey("conversation_participants.id"), nullable=True)

    # Destinatário (opcional, para mensagens direcionadas)
    directed_to_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    directed_to_participant_id = Column(PGUUID(as_uuid=True), ForeignKey("conversation_participants.id"), nullable=True)

    # Conteúdo
    content = Column(Text, nullable=False)
    message_type = Column(String, nullable=True)  # text, image, video, audio, system, action

    # Contexto e IA
    context_id = Column(PGUUID(as_uuid=True), ForeignKey("conversation_contexts.id"), nullable=True)
    context_confidence = Column(Numeric, nullable=True)  # 0.0 a 1.0
    detected_intent = Column(String, nullable=True)
    extracted_entities = Column(JSONB, nullable=True)

    # Ações
    action_id = Column(PGUUID(as_uuid=True), nullable=True)  # ID da ação executada
    action_executed = Column(Boolean, nullable=True, default=False)
    action_result = Column(JSONB, nullable=True)

    # Confirmação
    requires_confirmation = Column(Boolean, nullable=True, default=False)
    confirmed = Column(Boolean, nullable=True, default=False)
    confirmed_at = Column(DateTime, nullable=True)
    confirmed_by_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)

    # Anexos e visibilidade
    attachments_urls = Column(Text, nullable=True)
    visible_to_participant_ids = Column(Text, nullable=True)
    is_private = Column(Boolean, nullable=True, default=False)

    # Interação humana
    requires_user_interaction = Column(Boolean, nullable=True, default=False)
    interaction_reason = Column(String, nullable=True)

    # Processamento
    auto_processed = Column(Boolean, nullable=True, default=False)
    processed = Column(Boolean, nullable=True, default=False)
    processed_at = Column(DateTime, nullable=True)

    # Reações
    reactions = Column(JSONB, nullable=True)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender_entity = relationship("Entity", foreign_keys=[sender_entity_id])
    sender_participant = relationship("ConversationParticipant", foreign_keys=[sender_participant_id])
    directed_to_entity = relationship("Entity", foreign_keys=[directed_to_entity_id])
    directed_to_participant = relationship("ConversationParticipant", foreign_keys=[directed_to_participant_id])
    context = relationship("ConversationContext", back_populates="messages")
    confirmed_by_entity = relationship("Entity", foreign_keys=[confirmed_by_entity_id])
