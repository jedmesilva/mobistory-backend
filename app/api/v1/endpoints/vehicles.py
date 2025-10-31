from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models import Vehicle, Brand, Model
from app.schemas import (
    Vehicle as VehicleSchema,
    VehicleCreate,
    VehicleUpdate,
    VehicleWithDetails,
)

router = APIRouter()


@router.get("/", response_model=List[VehicleWithDetails])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    entity_id: Optional[str] = Header(None, alias="X-Entity-ID"),
    db: Session = Depends(get_db),
):
    """
    Listar todos os veículos

    - **skip**: Quantos registros pular (paginação)
    - **limit**: Limite de registros retornados
    - **X-Entity-ID**: ID da entidade (opcional, via header)
    """
    vehicles = db.query(Vehicle).offset(skip).limit(limit).all()
    return vehicles


@router.post("/", response_model=VehicleWithDetails, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    entity_id: Optional[str] = Header(None, alias="X-Entity-ID"),
    db: Session = Depends(get_db),
):
    """
    Criar novo veículo

    - **brand_id**: ID da marca
    - **model_id**: ID do modelo
    - **version_id**: ID da versão (opcional)
    - **color_id**: ID da cor (opcional)
    - **year**: Ano do veículo (opcional)
    - **nickname**: Apelido do veículo (opcional)
    - **X-Entity-ID**: ID da entidade (via header)
    """
    # Verificar se brand existe
    brand = db.query(Brand).filter(Brand.id == vehicle_in.brand_id).first()
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found",
        )

    # Verificar se model existe
    model = db.query(Model).filter(Model.id == vehicle_in.model_id).first()
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    # Criar veículo
    vehicle_data = vehicle_in.model_dump()
    if entity_id:
        vehicle_data['entity_id'] = entity_id

    vehicle = Vehicle(**vehicle_data)
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleWithDetails)
def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
):
    """
    Obter um veículo específico por ID

    - **vehicle_id**: ID do veículo
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleWithDetails)
def update_vehicle(
    vehicle_id: str,
    vehicle_in: VehicleUpdate,
    db: Session = Depends(get_db),
):
    """
    Atualizar um veículo existente

    - **vehicle_id**: ID do veículo
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    # Atualizar apenas campos fornecidos
    update_data = vehicle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)

    return vehicle


@router.patch("/{vehicle_id}", response_model=VehicleWithDetails)
def patch_vehicle(
    vehicle_id: str,
    vehicle_in: VehicleUpdate,
    db: Session = Depends(get_db),
):
    """
    Atualizar PARCIALMENTE um veículo

    Permite atualizar apenas os campos fornecidos, sem precisar enviar todos os dados.

    - **vehicle_id**: ID do veículo
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    # Atualizar apenas campos fornecidos (exclude_unset ignora campos não enviados)
    update_data = vehicle_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(vehicle, field, value)

    db.commit()
    db.refresh(vehicle)

    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
):
    """
    Deletar um veículo

    - **vehicle_id**: ID do veículo
    """
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    # Hard delete
    db.delete(vehicle)
    db.commit()

    return None
