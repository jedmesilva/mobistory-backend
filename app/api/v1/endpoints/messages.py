from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import User, Message, Conversation
from app.schemas import Message as MessageSchema, MessageCreate, MessageUpdate
from app.api.deps import get_current_user

router = APIRouter()


@router.get("/", response_model=List[MessageSchema])
def list_messages(
    conversation_id: str,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar mensagens de uma conversa

    - **conversation_id**: ID da conversa (obrigatório)
    - **skip**: Paginação
    - **limit**: Limite de registros
    """
    # Verificar se conversa existe e pertence ao usuário
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

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return messages


@router.post("/", response_model=MessageSchema, status_code=status.HTTP_201_CREATED)
def create_message(
    message_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Enviar nova mensagem em uma conversa

    - **conversation_id**: ID da conversa
    - **content**: Conteúdo da mensagem
    - **message_type**: Tipo (text, image, audio, video)
    - **sender_type**: Quem enviou (user, ai, system)
    - **context_hint**: Hint de contexto (opcional)
    - **media_url**: URL da mídia (opcional)
    """
    # Verificar se conversa existe e pertence ao usuário
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == message_in.conversation_id)
        .filter(Conversation.user_id == current_user.id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Criar mensagem
    message = Message(**message_in.model_dump())
    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get("/{message_id}", response_model=MessageSchema)
def get_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter uma mensagem específica por ID
    """
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    # Verificar se a conversa da mensagem pertence ao usuário
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == message.conversation_id)
        .filter(Conversation.user_id == current_user.id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this message",
        )

    return message


@router.put("/{message_id}", response_model=MessageSchema)
def update_message(
    message_id: str,
    message_in: MessageUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar uma mensagem (ex: associar a um contexto)
    """
    message = db.query(Message).filter(Message.id == message_id).first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    # Verificar permissão
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == message.conversation_id)
        .filter(Conversation.user_id == current_user.id)
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this message",
        )

    update_data = message_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)

    db.commit()
    db.refresh(message)

    return message
