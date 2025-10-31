from fastapi import APIRouter, Depends, HTTPException, UploadFile, File as FastAPIFile, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import os
import shutil
from pathlib import Path
from datetime import datetime
import mimetypes
from PIL import Image

from app.core.database import get_db
from app.models import File, Entity, Vehicle
from app.schemas.file import FileUploadResponse, FileUpdate, FileInfo

router = APIRouter()


# Configuração de diretório de upload
UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def get_file_type(mime_type: str) -> str:
    """Determinar tipo de arquivo baseado no MIME type"""
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("audio/"):
        return "audio"
    elif mime_type.startswith("application/pdf"):
        return "document"
    elif "document" in mime_type or "word" in mime_type or "excel" in mime_type:
        return "document"
    else:
        return "other"


def get_image_dimensions(file_path: str) -> tuple:
    """Obter dimensões de uma imagem"""
    try:
        with Image.open(file_path) as img:
            return img.width, img.height
    except Exception:
        return None, None


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    uploaded_by_entity_id: uuid.UUID = Form(...),
    vehicle_id: Optional[uuid.UUID] = Form(None),
    source: Optional[str] = Form("api"),
    db: Session = Depends(get_db)
):
    """
    Upload de arquivo

    Faz upload do arquivo, salva no sistema de arquivos e registra na tabela files.

    - **file**: Arquivo a ser enviado
    - **uploaded_by_entity_id**: ID da entidade que está fazendo upload
    - **vehicle_id**: ID do veículo relacionado (opcional)
    - **source**: Origem do upload (mobile, web, api)
    """
    # Verificar se entidade existe
    entity = db.query(Entity).filter(Entity.id == uploaded_by_entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Verificar se veículo existe (se fornecido)
    if vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

    # Gerar nome único para o arquivo
    file_extension = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    # Salvar arquivo no disco
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Obter informações do arquivo
    file_size = os.path.getsize(file_path)
    mime_type = file.content_type or mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    file_type = get_file_type(mime_type)

    # Obter dimensões se for imagem
    width, height = None, None
    if file_type == "image":
        width, height = get_image_dimensions(str(file_path))

    # Criar URL do arquivo (ajuste conforme sua configuração)
    file_url = f"/uploads/{unique_filename}"

    # Registrar no banco de dados
    db_file = File(
        vehicle_id=vehicle_id,
        uploaded_by_entity_id=uploaded_by_entity_id,
        file_url=file_url,
        file_name=file.filename,
        file_type=file_type,
        mime_type=mime_type,
        file_size_bytes=file_size,
        width=width,
        height=height,
        source=source,
        status="active",
        uploaded_at=datetime.utcnow()
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return db_file


@router.get("/", response_model=List[FileInfo])
def list_files(
    vehicle_id: Optional[uuid.UUID] = Query(None),
    uploaded_by_entity_id: Optional[uuid.UUID] = Query(None),
    file_type: Optional[str] = Query(None),
    status: str = Query("active"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Listar arquivos com filtros

    - **vehicle_id**: Filtrar por veículo
    - **uploaded_by_entity_id**: Filtrar por entidade que fez upload
    - **file_type**: Filtrar por tipo (image, video, document, audio)
    - **status**: Filtrar por status (active, deleted, processing)
    - **skip**: Paginação - quantos pular
    - **limit**: Paginação - limite de resultados
    """
    query = db.query(File)

    if vehicle_id:
        query = query.filter(File.vehicle_id == vehicle_id)
    if uploaded_by_entity_id:
        query = query.filter(File.uploaded_by_entity_id == uploaded_by_entity_id)
    if file_type:
        query = query.filter(File.file_type == file_type)
    if status:
        query = query.filter(File.status == status)

    files = query.order_by(File.uploaded_at.desc()).offset(skip).limit(limit).all()
    return files


@router.get("/{file_id}", response_model=FileInfo)
def get_file(
    file_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Buscar arquivo específico por ID

    Retorna todas as informações do arquivo registradas no banco.
    """
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file


@router.patch("/{file_id}", response_model=FileInfo)
def update_file_info(
    file_id: uuid.UUID,
    file_update: FileUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar informações do arquivo

    Permite atualizar metadados do arquivo (nome, tipo, veículo relacionado, etc).
    NÃO atualiza o arquivo físico, apenas as informações no banco.
    """
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    # Atualizar apenas campos fornecidos
    update_data = file_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(file, field, value)

    db.commit()
    db.refresh(file)

    return file


@router.delete("/{file_id}")
def delete_file(
    file_id: uuid.UUID,
    permanent: bool = Query(False, description="Se True, deleta fisicamente o arquivo. Se False, apenas soft delete."),
    db: Session = Depends(get_db)
):
    """
    Deletar arquivo

    - **permanent=False**: Soft delete - marca como 'deleted' no banco, mas mantém o arquivo
    - **permanent=True**: Hard delete - remove do banco E do sistema de arquivos
    """
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if permanent:
        # Hard delete - remove arquivo físico e registro do banco
        file_path = UPLOAD_DIR / os.path.basename(file.file_url)
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error deleting physical file: {str(e)}")

        db.delete(file)
        db.commit()
        return {"message": "File permanently deleted"}
    else:
        # Soft delete - apenas marca como deleted
        file.status = "deleted"
        db.commit()
        return {"message": "File marked as deleted"}


@router.get("/download/{file_id}")
def download_file(
    file_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obter URL de download do arquivo

    Retorna informações para download do arquivo.
    """
    file = db.query(File).filter(File.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if file.status == "deleted":
        raise HTTPException(status_code=410, detail="File has been deleted")

    return {
        "file_id": file.id,
        "file_url": file.file_url,
        "file_name": file.file_name,
        "mime_type": file.mime_type,
        "file_size_bytes": file.file_size_bytes
    }
