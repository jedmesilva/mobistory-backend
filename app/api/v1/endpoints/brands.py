from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import Brand, Model, ModelVersion
from app.schemas import (
    Brand as BrandSchema,
    BrandCreate,
    Model as ModelSchema,
    ModelCreate,
    ModelVersion as ModelVersionSchema,
    ModelVersionCreate,
)

router = APIRouter()


# ═══════════════════════════════════════════════════════
# BRANDS
# ═══════════════════════════════════════════════════════

@router.get("/brands", response_model=List[BrandSchema])
def list_brands(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Listar todas as marcas de veículos

    Endpoint público - não requer autenticação
    """
    brands = db.query(Brand).offset(skip).limit(limit).all()
    return brands


@router.post("/brands", response_model=BrandSchema, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
):
    """
    Criar nova marca

    Endpoint público - não requer autenticação
    """
    # Verificar se marca já existe
    existing = db.query(Brand).filter(Brand.brand == brand_in.brand).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand already exists",
        )

    brand = Brand(**brand_in.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)

    return brand


@router.get("/brands/{brand_id}", response_model=BrandSchema)
def get_brand(
    brand_id: str,
    db: Session = Depends(get_db),
):
    """Obter uma marca específica"""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    return brand


# ═══════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════

@router.get("/models", response_model=List[ModelSchema])
def list_models(
    brand_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Listar modelos de veículos

    - **brand_id**: Filtrar por marca (opcional)
    """
    query = db.query(Model)

    if brand_id:
        query = query.filter(Model.brand_id == brand_id)

    models = query.offset(skip).limit(limit).all()
    return models


@router.post("/models", response_model=ModelSchema, status_code=status.HTTP_201_CREATED)
def create_model(
    model_in: ModelCreate,
    db: Session = Depends(get_db),
):
    """Criar novo modelo"""
    # Verificar se brand existe
    brand = db.query(Brand).filter(Brand.id == model_in.brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    model = Model(**model_in.model_dump())
    db.add(model)
    db.commit()
    db.refresh(model)

    return model


@router.get("/models/{model_id}", response_model=ModelSchema)
def get_model(
    model_id: str,
    db: Session = Depends(get_db),
):
    """Obter um modelo específico"""
    model = db.query(Model).filter(Model.id == model_id).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    return model


# ═══════════════════════════════════════════════════════
# MODEL VERSIONS
# ═══════════════════════════════════════════════════════

@router.get("/versions", response_model=List[ModelVersionSchema])
def list_versions(
    model_id: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Listar versões de modelos

    - **model_id**: Filtrar por modelo (opcional)
    """
    query = db.query(ModelVersion)

    if model_id:
        query = query.filter(ModelVersion.model_id == model_id)

    versions = query.offset(skip).limit(limit).all()
    return versions


@router.post("/versions", response_model=ModelVersionSchema, status_code=status.HTTP_201_CREATED)
def create_version(
    version_in: ModelVersionCreate,
    db: Session = Depends(get_db),
):
    """Criar nova versão de modelo"""
    # Verificar se model existe
    model = db.query(Model).filter(Model.id == version_in.model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    version = ModelVersion(**version_in.model_dump())
    db.add(version)
    db.commit()
    db.refresh(version)

    return version


@router.get("/versions/{version_id}", response_model=ModelVersionSchema)
def get_version(
    version_id: str,
    db: Session = Depends(get_db),
):
    """Obter uma versão específica"""
    version = db.query(ModelVersion).filter(ModelVersion.id == version_id).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found",
        )

    return version
