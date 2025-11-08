from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime, date

from app.core.database import Base
from .base import BaseModel


class EntityName(Base, BaseModel):
    """Histórico de nomes de entidades"""
    __tablename__ = "entity_names"

    entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    name_type = Column(String, nullable=False)  # legal_name, display_name, nickname, alias, trade_name
    name_value = Column(String, nullable=False)
    is_current = Column(Boolean, default=True)
    start_date = Column(Date, nullable=False, default=date.today)
    end_date = Column(Date, nullable=True)
    reason = Column(String, nullable=True)  # marriage, divorce, legal_change, correction, preference
    changed_by_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=True)
    observations = Column(Text, nullable=True)

    # Relationships
    entity = relationship("Entity", back_populates="names", foreign_keys=[entity_id])
    changed_by = relationship("Entity", foreign_keys=[changed_by_entity_id])
