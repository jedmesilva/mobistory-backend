from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from .base import BaseModel


class Brand(Base, BaseModel):
    """Marca do veículo (Fiat, Volkswagen, etc)"""

    __tablename__ = "brands"

    brand = Column(String, nullable=False, unique=True, index=True)

    # Relacionamentos
    models = relationship("Model", back_populates="brand", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Brand {self.brand}>"


class Model(Base, BaseModel):
    """Modelo do veículo (Uno, Gol, etc)"""

    __tablename__ = "models"

    model = Column(String, nullable=False, index=True)
    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)

    # Relacionamentos
    brand = relationship("Brand", back_populates="models")
    versions = relationship("ModelVersion", back_populates="model", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Model {self.model}>"


class ModelVersion(Base, BaseModel):
    """Versão do modelo (1.0, 1.6, etc)"""

    __tablename__ = "model_versions"

    version = Column(String, nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)

    # Relacionamentos
    model = relationship("Model", back_populates="versions")

    def __repr__(self):
        return f"<ModelVersion {self.version}>"


class Color(Base, BaseModel):
    """Cor do veículo"""

    __tablename__ = "colors"

    color = Column(String, nullable=False, unique=True, index=True)
    hex_code = Column(String, nullable=True)  # Código hexadecimal da cor

    def __repr__(self):
        return f"<Color {self.color}>"


class Plate(Base, BaseModel):
    """Placa do veículo"""

    __tablename__ = "plates"

    plate = Column(String, nullable=False, unique=True, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    is_current = Column(Boolean, default=True)  # Placa atual ou histórica

    # Relacionamentos
    vehicle = relationship("Vehicle", back_populates="plates")

    def __repr__(self):
        return f"<Plate {self.plate}>"


class Vehicle(Base, BaseModel):
    """Veículo"""

    __tablename__ = "vehicles"

    brand_id = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    model_id = Column(UUID(as_uuid=True), ForeignKey("models.id"), nullable=False)
    version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=True)
    category_id = Column(UUID(as_uuid=True), nullable=False)
    chassis = Column(String, nullable=False, unique=True, index=True)
    model_year = Column(Integer, nullable=False)
    manufacture_year = Column(Integer, nullable=False)
    active = Column(Boolean, default=True)

    # Relacionamentos
    brands = relationship("Brand")
    models = relationship("Model")
    model_versions = relationship("ModelVersion")
    plates = relationship("Plate", back_populates="vehicle", cascade="all, delete-orphan")
    colors = relationship("Color", back_populates="vehicle", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="vehicle", cascade="all, delete-orphan")
    moments = relationship("Moment", back_populates="vehicle", cascade="all, delete-orphan")
    entity_links = relationship("VehicleEntityLink", back_populates="vehicle", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Vehicle {self.brands.brand if self.brands else ''} {self.models.model if self.models else ''}>"
