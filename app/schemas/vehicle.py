from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


# PlateType schemas
class PlateTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    country: str
    category: Optional[str] = None
    format_pattern: Optional[str] = None
    format_example: Optional[str] = None
    plate_color_name: Optional[str] = None
    background_color_hex: Optional[str] = None
    text_color_hex: Optional[str] = None


class PlateTypeCreate(PlateTypeBase):
    pass


class PlateType(PlateTypeBase):
    id: UUID
    active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Plate schemas
class PlateBase(BaseModel):
    plate_number: str
    licensing_date: Optional[date] = None
    licensing_country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = None


class PlateCreate(PlateBase):
    vehicle_id: UUID
    plate_type_id: UUID
    created_by_entity_id: Optional[UUID] = None


class Plate(PlateBase):
    id: UUID
    vehicle_id: UUID
    plate_type_id: UUID
    end_date: Optional[date] = None
    created_by_entity_id: Optional[UUID] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Color schemas
class ColorBase(BaseModel):
    color: str
    hex_code: Optional[str] = None
    description: Optional[str] = None


class ColorCreate(ColorBase):
    vehicle_id: UUID
    start_date: Optional[date] = None
    created_by_entity_id: Optional[UUID] = None


class Color(ColorBase):
    id: UUID
    vehicle_id: UUID
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    created_by_entity_id: Optional[UUID] = None
    active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Brand schemas
class BrandBase(BaseModel):
    name: str
    country_of_origin: Optional[str] = None
    logo_url: Optional[str] = None


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = None
    country_of_origin: Optional[str] = None
    logo_url: Optional[str] = None


class Brand(BrandBase):
    id: UUID
    active: bool = True
    verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Model schemas
class ModelBase(BaseModel):
    name: str
    brand_id: UUID
    category: Optional[str] = None


class ModelCreate(ModelBase):
    pass


class ModelUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None


class Model(ModelBase):
    id: UUID
    active: bool = True
    verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ModelVersion schemas
class ModelVersionBase(BaseModel):
    name: str
    model_id: UUID
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    drive_type: Optional[str] = None
    engine_displacement: Optional[str] = None
    engine_power: Optional[int] = None
    doors: Optional[int] = None
    seats: Optional[int] = None
    weight_kg: Optional[int] = None
    tank_capacity_liters: Optional[int] = None
    trunk_capacity_liters: Optional[int] = None


class ModelVersionCreate(ModelVersionBase):
    pass


class ModelVersionUpdate(BaseModel):
    name: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    drive_type: Optional[str] = None
    engine_displacement: Optional[str] = None
    engine_power: Optional[int] = None
    doors: Optional[int] = None
    seats: Optional[int] = None
    weight_kg: Optional[int] = None
    tank_capacity_liters: Optional[int] = None
    trunk_capacity_liters: Optional[int] = None


class ModelVersion(ModelVersionBase):
    id: UUID
    active: bool = True
    verified: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Color schemas
class ColorBase(BaseModel):
    color: str
    hex_code: Optional[str] = None


class ColorCreate(ColorBase):
    pass


class Color(ColorBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Plate schemas
class PlateBase(BaseModel):
    plate: str
    is_current: bool = True


class PlateCreate(PlateBase):
    vehicle_id: UUID


class Plate(PlateBase):
    id: UUID
    vehicle_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Vehicle schemas
class VehicleBase(BaseModel):
    vin: Optional[str] = None
    renavam: Optional[str] = None
    brand_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    version_id: Optional[UUID] = None
    custom_brand: Optional[str] = None
    custom_model: Optional[str] = None
    custom_version: Optional[str] = None
    manufacturing_year: Optional[int] = None
    model_year: Optional[int] = None
    current_color: Optional[str] = None
    current_plate: Optional[str] = None
    current_km: Optional[int] = None
    visibility: Optional[str] = "private"
    observations: Optional[str] = None


class VehicleCreate(VehicleBase):
    # Campos para criação de placa (opcional)
    plate_number: Optional[str] = None
    plate_type_id: Optional[UUID] = None
    licensing_date: Optional[date] = None
    licensing_country: Optional[str] = None
    plate_state: Optional[str] = None
    plate_city: Optional[str] = None

    # Campos para criação de cor (opcional)
    color: Optional[str] = None
    hex_code: Optional[str] = None
    color_description: Optional[str] = None

    # Campo para criar link com entidade (opcional)
    entity_id: Optional[UUID] = None
    link_type_id: Optional[UUID] = None


class VehicleUpdate(BaseModel):
    vin: Optional[str] = None
    renavam: Optional[str] = None
    brand_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    version_id: Optional[UUID] = None
    custom_brand: Optional[str] = None
    custom_model: Optional[str] = None
    custom_version: Optional[str] = None
    manufacturing_year: Optional[int] = None
    model_year: Optional[int] = None
    current_color: Optional[str] = None
    current_plate: Optional[str] = None
    current_km: Optional[int] = None
    visibility: Optional[str] = None
    observations: Optional[str] = None


class Vehicle(VehicleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleWithDetails(Vehicle):
    """Vehicle com relacionamentos populados"""
    brand: Optional[Brand] = None
    model: Optional[Model] = None
    version: Optional[ModelVersion] = None
    entity_links: List = []

    model_config = ConfigDict(from_attributes=True)
