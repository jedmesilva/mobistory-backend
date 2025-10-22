from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import User, Conversation, Vehicle
from app.schemas import (
    Conversation as ConversationSchema,
    ConversationCreate,
    ConversationUpdate,
    ConversationWithDetails,
)
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ConversationWithDetails])
def list_conversations(
    vehicle_id: str = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar conversas do usuário autenticado

    - **vehicle_id**: Filtrar por veículo específico (opcional)
    - **skip**: Paginação
    - **limit**: Limite de registros
    """
    query = db.query(Conversation).filter(Conversation.user_id == current_user.id)

    if vehicle_id:
        query = query.filter(Conversation.vehicle_id == vehicle_id)

    conversations = (
        query.filter(Conversation.is_active == True)
        .order_by(Conversation.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return conversations


@router.post("/", response_model=ConversationWithDetails, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Criar nova conversa para um veículo

    - **vehicle_id**: ID do veículo
    - **title**: Título da conversa (opcional)
    """
    # Verificar se veículo existe e pertence ao usuário
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == conversation_in.vehicle_id)
        .filter(Vehicle.user_id == current_user.id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or does not belong to user",
        )

    # Criar conversa
    conversation = Conversation(
        **conversation_in.model_dump(),
        user_id=current_user.id,
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/{conversation_id}", response_model=ConversationWithDetails)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter uma conversa específica com todas as mensagens
    """
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .filter(Conversation.user_id == current_user.id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.put("/{conversation_id}", response_model=ConversationWithDetails)
def update_conversation(
    conversation_id: str,
    conversation_in: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar uma conversa (ex: título)
    """
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .filter(Conversation.user_id == current_user.id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    update_data = conversation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)

    db.commit()
    db.refresh(conversation)

    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Deletar (desativar) uma conversa
    """
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .filter(Conversation.user_id == current_user.id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Soft delete
    conversation.is_active = False
    db.commit()

    return None
