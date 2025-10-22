from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.core.database import get_db
from app.models import User, Fueling, Vehicle
from app.schemas import Fueling as FuelingSchema, FuelingCreate, FuelingUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[FuelingSchema])
def list_fuelings(
    vehicle_id: str = None,
    date_start: date = None,
    date_end: date = None,
    fuel_type: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar abastecimentos do usuário

    - **vehicle_id**: Filtrar por veículo (opcional)
    - **date_start**: Data inicial (opcional)
    - **date_end**: Data final (opcional)
    - **fuel_type**: Tipo de combustível (opcional)
    """
    # Buscar IDs dos veículos do usuário
    user_vehicle_ids = [v.id for v in db.query(Vehicle.id).filter(Vehicle.user_id == current_user.id).all()]

    query = db.query(Fueling).filter(Fueling.vehicle_id.in_(user_vehicle_ids))

    if vehicle_id:
        # Verificar se veículo pertence ao usuário
        if vehicle_id not in [str(vid) for vid in user_vehicle_ids]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vehicle does not belong to user",
            )
        query = query.filter(Fueling.vehicle_id == vehicle_id)

    if date_start:
        query = query.filter(Fueling.date >= date_start)

    if date_end:
        query = query.filter(Fueling.date <= date_end)

    if fuel_type:
        query = query.filter(Fueling.fuel_type == fuel_type)

    fuelings = query.order_by(Fueling.date.desc()).offset(skip).limit(limit).all()

    return fuelings


@router.post("/", response_model=FuelingSchema, status_code=status.HTTP_201_CREATED)
def create_fueling(
    fueling_in: FuelingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Registrar novo abastecimento

    - **vehicle_id**: ID do veículo
    - **date**: Data do abastecimento
    - **fuel_type**: Tipo de combustível (gasolina, etanol, diesel, gnv)
    - **liters**: Litros abastecidos
    - **price_per_liter**: Preço por litro
    - **total_price**: Preço total
    - **tank_filled**: Tanque cheio? (true/false)
    - **station_name**: Nome do posto (opcional)
    - **odometer**: Quilometragem (opcional)
    - **notes**: Observações (opcional)
    """
    # Verificar se veículo existe e pertence ao usuário
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == fueling_in.vehicle_id)
        .filter(Vehicle.user_id == current_user.id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or does not belong to user",
        )

    fueling = Fueling(**fueling_in.model_dump())
    db.add(fueling)
    db.commit()
    db.refresh(fueling)

    return fueling


@router.get("/{fueling_id}", response_model=FuelingSchema)
def get_fueling(
    fueling_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obter um abastecimento específico"""
    fueling = db.query(Fueling).filter(Fueling.id == fueling_id).first()

    if not fueling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fueling record not found",
        )

    # Verificar se veículo pertence ao usuário
    vehicle = db.query(Vehicle).filter(Vehicle.id == fueling.vehicle_id).first()
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this fueling record",
        )

    return fueling


@router.put("/{fueling_id}", response_model=FuelingSchema)
def update_fueling(
    fueling_id: str,
    fueling_in: FuelingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atualizar um abastecimento"""
    fueling = db.query(Fueling).filter(Fueling.id == fueling_id).first()

    if not fueling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fueling record not found",
        )

    # Verificar permissão
    vehicle = db.query(Vehicle).filter(Vehicle.id == fueling.vehicle_id).first()
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this fueling record",
        )

    update_data = fueling_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(fueling, field, value)

    db.commit()
    db.refresh(fueling)

    return fueling


@router.delete("/{fueling_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fueling(
    fueling_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletar um abastecimento"""
    fueling = db.query(Fueling).filter(Fueling.id == fueling_id).first()

    if not fueling:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fueling record not found",
        )

    # Verificar permissão
    vehicle = db.query(Vehicle).filter(Vehicle.id == fueling.vehicle_id).first()
    if vehicle.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this fueling record",
        )

    db.delete(fueling)
    db.commit()

    return None
