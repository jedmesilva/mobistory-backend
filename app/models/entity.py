from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
import enum
from datetime import datetime
import uuid

from app.core.database import Base
from .base import BaseModel


class EntityType(str, enum.Enum):
    PERSON = "person"
    COMPANY = "company"
    AI_AGENT = "ai_agent"


class Entity(Base, BaseModel):
    __tablename__ = "entities"

    entity_type = Column(SQLEnum(EntityType), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    document_number = Column(String, nullable=True)
    ai_model = Column(String, nullable=True)
    ai_capabilities = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    vehicle_links = relationship("VehicleEntityLink", back_populates="entity")


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


class VehicleEntityLink(Base, BaseModel):
    __tablename__ = "vehicle_entity_links"

    vehicle_id = Column(PGUUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=False)
    relationship_type = Column(SQLEnum(RelationshipType), nullable=False)
    status = Column(SQLEnum(LinkStatus), default=LinkStatus.ACTIVE)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="entity_links")
    entity = relationship("Entity", back_populates="vehicle_links")