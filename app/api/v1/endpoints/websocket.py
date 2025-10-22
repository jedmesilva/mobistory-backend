from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Dict, List
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models import User, Conversation, Message, SenderType, MessageType
import json
from datetime import datetime

router = APIRouter()

# Gerenciar conexões ativas
class ConnectionManager:
    def __init__(self):
        # conversation_id -> List[WebSocket]
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []
        self.active_connections[conversation_id].append(websocket)

    def disconnect(self, websocket: WebSocket, conversation_id: str):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)
            if len(self.active_connections[conversation_id]) == 0:
                del self.active_connections[conversation_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict, conversation_id: str):
        """Enviar mensagem para todos conectados naquela conversa"""
        if conversation_id in self.active_connections:
            message_json = json.dumps(message)
            for connection in self.active_connections[conversation_id]:
                await connection.send_text(message_json)


manager = ConnectionManager()


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    WebSocket para chat em tempo real

    Uso:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/chat/ws/CONVERSATION_ID?token=JWT_TOKEN')

    // Enviar mensagem
    ws.send(JSON.stringify({
      type: 'message',
      content: 'Olá!',
      message_type: 'text'
    }))

    // Receber mensagens
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log(data)
    }
    ```
    """

    # Validar token JWT
    payload = decode_access_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=1008, reason="Invalid token payload")
        return

    # Verificar se usuário existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=1008, reason="User not found")
        return

    # Verificar se conversa existe e pertence ao usuário
    conversation = (
        db.query(Conversation)
        .filter(Conversation.id == conversation_id)
        .filter(Conversation.user_id == user_id)
        .first()
    )

    if not conversation:
        await websocket.close(code=1008, reason="Conversation not found or unauthorized")
        return

    # Conectar
    await manager.connect(websocket, conversation_id)

    try:
        # Enviar mensagem de boas-vindas
        await manager.send_personal_message(
            json.dumps({
                "type": "system",
                "content": "Connected to chat",
                "timestamp": datetime.utcnow().isoformat()
            }),
            websocket
        )

        # Loop principal - receber mensagens
        while True:
            data = await websocket.receive_text()

            try:
                message_data = json.parse(data)

                # Validar tipo de mensagem
                msg_type = message_data.get("type", "message")

                if msg_type == "message":
                    # Salvar mensagem no banco
                    content = message_data.get("content", "")
                    message_type = message_data.get("message_type", "text")
                    context_hint = message_data.get("context_hint")

                    message = Message(
                        conversation_id=conversation_id,
                        sender_type=SenderType.USER,
                        message_type=MessageType(message_type),
                        content=content,
                        context_hint=context_hint,
                    )
                    db.add(message)
                    db.commit()
                    db.refresh(message)

                    # Broadcast para todos conectados
                    await manager.broadcast(
                        {
                            "type": "message",
                            "message_id": str(message.id),
                            "content": content,
                            "sender_type": "user",
                            "message_type": message_type,
                            "timestamp": message.created_at.isoformat(),
                        },
                        conversation_id
                    )

                elif msg_type == "typing":
                    # Broadcast "usuário está digitando"
                    await manager.broadcast(
                        {
                            "type": "typing",
                            "user_id": user_id,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        conversation_id
                    )

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    json.dumps({"type": "error", "content": "Invalid JSON"}),
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, conversation_id)
        # Notificar outros que usuário desconectou
        await manager.broadcast(
            {
                "type": "system",
                "content": "User disconnected",
                "timestamp": datetime.utcnow().isoformat(),
            },
            conversation_id
        )
