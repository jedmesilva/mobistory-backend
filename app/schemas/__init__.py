from .token import Token, TokenPayload
from .user import User, UserCreate, UserUpdate, UserLogin, UserInDB
from .vehicle import (
    Vehicle,
    VehicleCreate,
    VehicleUpdate,
    VehicleWithDetails,
    Brand,
    BrandCreate,
    Model,
    ModelCreate,
    ModelVersion,
    ModelVersionCreate,
    Color,
    ColorCreate,
    Plate,
    PlateCreate,
)
from .conversation import Conversation, ConversationCreate, ConversationUpdate, ConversationWithDetails
from .message import Message, MessageCreate, MessageUpdate
from .fueling import Fueling, FuelingCreate, FuelingUpdate
from .maintenance import Maintenance, MaintenanceCreate, MaintenanceUpdate

__all__ = [
    "Token",
    "TokenPayload",
    "User",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserInDB",
    "Vehicle",
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleWithDetails",
    "Brand",
    "BrandCreate",
    "Model",
    "ModelCreate",
    "ModelVersion",
    "ModelVersionCreate",
    "Color",
    "ColorCreate",
    "Plate",
    "PlateCreate",
    "Conversation",
    "ConversationCreate",
    "ConversationUpdate",
    "ConversationWithDetails",
    "Message",
    "MessageCreate",
    "MessageUpdate",
    "Fueling",
    "FuelingCreate",
    "FuelingUpdate",
    "Maintenance",
    "MaintenanceCreate",
    "MaintenanceUpdate",
]
