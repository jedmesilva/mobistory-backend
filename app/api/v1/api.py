from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    vehicles,
    conversations,
    messages,
    brands,
    colors,
    plate_models,
    plate_types,
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

# Colors (Catálogo de cores)
api_router.include_router(
    colors.router,
    prefix="/colors",
    tags=["colors"],
)

# Plate Models (Modelos de placas - Mercosul, Antigo, etc)
api_router.include_router(
    plate_models.router,
    prefix="/plate-models",
    tags=["plate-models"],
)

# Plate Types (Tipos de placas - Particular, Comercial, etc)
api_router.include_router(
    plate_types.router,
    prefix="/plate-types",
    tags=["plate-types"],
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
    prefix="/entities",
    tags=["entities"],
)
