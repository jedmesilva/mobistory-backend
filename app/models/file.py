from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Integer, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime

from app.core.database import Base
from .base import BaseModel


class File(Base, BaseModel):
    """Arquivos centralizados (imagens, vídeos, documentos, etc.)"""
    __tablename__ = "files"

    vehicle_id = Column(PGUUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=True)
    uploaded_by_entity_id = Column(PGUUID(as_uuid=True), ForeignKey("entities.id"), nullable=False)

    # Informações do arquivo
    file_url = Column(Text, nullable=False)  # URL ou caminho do arquivo
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)  # image, video, document, audio, etc
    mime_type = Column(String, nullable=True)  # image/png, video/mp4, etc
    file_size_bytes = Column(BigInteger, nullable=True)

    # Metadados específicos
    width = Column(Integer, nullable=True)  # Para imagens
    height = Column(Integer, nullable=True)  # Para imagens
    duration_seconds = Column(Integer, nullable=True)  # Para vídeos/áudios

    # Controle
    source = Column(String, nullable=True)  # mobile, web, api, etc
    status = Column(String, default="active")  # active, deleted, processing, error
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    vehicle = relationship("Vehicle", foreign_keys=[vehicle_id])
    uploaded_by = relationship("Entity", foreign_keys=[uploaded_by_entity_id])
