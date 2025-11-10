from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base
from .base import BaseModel


class Permission(Base, BaseModel):
    """Catálogo de todas as permissões possíveis no sistema"""
    __tablename__ = "permissions"

    code = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)
    active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    link_type_permissions = relationship("LinkTypePermission", back_populates="permission", cascade="all, delete-orphan")
