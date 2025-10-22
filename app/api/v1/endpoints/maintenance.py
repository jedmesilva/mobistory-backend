from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.core.database import get_db
from app.models import User, Maintenance, Vehicle
from app.schemas import Maintenance as MaintenanceSchema, MaintenanceCreate, MaintenanceUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[MaintenanceSchema])
def list_maintenances(
    vehicle_id: str = None,
    date_start: date = None,
    date_end: date = None,
    maintenance_type: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar manutenções do usuário

    - **vehicle_id**: Filtrar por veículo (opcional)
    - **date_start**: Data inicial (opcional)
    - **date_end**: Data final (opcional)
    - **maintenance_type**: Tipo de manutenção (opcional)
    """
    # Buscar IDs dos veículos do usuário
    user_vehicle_ids = [v.id for v in db.query(Vehicle.id).filter(Vehicle.user_id == current_user.id).all()]

    query = db.query(Maintenance).filter(Maintenance.vehicle_id.in_(user_vehicle_ids))

    if vehicle_id:
        if vehicle_id not in [str(vid) for vid in user_vehicle_ids]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vehicle does not belong to user",
            )
        query = query.filter(Maintenance.vehicle_id == vehicle_id)

    if date_start:
        query = query.filter(Maintenance.date >= date_start)

    if date_end:
        query = query.filter(Maintenance.date <= date_end)

    if maintenance_type:
        query = query.filter(Maintenance.type == maintenance_type)

    maintenances = query.order_by(Maintenance.date.desc()).offset(skip).limit(limit).all()

    return maintenances


@router.post("/", response_model=MaintenanceSchema, status_code=status.HTTP_201_CREATED)
def create_maintenance(
    maintenance_in: MaintenanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registrar nova manutenção

    - **vehicle_id**: ID do veículo
    - **date**: Data da manutenção
    - **type**: Tipo (oil_change, tire, brake, alignment, etc)
    - **description**: Descrição detalhada (opcional)
    - **cost**: Custo (opcional)
    - **provider**: Oficina/mecânico (opcional)
    - **parts**: Peças trocadas (opcional)
    - **next_due_date**: Próxima manutenção (opcional)
    - **next_due_odometer**: Próxima em km (opcional)
    - **odometer**: Quilometragem (opcional)
    """
    # Verificar se veículo existe e pertence ao usuário
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == maintenance_in.vehicle_id)
        .filter(Vehicle.user_id == current_user.id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or does not belong to user",
        )

    maintenance = Maintenance(**maintenance_in.model_dump())
    db.add(maintenance)
    db.commit()
    db.refresh(maintenance)

    return maintenance


@router.get("/{maintenance_id}", response_model=MaintenanceSchema)
def get_maintenance(
    maintenance_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obter uma manutenção específica"""
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()

    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found",
        )

    # Verificar se veículo pertence ao usuário
    vehicle = db.query(Vehicle).filter(Vehicle.id == maintenance.vehicle_id).first()
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this maintenance record",
        )

    return maintenance


@router.put("/{maintenance_id}", response_model=MaintenanceSchema)
def update_maintenance(
    maintenance_id: str,
    maintenance_in: MaintenanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualizar uma manutenção"""
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()

    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found",
        )

    # Verificar permissão
    vehicle = db.query(Vehicle).filter(Vehicle.id == maintenance.vehicle_id).first()
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this maintenance record",
        )

    update_data = maintenance_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(maintenance, field, value)

    db.commit()
    db.refresh(maintenance)

    return maintenance


@router.delete("/{maintenance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_maintenance(
    maintenance_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletar uma manutenção"""
    maintenance = db.query(Maintenance).filter(Maintenance.id == maintenance_id).first()

    if not maintenance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maintenance record not found",
        )

    # Verificar permissão
    vehicle = db.query(Vehicle).filter(Vehicle.id == maintenance.vehicle_id).first()
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this maintenance record",
        )

    db.delete(maintenance)
    db.commit()

    return None
