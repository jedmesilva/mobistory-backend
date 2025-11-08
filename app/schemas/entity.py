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
    name: str = Field(validation_alias="display_name", serialization_alias="name")
    email: Optional[str] = None
    phone: Optional[str] = None
    document_number: Optional[str] = Field(default=None, validation_alias="legal_id_number")
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


class Entity(BaseModel):
    id: uuid.UUID
    entity_code: str
    name: str = Field(alias="display_name")
    email: Optional[str] = None
    phone: Optional[str] = None
    document_number: Optional[str] = Field(default=None, alias="legal_id_number")
    active: bool = True
    created_at: datetime
    updated_at: datetime
    is_anonymous: bool = False
    verified: bool = False  # Entidade completamente validada (docs + dados conferidos)

    class Config:
        from_attributes = True
        populate_by_name = True


# Anonymous Entity Schemas
class AnonymousEntityCreate(BaseModel):
    """Schema para criar entidade anônima com device fingerprint"""
    device_fingerprint: dict  # Device ID, network info, geolocation, etc.
    name: Optional[str] = "Usuário Anônimo"


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


# Entity Relationship Schemas (pai-filho)
class EntityRelationshipBase(BaseModel):
    entity_id: uuid.UUID
    parent_entity_id: uuid.UUID
    relationship_type: str = "parent-child"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True
    reason: Optional[str] = None
    observations: Optional[str] = None


class EntityRelationshipCreate(BaseModel):
    parent_entity_id: uuid.UUID
    relationship_type: str = "parent-child"
    reason: Optional[str] = None
    observations: Optional[str] = None


class EntityRelationshipUpdate(BaseModel):
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    observations: Optional[str] = None


class EntityRelationship(EntityRelationshipBase):
    id: uuid.UUID
    created_by_entity_id: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EntityRelationshipWithParent(EntityRelationship):
    """Relacionamento com dados da entidade pai"""
    parent_entity: Entity


class EntityRelationshipWithChild(EntityRelationship):
    """Relacionamento com dados da entidade filho"""
    entity: Entity


# ============================================================================
# Link Advanced Schemas (para request, claim, grant)
# ============================================================================

class LinkRequest(BaseModel):
    """Solicitação de vínculo a outra entidade"""
    vehicle_id: uuid.UUID
    requested_entity_id: uuid.UUID  # Entidade que receberá a solicitação
    link_type_id: Optional[uuid.UUID] = None
    relationship_type: Optional[RelationshipType] = None
    reason: Optional[str] = None
    observations: Optional[str] = None


class LinkClaim(BaseModel):
    """Reivindicação de vínculo com documentos"""
    vehicle_id: uuid.UUID
    link_type_id: Optional[uuid.UUID] = None
    relationship_type: Optional[RelationshipType] = None
    document_proof: str  # URL ou base64 do documento
    observations: Optional[str] = None


class LinkGrant(BaseModel):
    """Concessão de vínculo a outra entidade"""
    vehicle_id: uuid.UUID
    granted_entity_id: uuid.UUID  # Entidade que receberá o vínculo
    link_type_id: Optional[uuid.UUID] = None
    relationship_type: Optional[RelationshipType] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    observations: Optional[str] = None


class LinkApproval(BaseModel):
    """Aprovação/rejeição de solicitação"""
    approved: bool
    link_type_id: Optional[uuid.UUID] = None
    observations: Optional[str] = None


class LinkWithEntities(VehicleEntityLink):
    """Vínculo com dados completos de entidade e veículo"""
    entity: Optional[Entity] = None
    vehicle: Optional[dict] = None