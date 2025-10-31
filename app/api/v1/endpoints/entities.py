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
    RelationshipType,
    EntityRelationshipCreate,
    EntityRelationshipUpdate,
    EntityRelationship,
    EntityRelationshipWithParent,
    EntityRelationshipWithChild,
    LinkRequest,
    LinkClaim,
    LinkGrant,
    LinkApproval,
    LinkWithEntities,
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


@router.patch("/entities/{entity_id}", response_model=Entity)
def patch_entity(
    entity_id: uuid.UUID,
    entity_update: EntityUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar PARCIALMENTE uma entidade

    Permite atualizar apenas os campos fornecidos, sem precisar enviar todos os dados.
    """
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


@router.patch("/vehicle-links/{link_id}", response_model=VehicleEntityLink)
def patch_vehicle_link(
    link_id: uuid.UUID,
    link_update: VehicleEntityLinkUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualizar PARCIALMENTE um vínculo

    Permite atualizar apenas os campos fornecidos.
    """
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


# ============================================================================
# Entity Relationships (Pai-Filho) endpoints
# ============================================================================

@router.post("/entities/{entity_id}/parent", response_model=EntityRelationship)
def set_entity_parent(
    entity_id: uuid.UUID,
    relationship_data: EntityRelationshipCreate,
    db: Session = Depends(get_db)
):
    """
    Definir entidade pai para uma entidade

    Cria um relacionamento pai-filho entre duas entidades.
    """
    from app.models import EntityRelationship as EntityRelationshipModel
    from datetime import date

    # Verificar se entity existe
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Verificar se parent_entity existe
    parent = db.query(Entity).filter(Entity.id == relationship_data.parent_entity_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent entity not found")

    # Criar relacionamento
    relationship = EntityRelationshipModel(
        entity_id=entity_id,
        parent_entity_id=relationship_data.parent_entity_id,
        relationship_type=relationship_data.relationship_type,
        reason=relationship_data.reason,
        observations=relationship_data.observations,
        start_date=date.today(),
        is_active=True
    )

    db.add(relationship)
    db.commit()
    db.refresh(relationship)

    return relationship


@router.get("/entities/{entity_id}/parent", response_model=Optional[EntityRelationshipWithParent])
def get_entity_parent(
    entity_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Obter entidade pai ativa de uma entidade

    Retorna o relacionamento ativo com a entidade pai.
    """
    from app.models import EntityRelationship as EntityRelationshipModel

    relationship = db.query(EntityRelationshipModel).filter(
        EntityRelationshipModel.entity_id == entity_id,
        EntityRelationshipModel.is_active == True
    ).first()

    if not relationship:
        return None

    return relationship


@router.get("/entities/{entity_id}/children", response_model=List[EntityRelationshipWithChild])
def get_entity_children(
    entity_id: uuid.UUID,
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Listar entidades filhas de uma entidade

    Retorna todos os relacionamentos onde esta entidade é pai.
    """
    from app.models import EntityRelationship as EntityRelationshipModel

    query = db.query(EntityRelationshipModel).filter(
        EntityRelationshipModel.parent_entity_id == entity_id
    )

    if active_only:
        query = query.filter(EntityRelationshipModel.is_active == True)

    relationships = query.all()
    return relationships


@router.get("/entities/{entity_id}/relationships", response_model=List[EntityRelationship])
def get_entity_relationships(
    entity_id: uuid.UUID,
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Listar todos os relacionamentos da entidade

    Retorna tanto relacionamentos como pai quanto como filho.
    """
    from app.models import EntityRelationship as EntityRelationshipModel

    query_as_child = db.query(EntityRelationshipModel).filter(
        EntityRelationshipModel.entity_id == entity_id
    )
    query_as_parent = db.query(EntityRelationshipModel).filter(
        EntityRelationshipModel.parent_entity_id == entity_id
    )

    if active_only:
        query_as_child = query_as_child.filter(EntityRelationshipModel.is_active == True)
        query_as_parent = query_as_parent.filter(EntityRelationshipModel.is_active == True)

    relationships = query_as_child.all() + query_as_parent.all()
    return relationships


@router.delete("/entities/{entity_id}/parent")
def remove_entity_parent(
    entity_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Remover relacionamento pai de uma entidade

    Desativa o relacionamento (soft delete), não remove do banco.
    """
    from app.models import EntityRelationship as EntityRelationshipModel
    from datetime import date

    relationship = db.query(EntityRelationshipModel).filter(
        EntityRelationshipModel.entity_id == entity_id,
        EntityRelationshipModel.is_active == True
    ).first()

    if not relationship:
        raise HTTPException(status_code=404, detail="No active parent relationship found")

    # Soft delete - apenas marca como inativo
    relationship.is_active = False
    relationship.end_date = date.today()

    db.commit()

    return {"message": "Parent relationship removed successfully"}


@router.get("/entities/{entity_id}/creator")
def get_entity_creator(
    entity_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Identificar quem criou a entidade

    Retorna a primeira relação de pai-filho registrada ou None.
    """
    from app.models import EntityRelationship as EntityRelationshipModel

    # O criador é considerado como a primeira entidade que estabeleceu
    # um relacionamento pai com esta entidade
    first_relationship = db.query(EntityRelationshipModel).filter(
        EntityRelationshipModel.entity_id == entity_id
    ).order_by(EntityRelationshipModel.created_at.asc()).first()

    if not first_relationship:
        return {"message": "No creator found - entity may be root"}

    return {
        "creator_entity_id": first_relationship.parent_entity_id,
        "created_at": first_relationship.created_at,
        "created_by_entity_id": first_relationship.created_by_entity_id
    }


# ============================================================================
# Vehicle Links - Advanced (Request, Claim, Grant, Deactivate)
# ============================================================================

@router.post("/vehicle-links/request", response_model=VehicleEntityLink)
def request_vehicle_link(
    link_request: LinkRequest,
    requesting_entity_id: uuid.UUID = Query(..., description="ID da entidade que está solicitando"),
    db: Session = Depends(get_db)
):
    """
    Solicitar vínculo a outra entidade sobre um veículo

    Cria uma solicitação de vínculo com status 'pending'.
    A entidade solicitada pode aprovar ou rejeitar.
    """
    from app.models import Link as LinkModel
    from datetime import datetime, date
    import secrets

    # Verificar se veículo existe
    from app.models import Vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.id == link_request.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verificar se as entidades existem
    from app.models import Entity as EntityModel
    requesting_entity = db.query(EntityModel).filter(EntityModel.id == requesting_entity_id).first()
    if not requesting_entity:
        raise HTTPException(status_code=404, detail="Requesting entity not found")

    requested_entity = db.query(EntityModel).filter(EntityModel.id == link_request.requested_entity_id).first()
    if not requested_entity:
        raise HTTPException(status_code=404, detail="Requested entity not found")

    # Criar link com status pending
    link = LinkModel(
        link_code=f"REQ-{secrets.token_hex(8)}",
        entity_id=link_request.requested_entity_id,  # Quem vai receber o vínculo
        vehicle_id=link_request.vehicle_id,
        link_type_id=link_request.link_type_id,
        status="pending_request",
        observations=f"Requested by entity {requesting_entity_id}. {link_request.observations or ''}",
        start_date=date.today()
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


@router.get("/entities/{entity_id}/link-requests/received", response_model=List[LinkWithEntities])
def get_received_link_requests(
    entity_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Listar solicitações de vínculo recebidas

    Retorna vínculos com status 'pending_request' direcionados a esta entidade.
    """
    from app.models import Link as LinkModel

    links = db.query(LinkModel).filter(
        LinkModel.entity_id == entity_id,
        LinkModel.status == "pending_request"
    ).all()

    return links


@router.get("/entities/{entity_id}/link-requests/sent")
def get_sent_link_requests(
    entity_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """
    Listar solicitações de vínculo enviadas

    Busca nos observations vínculos que foram solicitados por esta entidade.
    """
    from app.models import Link as LinkModel

    # Buscar nos observations
    links = db.query(LinkModel).filter(
        LinkModel.status == "pending_request",
        LinkModel.observations.like(f"%entity {entity_id}%")
    ).all()

    return [{"link_id": link.id, "vehicle_id": link.vehicle_id, "status": link.status} for link in links]


@router.post("/vehicle-links/request/{request_id}/approve", response_model=VehicleEntityLink)
def approve_link_request(
    request_id: uuid.UUID,
    approval: LinkApproval,
    db: Session = Depends(get_db)
):
    """
    Aprovar solicitação de vínculo

    Muda o status de 'pending_request' para 'active'.
    """
    from app.models import Link as LinkModel

    link = db.query(LinkModel).filter(LinkModel.id == request_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link request not found")

    if link.status != "pending_request":
        raise HTTPException(status_code=400, detail="Link is not pending approval")

    if approval.approved:
        link.status = "active"
        if approval.link_type_id:
            link.link_type_id = approval.link_type_id
        if approval.observations:
            link.observations = f"{link.observations}\nApproved: {approval.observations}"
    else:
        link.status = "rejected"
        if approval.observations:
            link.observations = f"{link.observations}\nRejected: {approval.observations}"

    db.commit()
    db.refresh(link)

    return link


@router.post("/vehicle-links/request/{request_id}/reject", response_model=VehicleEntityLink)
def reject_link_request(
    request_id: uuid.UUID,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Rejeitar solicitação de vínculo

    Muda o status para 'rejected'.
    """
    from app.models import Link as LinkModel

    link = db.query(LinkModel).filter(LinkModel.id == request_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link request not found")

    if link.status != "pending_request":
        raise HTTPException(status_code=400, detail="Link is not pending approval")

    link.status = "rejected"
    if reason:
        link.observations = f"{link.observations}\nRejected: {reason}"

    db.commit()
    db.refresh(link)

    return link


@router.post("/vehicle-links/claim", response_model=VehicleEntityLink)
def claim_vehicle_link(
    claim: LinkClaim,
    claiming_entity_id: uuid.UUID = Query(..., description="ID da entidade que está reivindicando"),
    db: Session = Depends(get_db)
):
    """
    Reivindicar vínculo com documentos

    Cria uma reivindicação de vínculo apresentando documentos que comprovem o vínculo.
    Status inicial: 'pending_validation'.
    """
    from app.models import Link as LinkModel, Vehicle
    from datetime import date
    import secrets

    # Verificar se veículo existe
    vehicle = db.query(Vehicle).filter(Vehicle.id == claim.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verificar se entidade existe
    from app.models import Entity as EntityModel
    entity = db.query(EntityModel).filter(EntityModel.id == claiming_entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Claiming entity not found")

    # Criar link com status pending_validation
    link = LinkModel(
        link_code=f"CLM-{secrets.token_hex(8)}",
        entity_id=claiming_entity_id,
        vehicle_id=claim.vehicle_id,
        link_type_id=claim.link_type_id,
        status="pending_validation",
        document_proof=claim.document_proof,
        observations=claim.observations,
        start_date=date.today()
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


@router.get("/vehicle-links/claims/pending", response_model=List[LinkWithEntities])
def get_pending_claims(
    db: Session = Depends(get_db)
):
    """
    Listar reivindicações de vínculo pendentes

    Retorna todos os vínculos com status 'pending_validation'.
    (Endpoint administrativo)
    """
    from app.models import Link as LinkModel

    claims = db.query(LinkModel).filter(
        LinkModel.status == "pending_validation"
    ).all()

    return claims


@router.post("/vehicle-links/claim/{claim_id}/validate", response_model=VehicleEntityLink)
def validate_claim(
    claim_id: uuid.UUID,
    approved: bool = Query(...),
    observations: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Validar reivindicação de vínculo

    Administrador valida documentos e aprova/rejeita a reivindicação.
    """
    from app.models import Link as LinkModel
    from datetime import datetime

    link = db.query(LinkModel).filter(LinkModel.id == claim_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Claim not found")

    if link.status != "pending_validation":
        raise HTTPException(status_code=400, detail="Claim is not pending validation")

    if approved:
        link.status = "active"
        link.validated_at = datetime.utcnow()
        if observations:
            link.observations = f"{link.observations}\nValidated: {observations}"
    else:
        link.status = "rejected"
        if observations:
            link.observations = f"{link.observations}\nRejected: {observations}"

    db.commit()
    db.refresh(link)

    return link


@router.post("/vehicle-links/grant", response_model=VehicleEntityLink)
def grant_vehicle_link(
    grant: LinkGrant,
    granting_entity_id: uuid.UUID = Query(..., description="ID da entidade que está concedendo"),
    db: Session = Depends(get_db)
):
    """
    Conceder vínculo a outra entidade

    Uma entidade com permissão concede vínculo diretamente a outra.
    Status: 'active' imediatamente.
    """
    from app.models import Link as LinkModel, Vehicle
    from datetime import date
    import secrets

    # Verificar se veículo existe
    vehicle = db.query(Vehicle).filter(Vehicle.id == grant.vehicle_id).first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    # Verificar se as entidades existem
    from app.models import Entity as EntityModel
    granting_entity = db.query(EntityModel).filter(EntityModel.id == granting_entity_id).first()
    if not granting_entity:
        raise HTTPException(status_code=404, detail="Granting entity not found")

    granted_entity = db.query(EntityModel).filter(EntityModel.id == grant.granted_entity_id).first()
    if not granted_entity:
        raise HTTPException(status_code=404, detail="Granted entity not found")

    # TODO: Verificar se granting_entity tem permissão para conceder vínculos neste veículo

    # Criar link ativo
    link = LinkModel(
        link_code=f"GRT-{secrets.token_hex(8)}",
        entity_id=grant.granted_entity_id,
        vehicle_id=grant.vehicle_id,
        link_type_id=grant.link_type_id,
        status="active",
        observations=f"Granted by entity {granting_entity_id}. {grant.observations or ''}",
        start_date=grant.start_date or date.today(),
        end_date=grant.end_date
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link


@router.post("/vehicle-links/{link_id}/deactivate", response_model=VehicleEntityLink)
def deactivate_vehicle_link(
    link_id: uuid.UUID,
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Desvincular-se (desativar vínculo)

    Muda o status do vínculo para 'terminated'.
    Não deleta o registro, apenas atualiza o status.
    """
    from app.models import Link as LinkModel
    from datetime import date

    link = db.query(LinkModel).filter(LinkModel.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.status == "terminated":
        raise HTTPException(status_code=400, detail="Link already terminated")

    # Soft termination
    link.status = "terminated"
    link.end_date = date.today()
    if reason:
        link.observations = f"{link.observations}\nTerminated: {reason}"

    db.commit()
    db.refresh(link)

    return link


@router.post("/vehicle-links/{link_id}/revoke", response_model=VehicleEntityLink)
def revoke_vehicle_link(
    link_id: uuid.UUID,
    revoking_entity_id: uuid.UUID = Query(..., description="ID da entidade que está revogando"),
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Revogar vínculo de terceiro

    Uma entidade com permissão revoga o vínculo de outra entidade.
    """
    from app.models import Link as LinkModel
    from datetime import date

    link = db.query(LinkModel).filter(LinkModel.id == link_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.status == "terminated":
        raise HTTPException(status_code=400, detail="Link already terminated")

    # TODO: Verificar se revoking_entity tem permissão para revogar este vínculo

    # Revoke
    link.status = "revoked"
    link.end_date = date.today()
    if reason:
        link.observations = f"{link.observations}\nRevoked by entity {revoking_entity_id}: {reason}"

    db.commit()
    db.refresh(link)

    return link