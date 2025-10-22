from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from .message import Message
from .vehicle import VehicleWithDetails


class ConversationBase(BaseModel):
    vehicle_id: UUID
    title: Optional[str] = None


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None


class Conversation(ConversationBase):
    id: UUID
    user_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationWithDetails(Conversation):
    """Conversation com veículo e últimas mensagens"""
    vehicle: Optional[VehicleWithDetails] = None
    messages: List[Message] = []

    model_config = ConfigDict(from_attributes=True)
