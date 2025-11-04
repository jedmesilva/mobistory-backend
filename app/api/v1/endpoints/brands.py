from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Brand, Model, ModelVersion
from app.schemas import (
    Brand as BrandSchema,
    BrandCreate,
    BrandUpdate,
    Model as ModelSchema,
    ModelCreate,
    ModelUpdate,
    ModelVersion as ModelVersionSchema,
    ModelVersionCreate,
    ModelVersionUpdate,
)

router = APIRouter()


# ═══════════════════════════════════════════════════════
# BRANDS - /api/v1/brands
# ═══════════════════════════════════════════════════════

@router.get("/", response_model=List[BrandSchema])
def list_brands(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    """
    Listar todas as marcas de veículos

    - **active_only**: Se True, retorna apenas marcas ativas (default: True)
    - **verified_only**: Se True, retorna apenas marcas verificadas (default: False)
    - **skip**: Quantos registros pular (paginação)
    - **limit**: Limite de registros retornados
    """
    query = db.query(Brand)

    if active_only:
        query = query.filter(Brand.active == True)

    if verified_only:
        query = query.filter(Brand.verified == True)

    brands = query.offset(skip).limit(limit).all()
    return brands


@router.post("/", response_model=BrandSchema, status_code=status.HTTP_201_CREATED)
def create_brand(
    brand_in: BrandCreate,
    db: Session = Depends(get_db),
):
    """
    Criar nova marca

    - **name**: Nome da marca (obrigatório)
    - **country_of_origin**: País de origem (opcional)
    - **logo_url**: URL do logo (opcional)
    """
    # Verificar se marca já existe (case-insensitive)
    existing = db.query(Brand).filter(
        Brand.name.ilike(brand_in.name)
    ).first()

    if existing:
        # Se existir mas estiver inativa, reativar
        if not existing.active:
            existing.active = True
            existing.country_of_origin = brand_in.country_of_origin
            existing.logo_url = brand_in.logo_url
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Brand '{brand_in.name}' already exists",
            )

    brand = Brand(**brand_in.model_dump())
    db.add(brand)
    db.commit()
    db.refresh(brand)

    return brand


@router.get("/{brand_id}", response_model=BrandSchema)
def get_brand(
    brand_id: str,
    db: Session = Depends(get_db),
):
    """Obter uma marca específica por ID"""
    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    return brand


@router.patch("/{brand_id}", response_model=BrandSchema)
def update_brand(
    brand_id: str,
    brand_in: BrandUpdate,
    db: Session = Depends(get_db),
):
    """
    Atualizar uma marca existente (parcial)

    Permite atualizar apenas os campos fornecidos
    """
    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    # Atualizar apenas campos fornecidos
    update_data = brand_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(brand, field, value)

    db.commit()
    db.refresh(brand)

    return brand


@router.delete("/{brand_id}", status_code=status.HTTP_200_OK)
def delete_brand(
    brand_id: str,
    db: Session = Depends(get_db),
):
    """
    Deletar uma marca (soft delete)

    Marca como inativa ao invés de remover do banco de dados
    """
    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    # Soft delete - marca como inativa
    brand.active = False
    db.commit()

    return {"message": f"Brand '{brand.name}' marked as inactive"}


# ═══════════════════════════════════════════════════════
# MODELS - /api/v1/brands/{brand_id}/models
# ═══════════════════════════════════════════════════════

@router.get("/{brand_id}/models", response_model=List[ModelSchema])
def list_models_by_brand(
    brand_id: str,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    """
    Listar modelos de uma marca específica

    - **brand_id**: ID da marca
    - **active_only**: Se True, retorna apenas modelos ativos (default: True)
    - **verified_only**: Se True, retorna apenas modelos verificados (default: False)
    - **skip**: Quantos registros pular (paginação)
    - **limit**: Limite de registros retornados
    """
    # Verificar se marca existe
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    query = db.query(Model).filter(Model.brand_id == brand_id)

    if active_only:
        query = query.filter(Model.active == True)

    if verified_only:
        query = query.filter(Model.verified == True)

    models = query.offset(skip).limit(limit).all()
    return models


@router.post("/{brand_id}/models", response_model=ModelSchema, status_code=status.HTTP_201_CREATED)
def create_model_for_brand(
    brand_id: str,
    model_in: ModelCreate,
    db: Session = Depends(get_db),
):
    """
    Criar novo modelo para uma marca específica

    - **name**: Nome do modelo (obrigatório)
    - **category**: Categoria do veículo (opcional)

    O brand_id será obtido da URL automaticamente
    """
    # Verificar se brand existe
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    # Sobrescrever brand_id do body com o da URL (segurança)
    model_data = model_in.model_dump()
    model_data['brand_id'] = brand_id

    # Verificar se modelo já existe para esta marca
    existing = db.query(Model).filter(
        Model.brand_id == brand_id,
        Model.name.ilike(model_in.name)
    ).first()

    if existing:
        # Se existir mas estiver inativo, reativar
        if not existing.active:
            existing.active = True
            existing.category = model_in.category
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Model '{model_in.name}' already exists for this brand",
            )

    model = Model(**model_data)
    db.add(model)
    db.commit()
    db.refresh(model)

    return model


@router.get("/{brand_id}/models/{model_id}", response_model=ModelSchema)
def get_model(
    brand_id: str,
    model_id: str,
    db: Session = Depends(get_db),
):
    """Obter um modelo específico de uma marca"""
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    return model


@router.patch("/{brand_id}/models/{model_id}", response_model=ModelSchema)
def update_model(
    brand_id: str,
    model_id: str,
    model_in: ModelUpdate,
    db: Session = Depends(get_db),
):
    """
    Atualizar um modelo existente (parcial)

    Permite atualizar apenas os campos fornecidos
    """
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    # Atualizar apenas campos fornecidos
    update_data = model_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(model, field, value)

    db.commit()
    db.refresh(model)

    return model


@router.delete("/{brand_id}/models/{model_id}", status_code=status.HTTP_200_OK)
def delete_model(
    brand_id: str,
    model_id: str,
    db: Session = Depends(get_db),
):
    """
    Deletar um modelo (soft delete)

    Marca como inativo ao invés de remover do banco de dados
    """
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    # Soft delete - marca como inativo
    model.active = False
    db.commit()

    return {"message": f"Model '{model.name}' marked as inactive"}


# ═══════════════════════════════════════════════════════
# VERSIONS - /api/v1/brands/{brand_id}/models/{model_id}/versions
# ═══════════════════════════════════════════════════════

@router.get("/{brand_id}/models/{model_id}/versions", response_model=List[ModelVersionSchema])
def list_versions_by_model(
    brand_id: str,
    model_id: str,
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    verified_only: bool = False,
    db: Session = Depends(get_db),
):
    """
    Listar versões de um modelo específico

    - **brand_id**: ID da marca
    - **model_id**: ID do modelo
    - **active_only**: Se True, retorna apenas versões ativas (default: True)
    - **verified_only**: Se True, retorna apenas versões verificadas (default: False)
    - **skip**: Quantos registros pular (paginação)
    - **limit**: Limite de registros retornados
    """
    # Verificar se modelo existe e pertence à marca
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    query = db.query(ModelVersion).filter(ModelVersion.model_id == model_id)

    if active_only:
        query = query.filter(ModelVersion.active == True)

    if verified_only:
        query = query.filter(ModelVersion.verified == True)

    versions = query.offset(skip).limit(limit).all()
    return versions


@router.post("/{brand_id}/models/{model_id}/versions", response_model=ModelVersionSchema, status_code=status.HTTP_201_CREATED)
def create_version_for_model(
    brand_id: str,
    model_id: str,
    version_in: ModelVersionCreate,
    db: Session = Depends(get_db),
):
    """
    Criar nova versão para um modelo específico

    - **name**: Nome da versão (obrigatório)
    - Campos opcionais: fuel_type, transmission, engine_power, etc.

    O model_id será obtido da URL automaticamente
    """
    # Verificar se modelo existe e pertence à marca
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    # Sobrescrever model_id do body com o da URL (segurança)
    version_data = version_in.model_dump()
    version_data['model_id'] = model_id

    # Verificar se versão já existe para este modelo
    existing = db.query(ModelVersion).filter(
        ModelVersion.model_id == model_id,
        ModelVersion.name.ilike(version_in.name)
    ).first()

    if existing:
        # Se existir mas estiver inativa, reativar
        if not existing.active:
            existing.active = True
            # Atualizar outros campos
            update_data = version_in.model_dump(exclude={'model_id', 'name'})
            for field, value in update_data.items():
                setattr(existing, field, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Version '{version_in.name}' already exists for this model",
            )

    version = ModelVersion(**version_data)
    db.add(version)
    db.commit()
    db.refresh(version)

    return version


@router.get("/{brand_id}/models/{model_id}/versions/{version_id}", response_model=ModelVersionSchema)
def get_version(
    brand_id: str,
    model_id: str,
    version_id: str,
    db: Session = Depends(get_db),
):
    """Obter uma versão específica de um modelo"""
    # Verificar hierarquia completa
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    version = db.query(ModelVersion).filter(
        ModelVersion.id == version_id,
        ModelVersion.model_id == model_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found for this model",
        )

    return version


@router.patch("/{brand_id}/models/{model_id}/versions/{version_id}", response_model=ModelVersionSchema)
def update_version(
    brand_id: str,
    model_id: str,
    version_id: str,
    version_in: ModelVersionUpdate,
    db: Session = Depends(get_db),
):
    """
    Atualizar uma versão existente (parcial)

    Permite atualizar apenas os campos fornecidos
    """
    # Verificar hierarquia completa
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    version = db.query(ModelVersion).filter(
        ModelVersion.id == version_id,
        ModelVersion.model_id == model_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found for this model",
        )

    # Atualizar apenas campos fornecidos
    update_data = version_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(version, field, value)

    db.commit()
    db.refresh(version)

    return version


@router.delete("/{brand_id}/models/{model_id}/versions/{version_id}", status_code=status.HTTP_200_OK)
def delete_version(
    brand_id: str,
    model_id: str,
    version_id: str,
    db: Session = Depends(get_db),
):
    """
    Deletar uma versão (soft delete)

    Marca como inativa ao invés de remover do banco de dados
    """
    # Verificar hierarquia completa
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    version = db.query(ModelVersion).filter(
        ModelVersion.id == version_id,
        ModelVersion.model_id == model_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found for this model",
        )

    # Soft delete - marca como inativa
    version.active = False
    db.commit()

    return {"message": f"Version '{version.name}' marked as inactive"}


# ═══════════════════════════════════════════════════════
# ADMIN: Verificação (Marcar como verificado)
# ═══════════════════════════════════════════════════════

@router.patch("/{brand_id}/verify", response_model=BrandSchema)
def verify_brand(
    brand_id: str,
    verified: bool = True,
    db: Session = Depends(get_db),
):
    """
    Marcar uma marca como verificada (Admin)

    - **brand_id**: ID da marca
    - **verified**: True para verificar, False para remover verificação
    """
    brand = db.query(Brand).filter(Brand.id == brand_id).first()

    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    brand.verified = verified
    db.commit()
    db.refresh(brand)

    action = "verified" if verified else "unverified"
    return brand


@router.patch("/{brand_id}/models/{model_id}/verify", response_model=ModelSchema)
def verify_model(
    brand_id: str,
    model_id: str,
    verified: bool = True,
    db: Session = Depends(get_db),
):
    """
    Marcar um modelo como verificado (Admin)

    - **brand_id**: ID da marca
    - **model_id**: ID do modelo
    - **verified**: True para verificar, False para remover verificação
    """
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    model.verified = verified
    db.commit()
    db.refresh(model)

    return model


@router.patch("/{brand_id}/models/{model_id}/versions/{version_id}/verify", response_model=ModelVersionSchema)
def verify_version(
    brand_id: str,
    model_id: str,
    version_id: str,
    verified: bool = True,
    db: Session = Depends(get_db),
):
    """
    Marcar uma versão como verificada (Admin)

    - **brand_id**: ID da marca
    - **model_id**: ID do modelo
    - **version_id**: ID da versão
    - **verified**: True para verificar, False para remover verificação
    """
    # Verificar hierarquia completa
    model = db.query(Model).filter(
        Model.id == model_id,
        Model.brand_id == brand_id
    ).first()

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found for this brand",
        )

    version = db.query(ModelVersion).filter(
        ModelVersion.id == version_id,
        ModelVersion.model_id == model_id
    ).first()

    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Version not found for this model",
        )

    version.verified = verified
    db.commit()
    db.refresh(version)

    return version
