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
    vehicle_colors = relationship("VehicleColor", back_populates="vehicle")
    covers = relationship("VehicleCover", back_populates="vehicle", order_by="VehicleCover.display_order")

    @property
    def primary_cover(self):
        """Retorna a capa primária do veículo"""
        try:
            if hasattr(self, 'covers') and self.covers:
                # Busca a capa marcada como primária
                primary = next((c for c in self.covers if c.is_primary), None)
                if primary:
                    return primary
                # Se não houver primária, retorna a primeira pela ordem
                return self.covers[0] if self.covers else None
        except Exception:
            pass
        return None

    @property
    def primary_cover_url(self):
        """Retorna a URL da capa primária"""
        primary = self.primary_cover
        if primary:
            return primary.image_url
        return None


class PlateModel(Base, BaseModelWithUpdate):
    """Modelos/Padrões de placas (Mercosul, Antigo, etc.)"""
    __tablename__ = "plate_models"

    code = Column(String, unique=True, nullable=False)  # BR_MERCOSUL, BR_OLD_STANDARD
    name = Column(String, nullable=False)  # Mercosul, Padrão Antigo
    country = Column(String, nullable=False)  # BR, US, AR
    region_code = Column(String(10), nullable=False)  # BR, CA, SP, etc.
    region_type = Column(String(20), nullable=False)  # national, state, province, city, district
    description = Column(Text, nullable=True)
    format_pattern = Column(String, nullable=True)  # AAA0A00 (visual)
    format_regex = Column(String, nullable=True)  # ^[A-Z]{3}[0-9][A-Z][0-9]{2}$
    format_example = Column(String, nullable=True)  # ABC1D23
    valid_from = Column(Date, nullable=True)  # Data início vigência
    valid_until = Column(Date, nullable=True)  # Data fim (null se vigente)
    has_qrcode = Column(Boolean, default=False)  # Mercosul tem QR Code
    has_chip = Column(Boolean, default=False)  # Algumas têm chip RFID
    active = Column(Boolean, default=True)

    # Relationships
    plate_types = relationship("PlateType", back_populates="plate_model")
    plates = relationship("Plate", back_populates="plate_model")


class PlateType(Base, BaseModelWithUpdate):
    """Tipos/Categorias de placas (Particular, Comercial, Oficial, etc.)"""
    __tablename__ = "plate_types"

    plate_model_id = Column(PGUUID(as_uuid=True), ForeignKey("plate_models.id"), nullable=False)
    code = Column(String, unique=True, nullable=False)  # BR_MERCOSUL_PARTICULAR
    name = Column(String, nullable=False)  # Particular
    description = Column(Text, nullable=True)
    color_code = Column(String, nullable=False)  # WHITE, RED, BLACK
    background_color = Column(String, nullable=True)  # #FFFFFF
    text_color = Column(String, nullable=True)  # #000000
    border_color = Column(String, nullable=True)  # #000000 (se aplicável)
    vehicle_category = Column(String, nullable=True)  # PRIVATE, COMMERCIAL, OFFICIAL
    requires_special_license = Column(Boolean, default=False)  # Táxi requer licença
    valid_from = Column(Date, nullable=True)  # Data de início da vigência deste tipo de placa
    valid_until = Column(Date, nullable=True)  # Data de fim da vigência (NULL = vigente)
    active = Column(Boolean, default=True)

    # Relationships
    plate_model = relationship("PlateModel", back_populates="plate_types")
    plates = relationship("Plate", back_populates="plate_type")


class Plate(Base, BaseModelWithUpdate):
    """Placas de veículos (histórico)"""
    __tablename__ = "plates"

    vehicle_id = Column(PGUUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    plate_type_id = Column(PGUUID(as_uuid=True), ForeignKey("plate_types.id"), nullable=False)
    plate_model_id = Column(PGUUID(as_uuid=True), ForeignKey("plate_models.id"), nullable=True)
    plate_number = Column(String, nullable=False)
    licensing_start_date = Column(Date, nullable=True)  # Data de início do licenciamento
    licensing_end_date = Column(Date, nullable=True)  # Data de fim do licenciamento
    licensing_country = Column(String, nullable=True)
    state = Column(String, nullable=True)  # UF/Estado
    city = Column(String, nullable=True)
    status = Column(String, nullable=True)  # ACTIVE, REPLACED, STOLEN, LOST
    end_date = Column(Date, nullable=True)  # Quando parou de usar (null se ativa)
    created_by_entity_id = Column(PGUUID(as_uuid=True), nullable=True)
    active = Column(Boolean, default=True)

    # Relationships
    vehicle = relationship("Vehicle", back_populates="plates")
    plate_type = relationship("PlateType", back_populates="plates")
    plate_model = relationship("PlateModel", back_populates="plates")


# Removido - agora usamos Color e VehicleColor em app/models/color.py
