from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, func
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.core.database import get_db
from app.models import (
    Conversation,
    ConversationContext,
    ConversationParticipant,
    ConversationMessage,
    Entity,
    Vehicle,
    Link,
)
from app.schemas.conversation import (
    # Context
    ConversationContext as ConversationContextSchema,
    ConversationContextCreate,
    ConversationContextUpdate,
    # Conversation
    Conversation as ConversationSchema,
    ConversationCreate,
    ConversationUpdate,
    ConversationWithDetails,
    ConversationListResponse,
    ConversationDetailResponse,
    # Participant
    ConversationParticipant as ConversationParticipantSchema,
    ConversationParticipantCreate,
    ConversationParticipantUpdate,
    # Message
    ConversationMessage as ConversationMessageSchema,
    ConversationMessageCreate,
    ConversationMessageUpdate,
)

router = APIRouter()


# =============================================================================
# CONVERSATION CONTEXTS ENDPOINTS
# =============================================================================

@router.get("/contexts", response_model=List[ConversationContextSchema])
def list_contexts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Lista todos os contextos de conversas disponíveis"""
    query = db.query(ConversationContext)

    if active_only:
        query = query.filter(ConversationContext.active == True)

    contexts = query.offset(skip).limit(limit).all()
    return contexts


@router.post("/contexts", response_model=ConversationContextSchema, status_code=201)
def create_context(
    context_data: ConversationContextCreate,
    db: Session = Depends(get_db),
):
    """Cria um novo contexto de conversa"""
    # Verificar se já existe um contexto com o mesmo código
    existing = db.query(ConversationContext).filter(
        ConversationContext.code == context_data.code
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Contexto com este código já existe")

    context = ConversationContext(**context_data.model_dump())
    db.add(context)
    db.commit()
    db.refresh(context)
    return context


@router.get("/contexts/{context_id}", response_model=ConversationContextSchema)
def get_context(context_id: UUID, db: Session = Depends(get_db)):
    """Obtém detalhes de um contexto específico"""
    context = db.query(ConversationContext).filter(ConversationContext.id == context_id).first()

    if not context:
        raise HTTPException(status_code=404, detail="Contexto não encontrado")

    return context


@router.patch("/contexts/{context_id}", response_model=ConversationContextSchema)
def update_context(
    context_id: UUID,
    context_data: ConversationContextUpdate,
    db: Session = Depends(get_db),
):
    """Atualiza um contexto de conversa"""
    context = db.query(ConversationContext).filter(ConversationContext.id == context_id).first()

    if not context:
        raise HTTPException(status_code=404, detail="Contexto não encontrado")

    update_data = context_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(context, field, value)

    db.commit()
    db.refresh(context)
    return context


@router.delete("/contexts/{context_id}", status_code=204)
def delete_context(context_id: UUID, db: Session = Depends(get_db)):
    """Desativa um contexto de conversa (soft delete)"""
    context = db.query(ConversationContext).filter(ConversationContext.id == context_id).first()

    if not context:
        raise HTTPException(status_code=404, detail="Contexto não encontrado")

    context.active = False
    db.commit()
    return None


# =============================================================================
# CONVERSATIONS ENDPOINTS
# =============================================================================

@router.get("")
def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    vehicle_id: Optional[UUID] = None,
    entity_id: Optional[UUID] = None,
    status: Optional[str] = Query("active", description="Status da conversa (active, archived, closed). Por padrão retorna apenas conversas ativas."),
    conversation_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Lista conversas com filtros opcionais

    Filtros:
    - vehicle_id: Filtra por veículo específico
    - entity_id: Filtra por participante específico
    - status: Filtra por status (active, archived, closed). Por padrão retorna apenas conversas ativas.
    - conversation_type: Filtra por tipo (private, group, support)
    """
    from app.schemas.vehicle import VehicleWithDetails
    from app.models.vehicle import Brand, Model, ModelVersion, Plate
    from app.models.color import Color, VehicleColor

    # Buscar conversas com eager loading de veículos e relacionamentos
    query = db.query(Conversation).options(
        joinedload(Conversation.primary_vehicle)
        .joinedload(Vehicle.brand),
        joinedload(Conversation.primary_vehicle)
        .joinedload(Vehicle.model),
        joinedload(Conversation.primary_vehicle)
        .joinedload(Vehicle.version),
        joinedload(Conversation.primary_vehicle)
        .joinedload(Vehicle.plates),
        joinedload(Conversation.primary_vehicle)
        .joinedload(Vehicle.vehicle_colors)
        .joinedload(VehicleColor.color),
    )

    # Filtro global: excluir conversas deletadas (soft delete)
    query = query.filter(Conversation.deleted_at.is_(None))

    # Filtro por veículo
    if vehicle_id:
        query = query.filter(Conversation.primary_vehicle_id == vehicle_id)

    # Filtro por participante (apenas participantes ativos)
    if entity_id:
        query = query.join(ConversationParticipant).filter(
            and_(
                ConversationParticipant.entity_id == entity_id,
                ConversationParticipant.is_active == True
            )
        )

    # Filtro por status
    if status:
        query = query.filter(Conversation.status == status)

    # Filtro por tipo
    if conversation_type:
        query = query.filter(Conversation.conversation_type == conversation_type)

    # Contagem total
    total = query.count()

    # Ordenar por última mensagem
    conversations = query.order_by(desc(Conversation.last_message_at)).offset(skip).limit(limit).all()

    # Serializar manualmente para evitar erros de Pydantic
    conversations_data = []
    for conv in conversations:
        # Construir dicionário manualmente
        conv_dict = {
            "id": str(conv.id),
            "conversation_code": conv.conversation_code,
            "primary_vehicle_id": str(conv.primary_vehicle_id) if conv.primary_vehicle_id else None,
            "vehicle_ids": conv.vehicle_ids,
            "conversation_type": conv.conversation_type,
            "title": conv.title,
            "summary": conv.summary,
            "status": conv.status,
            "main_context_id": str(conv.main_context_id) if conv.main_context_id else None,
            "total_participants": conv.total_participants,
            "active_participants": conv.active_participants,
            "total_messages": conv.total_messages,
            "total_actions_executed": conv.total_actions_executed,
            "started_at": conv.started_at.isoformat() if conv.started_at else None,
            "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
            "finished_at": conv.finished_at.isoformat() if conv.finished_at else None,
            "archived_at": conv.archived_at.isoformat() if conv.archived_at else None,
            "created_at": conv.created_at.isoformat(),
            "updated_at": conv.updated_at.isoformat(),
        }

        # Adicionar dados do veículo se existir
        if conv.primary_vehicle:
            vehicle = conv.primary_vehicle
            vehicle_dict = {
                "id": str(vehicle.id),
                "brand": {"id": str(vehicle.brand.id), "name": vehicle.brand.name} if vehicle.brand else None,
                "model": {"id": str(vehicle.model.id), "name": vehicle.model.name} if vehicle.model else None,
                "version": {"id": str(vehicle.version.id), "name": vehicle.version.name} if vehicle.version else None,
                "model_year": vehicle.model_year,
                "manufacturing_year": vehicle.manufacturing_year,
                "current_plate": vehicle.current_plate,
                "current_color": vehicle.current_color,
                "plates": [{"id": str(p.id), "plate_number": p.plate_number, "status": p.status, "state": p.state} for p in vehicle.plates] if vehicle.plates else [],
                "vehicle_colors": [{"id": str(vc.id), "color": vc.color.name if vc.color else None, "is_primary": vc.is_primary} for vc in vehicle.vehicle_colors] if vehicle.vehicle_colors else [],
            }
            conv_dict["primary_vehicle"] = vehicle_dict
        else:
            conv_dict["primary_vehicle"] = None

        conversations_data.append(conv_dict)

    return JSONResponse(content={
        "conversations": conversations_data,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit,
    })


@router.post("", response_model=ConversationSchema, status_code=201)
def create_conversation(
    conversation_data: ConversationCreate,
    entity_id: UUID = Query(..., description="ID da entidade que está criando a conversa"),
    db: Session = Depends(get_db),
):
    """
    Cria uma nova conversa

    O entity_id fornecido será automaticamente adicionado como primeiro participante
    com role='owner'
    """
    # Verificar se a entidade existe
    entity = db.query(Entity).filter(Entity.id == entity_id).first()
    if not entity:
        raise HTTPException(status_code=404, detail="Entidade não encontrada")

    # Verificar se o veículo existe (se fornecido)
    if conversation_data.primary_vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == conversation_data.primary_vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Veículo não encontrado")

        # Verificar se já existe uma conversa ativa entre esta entidade e este veículo
        existing_conversation = (
            db.query(Conversation)
            .join(ConversationParticipant)
            .filter(
                and_(
                    Conversation.primary_vehicle_id == conversation_data.primary_vehicle_id,
                    Conversation.status == "active",
                    Conversation.deleted_at.is_(None),  # Excluir conversas deletadas
                    ConversationParticipant.entity_id == entity_id,
                    ConversationParticipant.is_active == True,
                )
            )
            .first()
        )

        # Se já existe, retornar a conversa existente ao invés de criar nova
        if existing_conversation:
            return existing_conversation

    # Gerar código único para a conversa
    conversation_code = f"CONV-{uuid4().hex[:12].upper()}"

    # Criar conversa
    conversation = Conversation(
        conversation_code=conversation_code,
        **conversation_data.model_dump(),
        status="active",
        started_at=datetime.utcnow(),
        total_participants=1,
        active_participants=1,
    )
    db.add(conversation)
    db.flush()

    # Adicionar o criador como primeiro participante
    participant = ConversationParticipant(
        conversation_id=conversation.id,
        entity_id=entity_id,
        role="owner",
        participant_type="human",
        joined_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(participant)

    db.commit()
    db.refresh(conversation)
    return conversation


@router.get("/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: UUID,
    entity_id: Optional[UUID] = Query(None, description="ID da entidade acessando"),
    include_messages: bool = Query(True),
    messages_limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Obtém detalhes completos de uma conversa

    Inclui: participantes, contexto, mensagens recentes e permissões
    """
    # Buscar conversa com relacionamentos
    query = db.query(Conversation).options(
        joinedload(Conversation.primary_vehicle),
        joinedload(Conversation.main_context),
        joinedload(Conversation.participants).joinedload(ConversationParticipant.entity),
    )

    conversation = query.filter(
        and_(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None)  # Excluir conversas deletadas
        )
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    # Verificar permissões (se entity_id fornecido)
    participant = None
    if entity_id:
        participant = db.query(ConversationParticipant).filter(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.entity_id == entity_id,
                ConversationParticipant.is_active == True,
            )
        ).first()

        if not participant:
            raise HTTPException(status_code=403, detail="Você não é participante desta conversa")

    # Buscar mensagens recentes
    if include_messages:
        messages = db.query(ConversationMessage).options(
            joinedload(ConversationMessage.sender_entity),
            joinedload(ConversationMessage.context),
        ).filter(
            ConversationMessage.conversation_id == conversation_id
        ).order_by(desc(ConversationMessage.created_at)).limit(messages_limit).all()

        # Inverter ordem para mostrar da mais antiga para a mais recente
        messages.reverse()
    else:
        messages = []

    # Calcular permissões
    can_send_message = participant is not None
    can_invite_participants = participant and participant.role in ["owner", "admin"]
    can_manage_conversation = participant and participant.role == "owner"

    return ConversationDetailResponse(
        conversation=ConversationWithDetails(
            **conversation.__dict__,
            messages=messages,
        ),
        can_send_message=can_send_message,
        can_invite_participants=can_invite_participants,
        can_manage_conversation=can_manage_conversation,
    )


@router.patch("/{conversation_id}", response_model=ConversationSchema)
def update_conversation(
    conversation_id: UUID,
    conversation_data: ConversationUpdate,
    entity_id: UUID = Query(..., description="ID da entidade atualizando"),
    db: Session = Depends(get_db),
):
    """Atualiza uma conversa (apenas owner pode atualizar)"""
    # Verificar permissões
    participant = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == entity_id,
            ConversationParticipant.role == "owner",
        )
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Apenas o owner pode atualizar a conversa")

    # Buscar conversa
    conversation = db.query(Conversation).filter(
        and_(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None)  # Não permitir atualizar conversas deletadas
        )
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    # Atualizar campos
    update_data = conversation_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)

    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    return conversation


@router.delete("/{conversation_id}", status_code=204)
def delete_conversation(
    conversation_id: UUID,
    entity_id: UUID = Query(..., description="ID da entidade deletando"),
    db: Session = Depends(get_db),
):
    """Deleta uma conversa (soft delete usando deleted_at)"""
    # Verificar permissões
    participant = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == entity_id,
            ConversationParticipant.role == "owner",
        )
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Apenas o owner pode deletar a conversa")

    # Buscar conversa (excluir conversas já deletadas)
    conversation = db.query(Conversation).filter(
        and_(
            Conversation.id == conversation_id,
            Conversation.deleted_at.is_(None)  # Não permitir deletar conversas já deletadas
        )
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")

    # Soft delete usando deleted_at
    conversation.status = "deleted"
    conversation.deleted_at = datetime.utcnow()
    db.commit()
    return None


# =============================================================================
# CONVERSATION PARTICIPANTS ENDPOINTS
# =============================================================================

@router.get("/{conversation_id}/participants", response_model=List[ConversationParticipantSchema])
def list_participants(
    conversation_id: UUID,
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
):
    """Lista todos os participantes de uma conversa"""
    query = db.query(ConversationParticipant).filter(
        ConversationParticipant.conversation_id == conversation_id
    )

    if active_only:
        query = query.filter(ConversationParticipant.is_active == True)

    participants = query.all()
    return participants


@router.post("/{conversation_id}/participants", response_model=ConversationParticipantSchema, status_code=201)
def add_participant(
    conversation_id: UUID,
    participant_data: ConversationParticipantCreate,
    inviter_entity_id: UUID = Query(..., description="ID da entidade convidando"),
    db: Session = Depends(get_db),
):
    """Adiciona um novo participante à conversa"""
    # Verificar se o convite tem permissão
    inviter = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == inviter_entity_id,
            ConversationParticipant.role.in_(["owner", "admin"]),
        )
    ).first()

    if not inviter:
        raise HTTPException(status_code=403, detail="Você não tem permissão para adicionar participantes")

    # Verificar se a entidade já é participante
    existing = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == participant_data.entity_id,
            ConversationParticipant.is_active == True,
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Entidade já é participante desta conversa")

    # Criar participante
    participant = ConversationParticipant(
        **participant_data.model_dump(),
        invited_by_entity_id=inviter_entity_id,
        invited_by_participant_id=inviter.id,
        joined_at=datetime.utcnow(),
        is_active=True,
    )
    db.add(participant)

    # Atualizar contadores da conversa
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    conversation.total_participants += 1
    conversation.active_participants += 1

    db.commit()
    db.refresh(participant)
    return participant


@router.patch("/{conversation_id}/participants/{participant_id}", response_model=ConversationParticipantSchema)
def update_participant(
    conversation_id: UUID,
    participant_id: UUID,
    participant_data: ConversationParticipantUpdate,
    updater_entity_id: UUID = Query(..., description="ID da entidade atualizando"),
    db: Session = Depends(get_db),
):
    """Atualiza um participante (role, permissões, etc)"""
    # Verificar permissões do atualizador
    updater = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == updater_entity_id,
            ConversationParticipant.role == "owner",
        )
    ).first()

    if not updater:
        raise HTTPException(status_code=403, detail="Apenas o owner pode atualizar participantes")

    # Buscar participante
    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.id == participant_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    # Atualizar
    update_data = participant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(participant, field, value)

    participant.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(participant)
    return participant


@router.delete("/{conversation_id}/participants/{participant_id}", status_code=204)
def remove_participant(
    conversation_id: UUID,
    participant_id: UUID,
    remover_entity_id: UUID = Query(..., description="ID da entidade removendo"),
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Remove um participante da conversa"""
    # Verificar permissões
    remover = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == remover_entity_id,
            ConversationParticipant.role.in_(["owner", "admin"]),
        )
    ).first()

    if not remover:
        raise HTTPException(status_code=403, detail="Você não tem permissão para remover participantes")

    # Buscar participante
    participant = db.query(ConversationParticipant).filter(
        ConversationParticipant.id == participant_id
    ).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participante não encontrado")

    # Não permitir remover o owner
    if participant.role == "owner":
        raise HTTPException(status_code=400, detail="Não é possível remover o owner da conversa")

    # Remover (soft delete)
    participant.is_active = False
    participant.left_at = datetime.utcnow()
    participant.removed_by_entity_id = remover_entity_id
    participant.removal_reason = reason

    # Atualizar contadores da conversa
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    conversation.active_participants -= 1

    db.commit()
    return None


# =============================================================================
# CONVERSATION MESSAGES ENDPOINTS
# =============================================================================

@router.get("/{conversation_id}/messages", response_model=List[ConversationMessageSchema])
def list_messages(
    conversation_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    entity_id: Optional[UUID] = Query(None, description="ID da entidade acessando"),
    db: Session = Depends(get_db),
):
    """Lista mensagens de uma conversa"""
    # Verificar se a entidade é participante
    if entity_id:
        participant = db.query(ConversationParticipant).filter(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.entity_id == entity_id,
                ConversationParticipant.is_active == True,
            )
        ).first()

        if not participant:
            raise HTTPException(status_code=403, detail="Você não é participante desta conversa")

    # Buscar mensagens
    messages = db.query(ConversationMessage).options(
        joinedload(ConversationMessage.sender_entity),
        joinedload(ConversationMessage.context),
    ).filter(
        ConversationMessage.conversation_id == conversation_id
    ).order_by(ConversationMessage.created_at).offset(skip).limit(limit).all()

    return messages


@router.post("/{conversation_id}/messages", response_model=ConversationMessageSchema, status_code=201)
def send_message(
    conversation_id: UUID,
    message_data: ConversationMessageCreate,
    db: Session = Depends(get_db),
):
    """Envia uma nova mensagem na conversa"""
    # Verificar se o sender é participante ativo
    participant = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == message_data.sender_entity_id,
            ConversationParticipant.is_active == True,
        )
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Você não é participante desta conversa")

    # Criar mensagem
    message = ConversationMessage(**message_data.model_dump())
    db.add(message)

    # Atualizar contadores da conversa
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    conversation.total_messages += 1
    conversation.last_message_at = datetime.utcnow()

    # Atualizar unread_count para outros participantes
    db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id != message_data.sender_entity_id,
            ConversationParticipant.is_active == True,
        )
    ).update({ConversationParticipant.unread_count: ConversationParticipant.unread_count + 1})

    db.commit()
    db.refresh(message)
    return message


@router.patch("/{conversation_id}/messages/{message_id}", response_model=ConversationMessageSchema)
def update_message(
    conversation_id: UUID,
    message_id: UUID,
    message_data: ConversationMessageUpdate,
    entity_id: UUID = Query(..., description="ID da entidade atualizando"),
    db: Session = Depends(get_db),
):
    """Atualiza uma mensagem (apenas o sender pode atualizar)"""
    # Buscar mensagem
    message = db.query(ConversationMessage).filter(
        and_(
            ConversationMessage.id == message_id,
            ConversationMessage.conversation_id == conversation_id,
        )
    ).first()

    if not message:
        raise HTTPException(status_code=404, detail="Mensagem não encontrada")

    # Verificar se é o sender ou admin/owner
    if message.sender_entity_id != entity_id:
        participant = db.query(ConversationParticipant).filter(
            and_(
                ConversationParticipant.conversation_id == conversation_id,
                ConversationParticipant.entity_id == entity_id,
                ConversationParticipant.role.in_(["owner", "admin"]),
            )
        ).first()

        if not participant:
            raise HTTPException(status_code=403, detail="Você não tem permissão para atualizar esta mensagem")

    # Atualizar
    update_data = message_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)

    db.commit()
    db.refresh(message)
    return message


@router.post("/{conversation_id}/messages/{message_id}/mark-as-read", status_code=204)
def mark_message_as_read(
    conversation_id: UUID,
    message_id: UUID,
    entity_id: UUID = Query(..., description="ID da entidade lendo"),
    db: Session = Depends(get_db),
):
    """Marca uma mensagem como lida pelo participante"""
    # Buscar participante
    participant = db.query(ConversationParticipant).filter(
        and_(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.entity_id == entity_id,
            ConversationParticipant.is_active == True,
        )
    ).first()

    if not participant:
        raise HTTPException(status_code=403, detail="Você não é participante desta conversa")

    # Atualizar last_read
    participant.last_read_message_id = message_id
    participant.last_read_at = datetime.utcnow()

    # Recalcular unread_count
    unread_count = db.query(func.count(ConversationMessage.id)).filter(
        and_(
            ConversationMessage.conversation_id == conversation_id,
            ConversationMessage.created_at > participant.last_read_at,
            ConversationMessage.sender_entity_id != entity_id,
        )
    ).scalar()

    participant.unread_count = unread_count or 0

    db.commit()
    return None
