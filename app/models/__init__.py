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
from .vehicle import Vehicle, Brand, Model, ModelVersion
from .message import Message, MessageType, SenderType
from .file import File

__all__ = [
    "Entity",
    "EntityType",
    "EntityRelationship",
    "Link",
    "LinkType",
    "VehicleEntityLink",
    "RelationshipType",
    "LinkStatus",
    "Vehicle",
    "Brand",
    "Model",
    "ModelVersion",
    "Message",
    "MessageType",
    "SenderType",
    "File",
]
