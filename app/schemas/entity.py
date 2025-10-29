from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid


class EntityType(str, Enum):
    PERSON = "person"
    COMPANY = "company"
    AI_AGENT = "ai_agent"


class RelationshipType(str, Enum):
    OWNER = "owner"
    CO_OWNER = "co_owner"
    RENTER = "renter"
    AUTHORIZED_DRIVER = "authorized_driver"
    MANAGER = "manager"
    MECHANIC = "mechanic"


class LinkStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    PENDING = "pending"


# Entity Schemas
class EntityBase(BaseModel):
    entity_type: EntityType
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    document_number: Optional[str] = None
    ai_model: Optional[str] = None
    ai_capabilities: Optional[str] = None
    active: bool = True


class EntityCreate(EntityBase):
    pass


class EntityUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    document_number: Optional[str] = None
    ai_model: Optional[str] = None
    ai_capabilities: Optional[str] = None
    active: Optional[bool] = None


class Entity(EntityBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Vehicle Entity Link Schemas
class VehicleEntityLinkBase(BaseModel):
    vehicle_id: uuid.UUID
    entity_id: uuid.UUID
    relationship_type: RelationshipType
    status: LinkStatus = LinkStatus.ACTIVE
    start_date: datetime
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    active: bool = True


class VehicleEntityLinkCreate(VehicleEntityLinkBase):
    pass


class VehicleEntityLinkUpdate(BaseModel):
    relationship_type: Optional[RelationshipType] = None
    status: Optional[LinkStatus] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None
    active: Optional[bool] = None


class VehicleEntityLink(VehicleEntityLinkBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Combined schemas for responses with related data
class VehicleEntityLinkWithEntity(VehicleEntityLink):
    entity: Entity


class VehicleEntityLinkWithVehicle(VehicleEntityLink):
    vehicle: Optional[dict] = None  # We'll populate this with vehicle details


class VehicleLinksResponse(BaseModel):
    vehicle_id: uuid.UUID
    links: List[VehicleEntityLinkWithEntity]
    active_count: int
    total_count: int