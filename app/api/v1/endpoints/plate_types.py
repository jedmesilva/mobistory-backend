from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.vehicle import PlateType
from app.schemas.vehicle import PlateType as PlateTypeSchema

router = APIRouter()


@router.get("/", response_model=List[PlateTypeSchema])
def list_plate_types(
    plate_model_id: str = None,
    vehicle_category: str = None,
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    """
    Listar tipos de placas

    - **plate_model_id**: Filtrar por modelo de placa (UUID)
    - **vehicle_category**: Filtrar por categoria (PRIVATE, COMMERCIAL, OFFICIAL, etc)
    - **active_only**: Se True, retorna apenas tipos ativos (default: True)
    """
    query = db.query(PlateType)

    if active_only:
        query = query.filter(PlateType.active == True)

    if plate_model_id:
        query = query.filter(PlateType.plate_model_id == plate_model_id)

    if vehicle_category:
        query = query.filter(PlateType.vehicle_category == vehicle_category.upper())

    # Ordenar por nome
    query = query.order_by(PlateType.name)

    return query.all()


@router.get("/{plate_type_id}", response_model=PlateTypeSchema)
def get_plate_type(
    plate_type_id: str,
    db: Session = Depends(get_db),
):
    """Obter um tipo de placa específico"""
    plate_type = db.query(PlateType).filter(PlateType.id == plate_type_id).first()

    if not plate_type:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plate type not found",
        )

    return plate_type
