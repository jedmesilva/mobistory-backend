from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    vehicles,
    conversations,
    messages,
    brands,
    fueling,
    maintenance,
    websocket,
    upload,
)

api_router = APIRouter()

# Autenticação
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

# Veículos
api_router.include_router(
    vehicles.router,
    prefix="/vehicles",
    tags=["vehicles"],
)

# Brands, Models e Versions (dados base)
api_router.include_router(
    brands.router,
    prefix="/catalog",
    tags=["catalog"],
)

# Conversas
api_router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["conversations"],
)

# Mensagens
api_router.include_router(
    messages.router,
    prefix="/messages",
    tags=["messages"],
)

# Abastecimentos
api_router.include_router(
    fueling.router,
    prefix="/fueling",
    tags=["fueling"],
)

# Manutenções
api_router.include_router(
    maintenance.router,
    prefix="/maintenance",
    tags=["maintenance"],
)

# Chat em tempo real (WebSocket)
api_router.include_router(
    websocket.router,
    prefix="/chat",
    tags=["chat"],
)

# Upload de arquivos
api_router.include_router(
    upload.router,
    prefix="/upload",
    tags=["upload"],
)
