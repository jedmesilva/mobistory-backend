from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
import uuid

from app.core.database import Base
from .base import BaseModel


class Brand(Base, BaseModel):
    """Marcas de veículos (Toyota, Ford, etc.)"""
    __tablename__ = "brands"

    name = Column(String, nullable=False)
    country_of_origin = Column(String, nullable=True)
    logo_url = Column(Text, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    models = relationship("Model", back_populates="brand")
    vehicles = relationship("Vehicle", back_populates="brand")


class Model(Base, BaseModel):
    """Modelos de veículos (Corolla, F-150, etc.)"""
    __tablename__ = "models"

    brand_id = Column(PGUUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    brand = relationship("Brand", back_populates="models")
    versions = relationship("ModelVersion", back_populates="model")
    vehicles = relationship("Vehicle", back_populates="model")


class ModelVersion(Base, BaseModel):
    """Versões de modelos (Corolla XEi, F-150 XLT, etc.)"""
    __tablename__ = "model_versions"

    model_id = Column(PGUUID(as_uuid=True), ForeignKey("models.id"), nullable=False)
    name = Column(String, nullable=False)
    start_year = Column(Integer, nullable=True)
    end_year = Column(Integer, nullable=True)
    fuel_type = Column(String, nullable=True)
    transmission = Column(String, nullable=True)
    drive_type = Column(String, nullable=True)
    engine_displacement = Column(String, nullable=True)
    engine_power = Column(Integer, nullable=True)
    doors = Column(Integer, nullable=True)
    seats = Column(Integer, nullable=True)
    weight_kg = Column(Integer, nullable=True)
    tank_capacity_liters = Column(Integer, nullable=True)
    trunk_capacity_liters = Column(Integer, nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    model = relationship("Model", back_populates="versions")
    vehicles = relationship("Vehicle", back_populates="version")


class Vehicle(Base, BaseModel):
    """Veículos cadastrados"""
    __tablename__ = "vehicles"

    # Identificação do veículo
    vin = Column(String, unique=True, nullable=True)
    renavam = Column(String, unique=True, nullable=True)

    # Relacionamento com catálogo (brand, model, version)
    brand_id = Column(PGUUID(as_uuid=True), ForeignKey("brands.id"), nullable=True)
    model_id = Column(PGUUID(as_uuid=True), ForeignKey("models.id"), nullable=True)
    version_id = Column(PGUUID(as_uuid=True), ForeignKey("model_versions.id"), nullable=True)

    # Campos customizados (caso não encontre no catálogo)
    custom_brand = Column(String, nullable=True)
    custom_model = Column(String, nullable=True)
    custom_version = Column(String, nullable=True)

    # Informações atuais do veículo
    manufacturing_year = Column(Integer, nullable=True)
    model_year = Column(Integer, nullable=True)
    current_color = Column(String, nullable=True)
    current_plate = Column(String, nullable=True)
    current_km = Column(Integer, nullable=True)

    # Visibilidade e observações
    visibility = Column(String, default="private")  # private, public, restricted
    observations = Column(Text, nullable=True)

    # Timestamps
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    brand = relationship("Brand", back_populates="vehicles")
    model = relationship("Model", back_populates="vehicles")
    version = relationship("ModelVersion", back_populates="vehicles")
    entity_links = relationship("Link", back_populates="vehicle")
