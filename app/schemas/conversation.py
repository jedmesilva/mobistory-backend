from pydantic import BaseModel, ConfigDict, Field, field_serializer
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime
from uuid import UUID
from decimal import Decimal

if TYPE_CHECKING:
    from app.schemas.vehicle import VehicleWithDetails


# =============================================================================
# CONVERSATION CONTEXT SCHEMAS
# =============================================================================

class ConversationContextBase(BaseModel):
    code: str
    category: Optional[str] = None
    name: str
    description: Optional[str] = None
    keywords: Optional[Dict[str, Any]] = None
    available_actions: Optional[Dict[str, Any]] = None
    ai_instructions: Optional[str] = None
    requires_link: Optional[bool] = False
    required_permissions: Optional[Dict[str, Any]] = None
    active: Optional[bool] = True


class ConversationContextCreate(ConversationContextBase):
    pass


class ConversationContextUpdate(BaseModel):
    code: Optional[str] = None
    category: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    keywords: Optional[Dict[str, Any]] = None
    available_actions: Optional[Dict[str, Any]] = None
    ai_instructions: Optional[str] = None
    requires_link: Optional[bool] = None
    required_permissions: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


class ConversationContext(ConversationContextBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# CONVERSATION SCHEMAS
# =============================================================================

class ConversationBase(BaseModel):
    conversation_code: str
    primary_vehicle_id: Optional[UUID] = None
    vehicle_ids: Optional[str] = None  # Lista separada por vírgula
    conversation_type: Optional[str] = None  # private, group, support, etc.
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = "active"  # active, archived, closed
    main_context_id: Optional[UUID] = None


class ConversationCreate(BaseModel):
    primary_vehicle_id: Optional[UUID] = None
    vehicle_ids: Optional[str] = None
    conversation_type: Optional[str] = "private"
    title: Optional[str] = None
    main_context_id: Optional[UUID] = None


class ConversationUpdate(BaseModel):
    primary_vehicle_id: Optional[UUID] = None
    vehicle_ids: Optional[str] = None
    conversation_type: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    main_context_id: Optional[UUID] = None


class Conversation(ConversationBase):
    id: UUID
    total_participants: Optional[int] = 0
    active_participants: Optional[int] = 0
    total_messages: Optional[int] = 0
    total_actions_executed: Optional[int] = 0
    started_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    archived_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# CONVERSATION PARTICIPANT SCHEMAS
# =============================================================================

class ConversationParticipantBase(BaseModel):
    conversation_id: UUID
    entity_id: UUID
    link_id: Optional[UUID] = None
    role: Optional[str] = "viewer"  # owner, driver, admin, viewer
    participant_type: Optional[str] = "human"  # human, ai, system


class ConversationParticipantCreate(ConversationParticipantBase):
    invited_by_entity_id: Optional[UUID] = None
    invitation_reason: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    notification_enabled: Optional[bool] = True


class ConversationParticipantUpdate(BaseModel):
    role: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    notification_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class ConversationParticipant(ConversationParticipantBase):
    id: UUID
    joined_at: Optional[datetime] = None
    left_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    invited_by_entity_id: Optional[UUID] = None
    invited_by_participant_id: Optional[UUID] = None
    invitation_reason: Optional[str] = None
    removed_by_entity_id: Optional[UUID] = None
    removal_reason: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    context_summary_at_join: Optional[str] = None
    auto_leave_config: Optional[Dict[str, Any]] = None
    notification_enabled: Optional[bool] = True
    last_read_message_id: Optional[UUID] = None
    last_read_at: Optional[datetime] = None
    unread_count: Optional[int] = 0
    participant_metadata: Optional[Dict[str, Any]] = Field(None, serialization_alias='metadata')
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# =============================================================================
# CONVERSATION MESSAGE SCHEMAS
# =============================================================================

class ConversationMessageBase(BaseModel):
    conversation_id: UUID
    content: str
    message_type: Optional[str] = "text"  # text, image, video, audio, system, action


class ConversationMessageCreate(ConversationMessageBase):
    sender_entity_id: UUID
    sender_participant_id: Optional[UUID] = None
    directed_to_entity_id: Optional[UUID] = None
    directed_to_participant_id: Optional[UUID] = None
    context_id: Optional[UUID] = None
    attachments_urls: Optional[str] = None
    is_private: Optional[bool] = False
    requires_confirmation: Optional[bool] = False


class ConversationMessageUpdate(BaseModel):
    content: Optional[str] = None
    confirmed: Optional[bool] = None
    confirmed_by_entity_id: Optional[UUID] = None
    processed: Optional[bool] = None
    reactions: Optional[Dict[str, Any]] = None


class ConversationMessage(ConversationMessageBase):
    id: UUID
    sender_entity_id: UUID
    sender_participant_id: Optional[UUID] = None
    directed_to_entity_id: Optional[UUID] = None
    directed_to_participant_id: Optional[UUID] = None
    context_id: Optional[UUID] = None
    context_confidence: Optional[Decimal] = None
    detected_intent: Optional[str] = None
    extracted_entities: Optional[Dict[str, Any]] = None
    action_id: Optional[UUID] = None
    action_executed: Optional[bool] = False
    action_result: Optional[Dict[str, Any]] = None
    requires_confirmation: Optional[bool] = False
    confirmed: Optional[bool] = False
    confirmed_at: Optional[datetime] = None
    confirmed_by_entity_id: Optional[UUID] = None
    attachments_urls: Optional[str] = None
    visible_to_participant_ids: Optional[str] = None
    is_private: Optional[bool] = False
    requires_user_interaction: Optional[bool] = False
    interaction_reason: Optional[str] = None
    auto_processed: Optional[bool] = False
    processed: Optional[bool] = False
    processed_at: Optional[datetime] = None
    reactions: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# DETAILED SCHEMAS WITH RELATIONSHIPS
# =============================================================================

class ConversationParticipantWithEntity(ConversationParticipant):
    """Participant com dados da entidade"""
    entity: Optional[Any] = None  # Será Entity quando importado

    model_config = ConfigDict(from_attributes=True)


class ConversationMessageWithDetails(ConversationMessage):
    """Message com dados do sender e contexto"""
    sender_entity: Optional[Any] = None  # Será Entity quando importado
    context: Optional[ConversationContext] = None

    model_config = ConfigDict(from_attributes=True)


class ConversationWithDetails(Conversation):
    """Conversation com veículo, contexto, participantes e mensagens recentes"""
    primary_vehicle: Optional[Any] = None  # Será Vehicle quando importado
    main_context: Optional[ConversationContext] = None
    participants: List[ConversationParticipantWithEntity] = []
    messages: List[ConversationMessageWithDetails] = []

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================

class ConversationListResponse(BaseModel):
    """Response para listagem de conversas"""
    conversations: List[Conversation]
    total: int
    page: int
    page_size: int


class ConversationDetailResponse(BaseModel):
    """Response detalhado de uma conversa"""
    conversation: ConversationWithDetails
    can_send_message: bool = False
    can_invite_participants: bool = False
    can_manage_conversation: bool = False
