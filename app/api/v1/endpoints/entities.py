from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.services.entity_service import EntityService, VehicleEntityLinkService
from app.schemas.entity import (
    Entity,
    EntityCreate,
    EntityUpdate,
    VehicleEntityLink,
    VehicleEntityLinkCreate,
    VehicleEntityLinkUpdate,
    VehicleEntityLinkWithEntity,
    VehicleLinksResponse,
    LinkStatus,
    RelationshipType
)

router = APIRouter()


# Entity endpoints
@router.post("/entities", response_model=Entity)
def create_entity(
    entity: EntityCreate,
    db: Session = Depends(get_db)
):
    """Create a new entity"""
    service = EntityService(db)
    return service.create_entity(entity)


@router.get("/entities", response_model=List[Entity])
def get_entities(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Get all entities with pagination"""
    service = EntityService(db)
    return service.get_entities(skip=skip, limit=limit)


@router.get("/entities/{entity_id}", response_model=Entity)
def get_entity(
    entity_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get entity by ID"""
    service = EntityService(db)
    entity = service.get_entity(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.put("/entities/{entity_id}", response_model=Entity)
def update_entity(
    entity_id: uuid.UUID,
    entity_update: EntityUpdate,
    db: Session = Depends(get_db)
):
    """Update entity"""
    service = EntityService(db)
    entity = service.update_entity(entity_id, entity_update)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.delete("/entities/{entity_id}")
def delete_entity(
    entity_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Delete entity"""
    service = EntityService(db)
    if not service.delete_entity(entity_id):
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"message": "Entity deleted successfully"}


# Vehicle Entity Link endpoints
@router.post("/vehicle-links", response_model=VehicleEntityLink)
def create_vehicle_link(
    link: VehicleEntityLinkCreate,
    db: Session = Depends(get_db)
):
    """Create a new vehicle-entity link"""
    service = VehicleEntityLinkService(db)
    return service.create_link(link)


@router.get("/vehicles/{vehicle_id}/links", response_model=VehicleLinksResponse)
def get_vehicle_links(
    vehicle_id: uuid.UUID,
    status: Optional[LinkStatus] = Query(None),
    relationship_type: Optional[RelationshipType] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all links for a vehicle"""
    service = VehicleEntityLinkService(db)
    links = service.get_vehicle_links(
        vehicle_id=vehicle_id,
        status=status,
        relationship_type=relationship_type,
        active_only=active_only
    )
    
    active_count = service.get_active_vehicle_links_count(vehicle_id)
    
    return VehicleLinksResponse(
        vehicle_id=vehicle_id,
        links=[VehicleEntityLinkWithEntity.from_orm(link) for link in links],
        active_count=active_count,
        total_count=len(links)
    )


@router.get("/entities/{entity_id}/links", response_model=List[VehicleEntityLink])
def get_entity_links(
    entity_id: uuid.UUID,
    status: Optional[LinkStatus] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all links for an entity"""
    service = VehicleEntityLinkService(db)
    return service.get_entity_links(
        entity_id=entity_id,
        status=status,
        active_only=active_only
    )


@router.get("/vehicle-links/{link_id}", response_model=VehicleEntityLinkWithEntity)
def get_vehicle_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get vehicle-entity link by ID"""
    service = VehicleEntityLinkService(db)
    link = service.get_link(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return VehicleEntityLinkWithEntity.from_orm(link)


@router.put("/vehicle-links/{link_id}", response_model=VehicleEntityLink)
def update_vehicle_link(
    link_id: uuid.UUID,
    link_update: VehicleEntityLinkUpdate,
    db: Session = Depends(get_db)
):
    """Update vehicle-entity link"""
    service = VehicleEntityLinkService(db)
    link = service.update_link(link_id, link_update)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.post("/vehicle-links/{link_id}/terminate", response_model=VehicleEntityLink)
def terminate_vehicle_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Terminate a vehicle-entity link"""
    service = VehicleEntityLinkService(db)
    link = service.terminate_link(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@router.delete("/vehicle-links/{link_id}")
def delete_vehicle_link(
    link_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Delete vehicle-entity link"""
    service = VehicleEntityLinkService(db)
    if not service.delete_link(link_id):
        raise HTTPException(status_code=404, detail="Link not found")
    return {"message": "Link deleted successfully"}


@router.get("/vehicles/{vehicle_id}/owners", response_model=List[VehicleEntityLinkWithEntity])
def get_vehicle_owners(
    vehicle_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get all owners for a vehicle"""
    service = VehicleEntityLinkService(db)
    owners = service.get_vehicle_owners(vehicle_id)
    return [VehicleEntityLinkWithEntity.from_orm(owner) for owner in owners]