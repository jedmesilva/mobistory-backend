from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Brand schemas
class BrandBase(BaseModel):
    brand: str


class BrandCreate(BrandBase):
    pass


class Brand(BrandBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Model schemas
class ModelBase(BaseModel):
    model: str
    brand_id: UUID


class ModelCreate(ModelBase):
    pass


class Model(ModelBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ModelVersion schemas
class ModelVersionBase(BaseModel):
    version: str
    model_id: UUID


class ModelVersionCreate(ModelVersionBase):
    pass


class ModelVersion(ModelVersionBase):
    id: UUID
    created_at: datetime

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
    pass


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
