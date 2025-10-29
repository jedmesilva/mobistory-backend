from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime
import uuid

from app.models.entity import Entity, VehicleEntityLink, LinkStatus, RelationshipType
from app.schemas.entity import (
    EntityCreate, 
    EntityUpdate, 
    VehicleEntityLinkCreate, 
    VehicleEntityLinkUpdate
)


class EntityService:
    """Service for managing entities"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_entity(self, entity_data: EntityCreate) -> Entity:
        """Create a new entity"""
        db_entity = Entity(**entity_data.dict())
        self.db.add(db_entity)
        self.db.commit()
        self.db.refresh(db_entity)
        return db_entity

    def get_entity(self, entity_id: uuid.UUID) -> Optional[Entity]:
        """Get entity by ID"""
        return self.db.query(Entity).filter(Entity.id == entity_id).first()

    def get_entities(self, skip: int = 0, limit: int = 100) -> List[Entity]:
        """Get all entities with pagination"""
        return self.db.query(Entity).filter(Entity.active == True).offset(skip).limit(limit).all()

    def update_entity(self, entity_id: uuid.UUID, entity_data: EntityUpdate) -> Optional[Entity]:
        """Update entity"""
        db_entity = self.get_entity(entity_id)
        if db_entity:
            for field, value in entity_data.dict(exclude_unset=True).items():
                setattr(db_entity, field, value)
            db_entity.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_entity)
        return db_entity

    def delete_entity(self, entity_id: uuid.UUID) -> bool:
        """Soft delete entity"""
        db_entity = self.get_entity(entity_id)
        if db_entity:
            db_entity.active = False
            db_entity.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False


class VehicleEntityLinkService:
    """Service for managing vehicle-entity links"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_link(self, link_data: VehicleEntityLinkCreate) -> VehicleEntityLink:
        """Create a new vehicle-entity link"""
        db_link = VehicleEntityLink(**link_data.dict())
        self.db.add(db_link)
        self.db.commit()
        self.db.refresh(db_link)
        return db_link

    def get_link(self, link_id: uuid.UUID) -> Optional[VehicleEntityLink]:
        """Get link by ID with entity data"""
        return self.db.query(VehicleEntityLink).options(
            joinedload(VehicleEntityLink.entity)
        ).filter(VehicleEntityLink.id == link_id).first()

    def get_vehicle_links(
        self, 
        vehicle_id: uuid.UUID, 
        status: Optional[LinkStatus] = None,
        relationship_type: Optional[RelationshipType] = None,
        active_only: bool = True
    ) -> List[VehicleEntityLink]:
        """Get all links for a vehicle with filters"""
        query = self.db.query(VehicleEntityLink).options(
            joinedload(VehicleEntityLink.entity)
        ).filter(VehicleEntityLink.vehicle_id == vehicle_id)
        
        if active_only:
            query = query.filter(VehicleEntityLink.active == True)
        
        if status:
            query = query.filter(VehicleEntityLink.status == status)
            
        if relationship_type:
            query = query.filter(VehicleEntityLink.relationship_type == relationship_type)
        
        return query.all()

    def get_entity_links(
        self, 
        entity_id: uuid.UUID, 
        status: Optional[LinkStatus] = None,
        active_only: bool = True
    ) -> List[VehicleEntityLink]:
        """Get all links for an entity"""
        query = self.db.query(VehicleEntityLink).options(
            joinedload(VehicleEntityLink.vehicle)
        ).filter(VehicleEntityLink.entity_id == entity_id)
        
        if active_only:
            query = query.filter(VehicleEntityLink.active == True)
        
        if status:
            query = query.filter(VehicleEntityLink.status == status)
        
        return query.all()

    def update_link(self, link_id: uuid.UUID, link_data: VehicleEntityLinkUpdate) -> Optional[VehicleEntityLink]:
        """Update vehicle-entity link"""
        db_link = self.get_link(link_id)
        if db_link:
            for field, value in link_data.dict(exclude_unset=True).items():
                setattr(db_link, field, value)
            db_link.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_link)
        return db_link

    def terminate_link(self, link_id: uuid.UUID, end_date: Optional[datetime] = None) -> Optional[VehicleEntityLink]:
        """Terminate a vehicle-entity link"""
        db_link = self.get_link(link_id)
        if db_link:
            db_link.status = LinkStatus.TERMINATED
            db_link.end_date = end_date or datetime.utcnow()
            db_link.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_link)
        return db_link

    def delete_link(self, link_id: uuid.UUID) -> bool:
        """Soft delete link"""
        db_link = self.get_link(link_id)
        if db_link:
            db_link.active = False
            db_link.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        return False

    def get_active_vehicle_links_count(self, vehicle_id: uuid.UUID) -> int:
        """Get count of active links for a vehicle"""
        return self.db.query(VehicleEntityLink).filter(
            and_(
                VehicleEntityLink.vehicle_id == vehicle_id,
                VehicleEntityLink.active == True,
                VehicleEntityLink.status == LinkStatus.ACTIVE
            )
        ).count()

    def get_vehicle_owners(self, vehicle_id: uuid.UUID) -> List[VehicleEntityLink]:
        """Get all owners (current and former) for a vehicle"""
        return self.db.query(VehicleEntityLink).options(
            joinedload(VehicleEntityLink.entity)
        ).filter(
            and_(
                VehicleEntityLink.vehicle_id == vehicle_id,
                VehicleEntityLink.relationship_type.in_([RelationshipType.OWNER, RelationshipType.CO_OWNER]),
                VehicleEntityLink.active == True
            )
        ).all()