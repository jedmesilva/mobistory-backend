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
    all_data,
    moments,
    entities,
)

api_router = APIRouter()

# Autenticacao
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"],
)

# Veiculos
api_router.include_router(
    vehicles.router,
    prefix="/vehicles",
    tags=["vehicles"],
)

# Brands, Models e Versions (hierarquia aninhada)
api_router.include_router(
    brands.router,
    prefix="/brands",
    tags=["brands"],
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

# Manutencoes
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

# Dados completos (equivalente ao Supabase)
api_router.include_router(
    all_data.router,
    tags=["data"],
)

# Moments com detalhes
api_router.include_router(
    moments.router,
    tags=["moments"],
)

# Entidades e vínculos
api_router.include_router(
    entities.router,
    tags=["entities"],
)
