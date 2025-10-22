from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class FuelingBase(BaseModel):
    date: date
    odometer: Optional[int] = None
    fuel_type: str  # gasolina, etanol, diesel, gnv
    liters: Optional[Decimal] = None
    price_per_liter: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    tank_filled: bool = False
    station_name: Optional[str] = None
    notes: Optional[str] = None


class FuelingCreate(FuelingBase):
    vehicle_id: UUID


class FuelingUpdate(BaseModel):
    date: Optional[date] = None
    odometer: Optional[int] = None
    fuel_type: Optional[str] = None
    liters: Optional[Decimal] = None
    price_per_liter: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    tank_filled: Optional[bool] = None
    station_name: Optional[str] = None
    notes: Optional[str] = None


class Fueling(FuelingBase):
    id: UUID
    vehicle_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
