from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class MaintenanceBase(BaseModel):
    date: date
    odometer: Optional[int] = None
    type: str  # oil_change, tire, brake, etc
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    provider: Optional[str] = None
    parts: Optional[str] = None
    next_due_date: Optional[date] = None
    next_due_odometer: Optional[int] = None


class MaintenanceCreate(MaintenanceBase):
    vehicle_id: UUID


class MaintenanceUpdate(BaseModel):
    date: Optional[date] = None
    odometer: Optional[int] = None
    type: Optional[str] = None
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    provider: Optional[str] = None
    parts: Optional[str] = None
    next_due_date: Optional[date] = None
    next_due_odometer: Optional[int] = None


class Maintenance(MaintenanceBase):
    id: UUID
    vehicle_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
