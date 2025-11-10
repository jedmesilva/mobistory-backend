from .entity import (
    Entity,
    EntityType,
    EntityRelationship,
    Link,
    LinkType,
    VehicleEntityLink,  # Alias para Link
    RelationshipType,
    LinkStatus,
)
from .entity_contact import EntityContact
from .entity_name import EntityName
from .vehicle import Vehicle, Brand, Model, ModelVersion, Plate, PlateType, PlateModel
from .vehicle_cover import VehicleCover
from .color import Color, VehicleColor
from .mileage import MileageRecord, Odometer
from .message import Message, MessageType, SenderType
from .file import File
from .conversation import (
    ConversationContext,
    Conversation,
    ConversationParticipant,
    ConversationMessage,
)
from .permission import Permission
from .link_type_permission import LinkTypePermission

__all__ = [
    "Entity",
    "EntityType",
    "EntityRelationship",
    "EntityContact",
    "EntityName",
    "Link",
    "LinkType",
    "VehicleEntityLink",
    "RelationshipType",
    "LinkStatus",
    "Vehicle",
    "Brand",
    "Model",
    "ModelVersion",
    "Plate",
    "PlateType",
    "PlateModel",
    "VehicleCover",
    "Color",
    "VehicleColor",
    "MileageRecord",
    "Odometer",
    "Message",
    "MessageType",
    "SenderType",
    "File",
    "ConversationContext",
    "Conversation",
    "ConversationParticipant",
    "ConversationMessage",
    "Permission",
    "LinkTypePermission",
]
