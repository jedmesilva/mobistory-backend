from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class LinkTypePermission(Base):
    """Relacionamento N para N entre tipos de vínculos e permissões.
    Define quais permissões cada tipo de vínculo possui por padrão.
    """
    __tablename__ = "link_type_permissions"

    link_type_id = Column(PGUUID(as_uuid=True), ForeignKey("link_types.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    permission_id = Column(PGUUID(as_uuid=True), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    link_type = relationship("LinkType", back_populates="link_type_permissions")
    permission = relationship("Permission", back_populates="link_type_permissions")
