from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, date
import uuid
from app.core.database import get_db
from app.models import Vehicle, Brand, Model, Plate, PlateType, Color, VehicleColor, Link, LinkType, VehicleCover
from app.schemas import (
    Vehicle as VehicleSchema,
    VehicleCreate,
    VehicleUpdate,
    VehicleWithDetails,
)
from app.services.entity_service import VehicleEntityLinkService
from app.schemas.entity import (
    VehicleLinksResponse,
    VehicleEntityLinkWithEntity,
    LinkStatus,
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
    # Carregar relacionamentos com eager loading
    vehicles = (
        db.query(Vehicle)
        .options(
            joinedload(Vehicle.brand),
            joinedload(Vehicle.model),
            joinedload(Vehicle.version),
            joinedload(Vehicle.plates),
            joinedload(Vehicle.vehicle_colors).joinedload(VehicleColor.color),
            joinedload(Vehicle.covers),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return vehicles


@router.post("/", response_model=VehicleWithDetails, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    entity_id: Optional[str] = Header(None, alias="X-Entity-ID"),
    db: Session = Depends(get_db),
):
    """
    Criar novo veículo

    Requer brand_id e model_id do catálogo. version_id é opcional.

    Opcionalmente cria:
    - Registro de placa (se plate_number fornecido)
    - Registro de cor (se color fornecido)
    - Link com entidade (se entity_id fornecido)

    Tudo em uma única transação.
    """
    print("=== CREATE_VEHICLE CHAMADO ===")
    print(f"Dados recebidos: {vehicle_in.model_dump()}")
    try:
        # Extrair campos específicos que não vão direto para o veículo
        vehicle_data = vehicle_in.model_dump(exclude={
            'plate_number', 'plate_type_id', 'plate_model_id', 'licensing_start_date',
            'licensing_end_date', 'licensing_country', 'plate_state', 'plate_city', 'color_id',
            'entity_id', 'link_type_id'
        })
        print(f">>> [Backend] Dados do veículo após exclusão: {vehicle_data}")

        # Limpar campos None que não devem ser passados ao Vehicle
        vehicle_data = {k: v for k, v in vehicle_data.items() if v is not None}
        print(f">>> [Backend] Dados do veículo após limpeza de None: {vehicle_data}")

        # Validar brand_id (obrigatório)
        print(f">>> [Backend] Validando brand_id: {vehicle_data.get('brand_id')}")
        if not vehicle_data.get('brand_id'):
            print("❌ [Backend] brand_id não fornecido")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="brand_id is required"
            )

        # Validar se brand existe
        brand = db.query(Brand).filter(Brand.id == vehicle_data['brand_id']).first()
        if not brand:
            print(f"❌ [Backend] Brand não encontrada: {vehicle_data['brand_id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Brand with id {vehicle_data['brand_id']} not found"
            )
        print(f"✓ [Backend] Brand encontrada: {brand.name}")

        # Validar model_id (obrigatório)
        print(f">>> [Backend] Validando model_id: {vehicle_data.get('model_id')}")
        if not vehicle_data.get('model_id'):
            print("❌ [Backend] model_id não fornecido")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="model_id is required"
            )

        # Validar se model existe
        model = db.query(Model).filter(Model.id == vehicle_data['model_id']).first()
        if not model:
            print(f"❌ [Backend] Model não encontrado: {vehicle_data['model_id']}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model with id {vehicle_data['model_id']} not found"
            )
        print(f"✓ [Backend] Model encontrado: {model.name}")

        # 1. Criar veículo
        print(">>> [Backend] [1/4] Criando registro de veículo...")
        vehicle = Vehicle(**vehicle_data)
        db.add(vehicle)
        db.flush()  # Flush para obter o ID do veículo sem commitar
        print(f"✓ [Backend] Veículo criado com ID: {vehicle.id}")

        # 2. Criar placa se fornecida
        if vehicle_in.plate_number:
            print(f">>> [Backend] [2/4] Criando placa: {vehicle_in.plate_number}")
            if not vehicle_in.plate_type_id:
                print("❌ [Backend] plate_type_id não fornecido")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="plate_type_id is required when plate_number is provided"
                )

            # Validar se plate_type existe
            print(f">>> [Backend] Validando plate_type_id: {vehicle_in.plate_type_id}")
            plate_type = db.query(PlateType).filter(PlateType.id == vehicle_in.plate_type_id).first()
            if not plate_type:
                print(f"❌ [Backend] PlateType não encontrado: {vehicle_in.plate_type_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"PlateType with id {vehicle_in.plate_type_id} not found"
                )
            print(f"✓ [Backend] PlateType encontrado: {plate_type.name}")

            plate = Plate(
                vehicle_id=vehicle.id,
                plate_type_id=vehicle_in.plate_type_id,
                plate_model_id=vehicle_in.plate_model_id if vehicle_in.plate_model_id else None,
                plate_number=vehicle_in.plate_number,
                licensing_start_date=vehicle_in.licensing_start_date,
                licensing_end_date=vehicle_in.licensing_end_date,
                licensing_country=vehicle_in.licensing_country,
                state=vehicle_in.plate_state,
                city=vehicle_in.plate_city,
                status="active",
                active=True,
                created_by_entity_id=vehicle_in.entity_id if vehicle_in.entity_id else None
            )
            db.add(plate)
            print(f"✓ [Backend] Placa criada")

            # Atualizar current_plate do veículo
            vehicle.current_plate = vehicle_in.plate_number
        else:
            print(">>> [Backend] [2/4] Nenhuma placa fornecida, pulando...")

        # 3. Criar relacionamento veículo-cor se fornecido
        if vehicle_in.color_id:
            print(f">>> [Backend] [3/4] Criando relacionamento com cor: {vehicle_in.color_id}")
            # Validar se color existe
            color = db.query(Color).filter(Color.id == vehicle_in.color_id).first()
            if not color:
                print(f"❌ [Backend] Color não encontrada: {vehicle_in.color_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Color with id {vehicle_in.color_id} not found"
                )
            print(f"✓ [Backend] Color encontrada: {color.name}")

            vehicle_color = VehicleColor(
                vehicle_id=vehicle.id,
                color_id=vehicle_in.color_id,
                is_primary=True
            )
            db.add(vehicle_color)
            print(f"✓ [Backend] VehicleColor criado")

            # Atualizar current_color do veículo com o nome da cor
            vehicle.current_color = color.name
        else:
            print(">>> [Backend] [3/4] Nenhuma cor fornecida, pulando...")

        # 4. Criar link com entidade se fornecido
        if vehicle_in.entity_id:
            print(f">>> [Backend] [4/4] Criando link com entidade: {vehicle_in.entity_id}")
            if not vehicle_in.link_type_id:
                print("❌ [Backend] link_type_id não fornecido")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="link_type_id is required when entity_id is provided"
                )

            # Validar se link_type existe
            link_type = db.query(LinkType).filter(LinkType.id == vehicle_in.link_type_id).first()
            if not link_type:
                print(f"❌ [Backend] LinkType não encontrado: {vehicle_in.link_type_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"LinkType with id {vehicle_in.link_type_id} not found"
                )
            print(f"✓ [Backend] LinkType encontrado: {link_type.name}")

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
            print(f"✓ [Backend] Link criado com código: {link_code}")
        else:
            print(">>> [Backend] [4/4] Nenhum link com entidade fornecido, pulando...")

        # Commit de toda a transação
        print(">>> [Backend] Commitando transação no banco de dados...")
        db.commit()
        print("✓✓✓ [Backend] VEÍCULO CRIADO COM SUCESSO ✓✓✓")

        # Recarregar veículo sem eager loading dos relationships
        db.expire(vehicle)

        return vehicle

    except HTTPException:
        print(f"❌ [Backend] HTTPException capturada, fazendo rollback")
        db.rollback()
        raise
    except Exception as e:
        print(f"❌❌❌ [Backend] ERRO INESPERADO ❌❌❌")
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print(f"Stack trace completa:")
        import traceback
        traceback.print_exc()
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
    vehicle = (
        db.query(Vehicle)
        .options(
            joinedload(Vehicle.brand),
            joinedload(Vehicle.model),
            joinedload(Vehicle.version),
            joinedload(Vehicle.plates),
            joinedload(Vehicle.vehicle_colors).joinedload(VehicleColor.color),
            joinedload(Vehicle.covers),
        )
        .filter(Vehicle.id == vehicle_id)
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


@router.get("/{vehicle_id}/links", response_model=VehicleLinksResponse)
def get_vehicle_links(
    vehicle_id: uuid.UUID,
    status: Optional[LinkStatus] = Query(None),
    link_type_id: Optional[uuid.UUID] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all links for a vehicle"""
    service = VehicleEntityLinkService(db)
    links = service.get_vehicle_links(
        vehicle_id=vehicle_id,
        status=status,
        link_type_id=link_type_id,
        active_only=active_only
    )

    active_count = service.get_active_vehicle_links_count(vehicle_id)

    return VehicleLinksResponse(
        vehicle_id=vehicle_id,
        links=[VehicleEntityLinkWithEntity.from_orm(link) for link in links],
        active_count=active_count,
        total_count=len(links)
    )
