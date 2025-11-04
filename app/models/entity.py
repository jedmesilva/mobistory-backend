from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Enum as SQLEnum, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import enum
from datetime import datetime, date
import uuid

from app.core.database import Base
from .base import BaseModel, BaseModelWithUpdate


class EntityType(Base, BaseModel):
    """Tipos de entidades (pessoa física, jurídica, etc.)"""
    __tablename__ = "entity_types"

    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    requires_cpf = Column(Boolean, default=False)
    requires_cnpj = Column(Boolean, default=False)
    requires_special_id = Column(Boolean, default=False)
    active = Column(Boolean, default=True)

    # Relationships
    entities = relationship("Entity", back_populates="entity_type")


class Entity(Base, BaseModelWithUpdate):
    """Entidades (pessoas, empresas, etc.)"""
    __tablename__ = "entities"

    entity_code = Column(String, unique=True, nullable=False)
    entity_type_id = Column(PGUUID(as_uuid=True), ForeignKey("entity_types.id"), nullable=True)
    legal_id_number = Column(String, unique=True, nullable=True)  # CPF, CNPJ, etc
    global_key_hash = Column(String, nullable=True)
    display_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    profile_picture_url = Column(Text, nullable=True)
    extra_metadata = Column("metadata", JSONB, nullable=True)  # 'metadata' é reservado, usa alias
    active = Column(Boolean, default=True)

    # Relationships
    entity_type = relationship("EntityType", back_populates="entities")
    vehicle_links = relationship("Link", back_populates="entity", foreign_keys="Link.entity_id")

    # Relacionamentos pai-filho
    children_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.parent_entity_id",
        back_populates="parent_entity"
    )
    parent_relationships = relationship(
        "EntityRelationship",
        foreign_keys="EntityRelationship.entity_id",
        back_populates="entity"
    )


class EntityRelationship(Base, BaseModelWithUpdate):
    """Relacionamentos entre entidades (pai-filho)"""
    __tablename__ = "entity_relationships"

    entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    parent_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id", ondelete="RESTRICT"), nullable=False)
    relationship_type = Column(String, nullable=False)  # parent-child, guardian-ward, etc
    start_date = Column(Date, nullable=False, default=date.today)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    reason = Column(Text, nullable=True)
    observations = Column(Text, nullable=True)
    created_by_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)

    # Relationships
    entity = relationship("Entity", foreign_keys=[entity_id], back_populates="parent_relationships")
    parent_entity = relationship("Entity", foreign_keys=[parent_entity_id], back_populates="children_relationships")
    created_by = relationship("Entity", foreign_keys=[created_by_entity_id])


class LinkType(Base, BaseModel):
    """Tipos de vínculos (proprietário, condutor autorizado, etc.)"""
    __tablename__ = "link_types"

    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSONB, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    links = relationship("Link", back_populates="link_type")


class Link(Base, BaseModelWithUpdate):
    """Vínculos entre entidades e veículos"""
    __tablename__ = "links"

    link_code = Column(String, unique=True, nullable=False)
    entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    vehicle_id = Column(PGUUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    link_type_id = Column(PGUUID(as_uuid=True), ForeignKey("link_types.id"), nullable=True)
    own_key_hash = Column(String, nullable=True)
    uses_own_key = Column(Boolean, default=False)
    status = Column(String, nullable=True)  # pending, active, suspended, terminated
    document_proof = Column(Text, nullable=True)
    validated_at = Column(DateTime, nullable=True)
    validated_by = Column(PGUUID(as_uuid=True), ForeignKey("links.id"), nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    observations = Column(Text, nullable=True)

    # Relationships
    entity = relationship("Entity", back_populates="vehicle_links", foreign_keys=[entity_id])
    vehicle = relationship("Vehicle", back_populates="entity_links", foreign_keys=[vehicle_id])
    link_type = relationship("LinkType", back_populates="links")


# Enums para compatibilidade com código antigo
class RelationshipType(str, enum.Enum):
    OWNER = "owner"
    CO_OWNER = "co_owner"
    RENTER = "renter"
    AUTHORIZED_DRIVER = "authorized_driver"
    MANAGER = "manager"
    MECHANIC = "mechanic"


class LinkStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    PENDING = "pending"


# Alias para compatibilidade com código antigo
VehicleEntityLink = Link