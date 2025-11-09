from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


# PlateModel schemas
class PlateModelBase(BaseModel):
    code: str
    name: str
    country: str
    region_code: str
    region_type: str
    description: Optional[str] = None
    format_pattern: Optional[str] = None
    format_regex: Optional[str] = None
    format_example: Optional[str] = None
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None
    has_qrcode: bool = False
    has_chip: bool = False


class PlateModelCreate(PlateModelBase):
    pass


class PlateModel(PlateModelBase):
    id: UUID
    active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# PlateType schemas
class PlateTypeBase(BaseModel):
    plate_model_id: UUID
    code: str
    name: str
    description: Optional[str] = None
    color_code: str
    background_color: Optional[str] = None
    text_color: Optional[str] = None
    border_color: Optional[str] = None
    vehicle_category: Optional[str] = None
    requires_special_license: bool = False
    valid_from: Optional[date] = None
    valid_until: Optional[date] = None


class PlateTypeCreate(PlateTypeBase):
    pass


# Plate Detection Request
class PlateDetectionRequest(BaseModel):
    plate_number: str


class PlateType(PlateTypeBase):
    id: UUID
    active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Plate schemas
class PlateBase(BaseModel):
    plate_number: str
    licensing_start_date: Optional[date] = None
    licensing_end_date: Optional[date] = None
    licensing_country: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    status: Optional[str] = None


class PlateCreate(PlateBase):
    vehicle_id: UUID
    plate_type_id: UUID
    plate_model_id: Optional[UUID] = None
    created_by_entity_id: Optional[UUID] = None


class Plate(PlateBase):
    id: UUID
    vehicle_id: UUID
    plate_type_id: UUID
    plate_model_id: Optional[UUID] = None
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


# Color schemas (Master Catalog)
class ColorBase(BaseModel):
    name: str
    description: Optional[str] = None
    hex_code: Optional[str] = None
    rgb_r: Optional[int] = None
    rgb_g: Optional[int] = None
    rgb_b: Optional[int] = None
    cmyk_c: Optional[int] = None
    cmyk_m: Optional[int] = None
    cmyk_y: Optional[int] = None
    cmyk_k: Optional[int] = None
    finish_type: Optional[str] = None  # solid, metallic, pearlescent, matte, glossy


class ColorCreate(ColorBase):
    pass


class ColorUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    hex_code: Optional[str] = None
    rgb_r: Optional[int] = None
    rgb_g: Optional[int] = None
    rgb_b: Optional[int] = None
    cmyk_c: Optional[int] = None
    cmyk_m: Optional[int] = None
    cmyk_y: Optional[int] = None
    cmyk_k: Optional[int] = None
    finish_type: Optional[str] = None


class Color(ColorBase):
    id: UUID
    verified: bool = False
    active: bool = True
    created_by: Optional[UUID] = None
    verified_by: Optional[UUID] = None
    verified_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# VehicleColor schemas (Relationship/History)
class VehicleColorBase(BaseModel):
    vehicle_id: UUID
    color_id: UUID
    is_primary: bool = True


class VehicleColorCreate(VehicleColorBase):
    pass


class VehicleColor(VehicleColorBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# VehicleCover schemas
class VehicleCoverBase(BaseModel):
    vehicle_id: UUID
    file_id: UUID
    is_primary: bool = False
    display_order: int = 0


class VehicleCoverCreate(VehicleCoverBase):
    pass


class VehicleCover(VehicleCoverBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    image_url: Optional[str] = None  # Computed from file relationship

    model_config = ConfigDict(from_attributes=True)


# Vehicle schemas
class VehicleBase(BaseModel):
    vin: Optional[str] = None
    renavam: Optional[str] = None
    brand_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    version_id: Optional[UUID] = None
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
    plate_model_id: Optional[UUID] = None
    licensing_start_date: Optional[date] = None
    licensing_end_date: Optional[date] = None
    licensing_country: Optional[str] = None
    plate_state: Optional[str] = None
    plate_city: Optional[str] = None

    # Campo para criar relacionamento cor-veículo (opcional)
    color_id: Optional[UUID] = None

    # Campo para criar link com entidade (opcional)
    entity_id: Optional[UUID] = None
    link_type_id: Optional[UUID] = None


class VehicleUpdate(BaseModel):
    vin: Optional[str] = None
    renavam: Optional[str] = None
    brand_id: Optional[UUID] = None
    model_id: Optional[UUID] = None
    version_id: Optional[UUID] = None
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
    covers: List['VehicleCover'] = []
    primary_cover_url: Optional[str] = None  # Computed property from model

    model_config = ConfigDict(from_attributes=True)
