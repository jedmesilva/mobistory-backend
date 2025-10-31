from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class FileBase(BaseModel):
    """Schema base para arquivos"""
    vehicle_id: Optional[uuid.UUID] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None  # image, video, document, audio
    source: Optional[str] = None  # mobile, web, api


class FileUploadResponse(BaseModel):
    """Resposta do upload de arquivo"""
    id: uuid.UUID
    file_url: str
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    mime_type: Optional[str] = None
    file_size_bytes: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None
    vehicle_id: Optional[uuid.UUID] = None
    uploaded_by_entity_id: uuid.UUID
    status: str
    uploaded_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class FileUpdate(BaseModel):
    """Schema para atualizar informações do arquivo"""
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    vehicle_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    source: Optional[str] = None


class FileFilter(BaseModel):
    """Filtros para listar arquivos"""
    vehicle_id: Optional[uuid.UUID] = None
    uploaded_by_entity_id: Optional[uuid.UUID] = None
    file_type: Optional[str] = None
    status: Optional[str] = "active"
    skip: int = 0
    limit: int = 100


class FileInfo(FileUploadResponse):
    """Informações completas do arquivo com relacionamentos"""
    pass
