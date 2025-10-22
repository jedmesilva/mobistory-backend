from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import User, Vehicle, Brand, Model
from app.schemas import (
    Vehicle as VehicleSchema,
    VehicleCreate,
    VehicleUpdate,
    VehicleWithDetails,
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[VehicleWithDetails])
def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar todos os veículos do usuário autenticado

    - **skip**: Quantos registros pular (paginação)
    - **limit**: Limite de registros retornados
    """
    vehicles = (
        db.query(Vehicle)
        .filter(Vehicle.user_id == current_user.id)
        .filter(Vehicle.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return vehicles


@router.post("/", response_model=VehicleWithDetails, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Criar novo veículo para o usuário autenticado

    - **brand_id**: ID da marca
    - **model_id**: ID do modelo
    - **version_id**: ID da versão (opcional)
    - **color_id**: ID da cor (opcional)
    - **year**: Ano do veículo (opcional)
    - **nickname**: Apelido do veículo (opcional)
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
    vehicle = Vehicle(
        **vehicle_in.model_dump(),
        user_id=current_user.id,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleWithDetails)
def get_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter um veículo específico por ID
    """
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .filter(Vehicle.user_id == current_user.id)
        .first()
    )

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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar um veículo existente
    """
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .filter(Vehicle.user_id == current_user.id)
        .first()
    )

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


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletar (desativar) um veículo

    Na verdade faz soft delete, apenas marca como is_active=False
    """
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .filter(Vehicle.user_id == current_user.id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    # Soft delete
    vehicle.is_active = False
    db.commit()

    return None
