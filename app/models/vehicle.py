from sqlalchemy import Column, String, UUID, ForeignKey, DateTime, Boolean, Integer, Text, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from datetime import datetime
import uuid

from app.core.database import Base
from .base import BaseModel, BaseModelWithUpdate


class Brand(Base, BaseModelWithUpdate):
    """Marcas de veículos (Toyota, Ford, etc.)"""
    __tablename__ = "brands"

    name = Column(String, nullable=False)
    country_of_origin = Column(String, nullable=True)
    logo_url = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)  # Marca verificada por admin

    # Relationships
    models = relationship("Model", back_populates="brand")
    vehicles = relationship("Vehicle", back_populates="brand")


class Model(Base, BaseModelWithUpdate):
    """Modelos de veículos (Corolla, F-150, etc.)"""
    __tablename__ = "models"

    brand_id = Column(PGUUID(as_uuid=True), ForeignKey("brands.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)  # Modelo verificado por admin

    # Relationships
    brand = relationship("Brand", back_populates="models")
    versions = relationship("ModelVersion", back_populates="model")
    vehicles = relationship("Vehicle", back_populates="model")


class ModelVersion(Base, BaseModelWithUpdate):
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
    verified = Column(Boolean, default=False)  # Versão verificada por admin

    # Relationships
    model = relationship("Model", back_populates="versions")
    vehicles = relationship("Vehicle", back_populates="version")


class Vehicle(Base, BaseModelWithUpdate):
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

    # Relationships
    brand = relationship("Brand", back_populates="vehicles")
    model = relationship("Model", back_populates="vehicles")
    version = relationship("ModelVersion", back_populates="vehicles")
    entity_links = relationship("Link", back_populates="vehicle")
    plates = relationship("Plate", back_populates="vehicle")
    colors = relationship("Color", back_populates="vehicle")


class PlateType(Base, BaseModelWithUpdate):
    """Tipos de placas (Mercosul, Antiga, etc.)"""
    __tablename__ = "plate_types"

    code = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    country = Column(String, nullable=False)
    category = Column(String, nullable=True)  # particular, comercial, oficial, etc
    format_pattern = Column(String, nullable=True)
    format_example = Column(String, nullable=True)
    plate_color_name = Column(String, nullable=True)  # Nome da cor (ex: "Cinza", "Branca")
    background_color_hex = Column(String, nullable=True)  # Cor de fundo (#808080)
    text_color_hex = Column(String, nullable=True)  # Cor do texto (#000000)
    active = Column(Boolean, default=True)

    # Relationships
    plates = relationship("Plate", back_populates="plate_type")


class Plate(Base, BaseModelWithUpdate):
    """Placas de veículos (histórico)"""
    __tablename__ = "plates"

    vehicle_id = Column(PGUUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    plate_type_id = Column(PGUUID(as_uuid=True), ForeignKey("plate_types.id"), nullable=False)
    plate_number = Column(String, nullable=False)
    licensing_date = Column(Date, nullable=True)
    licensing_country = Column(String, nullable=True)
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    status = Column(String, nullable=True)
    end_date = Column(Date, nullable=True)
    created_by_entity_id = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="plates")
    plate_type = relationship("PlateType", back_populates="plates")


class Color(Base, BaseModelWithUpdate):
    """Cores de veículos (histórico)"""
    __tablename__ = "colors"

    vehicle_id = Column(PGUUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    color = Column(String, nullable=False)
    hex_code = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    created_by_entity_id = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="colors")
