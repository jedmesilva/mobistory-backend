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
    VehicleEntityLinkUpdate,
    AnonymousEntityCreate
)


class EntityService:
    """Service for managing entities"""
    
    def __init__(self, db: Session):
        self.db = db

    def create_entity(self, entity_data: EntityCreate) -> Entity:
        """Create a new entity"""
        # Criar entity_code único
        entity_code = f"ENT-{uuid.uuid4().hex[:12].upper()}"

        # Criar entidade com os campos corretos
        db_entity = Entity(
            entity_code=entity_code,
            display_name=entity_data.name,  # 'name' do schema -> 'display_name' do model
            email=entity_data.email,
            phone=entity_data.phone,
            legal_id_number=entity_data.document_number,  # 'document_number' do schema -> 'legal_id_number' do model
            active=entity_data.active,
        )

        self.db.add(db_entity)
        self.db.commit()
        self.db.refresh(db_entity)
        return db_entity

    def create_anonymous_entity(self, entity_data: AnonymousEntityCreate) -> Entity:
        """Create a new anonymous entity with device fingerprint"""
        # Criar entity_code único para entidades anônimas
        entity_code = f"ANON-{uuid.uuid4().hex[:12].upper()}"

        # Criar entidade anônima
        db_entity = Entity(
            entity_code=entity_code,
            display_name=entity_data.name or "Usuário Anônimo",
            is_anonymous=True,
            device_fingerprint=entity_data.device_fingerprint,
            active=True,
            verified=False,
        )

        self.db.add(db_entity)
        self.db.commit()
        self.db.refresh(db_entity)
        return db_entity

    def convert_anonymous_to_verified(
        self,
        entity_id: uuid.UUID,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        document_number: Optional[str] = None,
        display_name: Optional[str] = None
    ) -> Optional[Entity]:
        """Convert anonymous entity to verified entity"""
        db_entity = self.get_entity(entity_id)
        if db_entity and db_entity.is_anonymous:
            # Atualizar dados
            if display_name:
                db_entity.display_name = display_name
            if email:
                db_entity.email = email
            if phone:
                db_entity.phone = phone
            if document_number:
                db_entity.legal_id_number = document_number

            # Marcar como não anônimo se tiver pelo menos um dado verificado
            if email or phone or document_number:
                db_entity.is_anonymous = False

            db_entity.updated_at = datetime.utcnow()
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
        link_type_id: Optional[uuid.UUID] = None,
        active_only: bool = True
    ) -> List[VehicleEntityLink]:
        """Get all links for a vehicle with filters"""
        query = self.db.query(VehicleEntityLink).options(
            joinedload(VehicleEntityLink.entity),
            joinedload(VehicleEntityLink.link_type)
        ).filter(VehicleEntityLink.vehicle_id == vehicle_id)

        if active_only:
            query = query.filter(VehicleEntityLink.status != 'terminated')

        if status:
            query = query.filter(VehicleEntityLink.status == status)

        if link_type_id:
            query = query.filter(VehicleEntityLink.link_type_id == link_type_id)

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
            query = query.filter(VehicleEntityLink.status != 'terminated')
        
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