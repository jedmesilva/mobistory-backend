from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime, date

from app.core.database import Base
from .base import BaseModel


class EntityContact(Base, BaseModel):
    """Contatos de entidades (emails, telefones, etc.)"""
    __tablename__ = "entity_contacts"

    entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    contact_type = Column(String, nullable=False)  # email, phone, whatsapp, api_endpoint, mqtt_topic
    contact_value = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    is_primary = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    use_for_login = Column(Boolean, default=False)
    use_for_recovery = Column(Boolean, default=False)
    use_for_notifications = Column(Boolean, default=True)
    use_for_2fa = Column(Boolean, default=False)
    label = Column(String, nullable=True)  # "Pessoal", "Trabalho", "Recuperação"
    is_active = Column(Boolean, default=True)
    start_date = Column(Date, nullable=False, default=date.today)
    end_date = Column(Date, nullable=True)

    # Relationships
    entity = relationship("Entity", back_populates="contacts", foreign_keys=[entity_id])
