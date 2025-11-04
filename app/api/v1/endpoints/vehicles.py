from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.core.database import get_db
from app.models import Vehicle, Brand, Model, Plate, PlateType, Color, Link, LinkType
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
    Criar novo veículo com suporte para catalog ou custom fields

    Pode usar brand_id/model_id/version_id (catálogo) OU custom_brand/custom_model/custom_version

    Opcionalmente cria:
    - Registro de placa (se plate_number fornecido)
    - Registro de cor (se color fornecido)
    - Link com entidade (se entity_id fornecido)

    Tudo em uma única transação.
    """
    print("=== CREATE_VEHICLE CHAMADO ===")
    try:
        # Extrair campos específicos que não vão direto para o veículo
        vehicle_data = vehicle_in.model_dump(exclude={
            'plate_number', 'plate_type_id', 'licensing_date', 'licensing_country',
            'plate_state', 'plate_city', 'color', 'hex_code', 'color_description',
            'entity_id', 'link_type_id'
        })

        # Limpar campos None que não devem ser passados ao Vehicle
        vehicle_data = {k: v for k, v in vehicle_data.items() if v is not None}

        # Validar lógica de brand: ou usa catalog OU custom
        if vehicle_data.get('brand_id'):
            # Validar se brand existe
            brand = db.query(Brand).filter(Brand.id == vehicle_data['brand_id']).first()
            if not brand:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Brand with id {vehicle_data['brand_id']} not found"
                )
        elif not vehicle_data.get('custom_brand'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either brand_id or custom_brand must be provided"
            )

        # Validar lógica de model: ou usa catalog OU custom
        if vehicle_data.get('model_id'):
            # Validar se model existe
            model = db.query(Model).filter(Model.id == vehicle_data['model_id']).first()
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Model with id {vehicle_data['model_id']} not found"
                )
        elif not vehicle_data.get('custom_model'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either model_id or custom_model must be provided"
            )

        # 1. Criar veículo
        vehicle = Vehicle(**vehicle_data)
        db.add(vehicle)
        db.flush()  # Flush para obter o ID do veículo sem commitar

        # 2. Criar placa se fornecida
        if vehicle_in.plate_number:
            if not vehicle_in.plate_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="plate_type_id is required when plate_number is provided"
                )

            # Validar se plate_type existe
            plate_type = db.query(PlateType).filter(PlateType.id == vehicle_in.plate_type_id).first()
            if not plate_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"PlateType with id {vehicle_in.plate_type_id} not found"
                )

            plate = Plate(
                vehicle_id=vehicle.id,
                plate_type_id=vehicle_in.plate_type_id,
                plate_number=vehicle_in.plate_number,
                licensing_date=vehicle_in.licensing_date,
                licensing_country=vehicle_in.licensing_country,
                state=vehicle_in.plate_state,
                city=vehicle_in.plate_city,
                status="active",
                active=True,
                created_by_entity_id=vehicle_in.entity_id if vehicle_in.entity_id else None
            )
            db.add(plate)

            # Atualizar current_plate do veículo
            vehicle.current_plate = vehicle_in.plate_number

        # 3. Criar cor se fornecida
        if vehicle_in.color:
            color = Color(
                vehicle_id=vehicle.id,
                color=vehicle_in.color,
                hex_code=vehicle_in.hex_code,
                description=vehicle_in.color_description,
                start_date=date.today(),
                active=True,
                created_by_entity_id=vehicle_in.entity_id if vehicle_in.entity_id else None
            )
            db.add(color)

            # Atualizar current_color do veículo
            vehicle.current_color = vehicle_in.color

        # 4. Criar link com entidade se fornecido
        if vehicle_in.entity_id:
            if not vehicle_in.link_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="link_type_id is required when entity_id is provided"
                )

            # Validar se link_type existe
            link_type = db.query(LinkType).filter(LinkType.id == vehicle_in.link_type_id).first()
            if not link_type:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LinkType with id {vehicle_in.link_type_id} not found"
                )

            # Gerar link_code único
            import uuid
            link_code = f"LNK-{uuid.uuid4().hex[:12].upper()}"

            link = Link(
                link_code=link_code,
                entity_id=vehicle_in.entity_id,
                vehicle_id=vehicle.id,
                link_type_id=vehicle_in.link_type_id,
                status="active",
                start_date=date.today()
            )
            db.add(link)

        # Commit de toda a transação
        db.commit()

        # Recarregar veículo sem eager loading dos relationships
        db.expire(vehicle)

        return vehicle

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating vehicle: {str(e)}"
        )


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
