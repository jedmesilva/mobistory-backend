from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from pathlib import Path
import uuid
from app.core.database import get_db
from app.core.config import settings
from app.models import User
from app.api.deps import get_current_user

router = APIRouter()

# Criar pasta de uploads se não existir
UPLOAD_DIR = Path(settings.STORAGE_PATH)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Tipos de arquivo permitidos
ALLOWED_EXTENSIONS = {
    "image": {".jpg", ".jpeg", ".png", ".gif", ".webp"},
    "audio": {".mp3", ".wav", ".m4a", ".ogg"},
    "video": {".mp4", ".mov", ".avi", ".mkv"},
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_file_extension(filename: str) -> str:
    """Obter extensão do arquivo"""
    return Path(filename).suffix.lower()


def get_file_type(extension: str) -> str:
    """Determinar tipo do arquivo pela extensão"""
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return "other"


def is_allowed_file(filename: str) -> bool:
    """Verificar se arquivo é permitido"""
    ext = get_file_extension(filename)
    for extensions in ALLOWED_EXTENSIONS.values():
        if ext in extensions:
            return True
    return False


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload de arquivo (imagem, áudio, vídeo)

    - **file**: Arquivo a ser enviado

    Tipos permitidos:
    - Imagens: jpg, jpeg, png, gif, webp
    - Áudios: mp3, wav, m4a, ogg
    - Vídeos: mp4, mov, avi, mkv

    Tamanho máximo: 50MB

    Retorna:
    ```json
    {
      "filename": "nome-original.jpg",
      "stored_filename": "uuid.jpg",
      "url": "/api/v1/upload/uuid.jpg",
      "file_type": "image",
      "size": 123456
    }
    ```
    """

    # Validar extensão
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join([ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts])}",
        )

    # Ler arquivo
    contents = await file.read()
    file_size = len(contents)

    # Validar tamanho
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB",
        )

    # Gerar nome único
    extension = get_file_extension(file.filename)
    stored_filename = f"{uuid.uuid4()}{extension}"
    file_path = UPLOAD_DIR / stored_filename

    # Salvar arquivo
    with open(file_path, "wb") as f:
        f.write(contents)

    # Determinar tipo
    file_type = get_file_type(extension)

    return {
        "filename": file.filename,
        "stored_filename": stored_filename,
        "url": f"/api/v1/upload/{stored_filename}",
        "file_type": file_type,
        "size": file_size,
    }


@router.post("/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Upload de múltiplos arquivos

    Retorna lista com informações de cada arquivo enviado
    """
    results = []

    for file in files:
        # Validar extensão
        if not is_allowed_file(file.filename):
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": "File type not allowed"
            })
            continue

        # Ler arquivo
        contents = await file.read()
        file_size = len(contents)

        # Validar tamanho
        if file_size > MAX_FILE_SIZE:
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": "File too large"
            })
            continue

        # Gerar nome único
        extension = get_file_extension(file.filename)
        stored_filename = f"{uuid.uuid4()}{extension}"
        file_path = UPLOAD_DIR / stored_filename

        # Salvar arquivo
        with open(file_path, "wb") as f:
            f.write(contents)

        # Determinar tipo
        file_type = get_file_type(extension)

        results.append({
            "filename": file.filename,
            "stored_filename": stored_filename,
            "url": f"/api/v1/upload/{stored_filename}",
            "file_type": file_type,
            "size": file_size,
            "status": "success"
        })

    return {"files": results}


@router.get("/{filename}")
async def get_file(filename: str):
    """
    Obter arquivo enviado

    - **filename**: Nome do arquivo (stored_filename)

    Retorna o arquivo para download/visualização
    """
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return FileResponse(file_path)


@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user),
):
    """
    Deletar arquivo

    - **filename**: Nome do arquivo (stored_filename)
    """
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    # Deletar arquivo
    os.remove(file_path)

    return None
