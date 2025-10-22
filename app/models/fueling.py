from sqlalchemy import Column, String, Numeric, Integer, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from .base import BaseModel


class Fueling(Base, BaseModel):
    """Registro de abastecimento"""

    __tablename__ = "fueling"

    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)

    date = Column(Date, nullable=False, index=True)
    odometer = Column(Integer, nullable=True)  # Quilometragem

    fuel_type = Column(String, nullable=False)  # gasolina, etanol, diesel, gnv
    liters = Column(Numeric(10, 2), nullable=True)
    price_per_liter = Column(Numeric(10, 2), nullable=True)
    total_price = Column(Numeric(10, 2), nullable=True)

    tank_filled = Column(Boolean, default=False)  # Tanque cheio?
    station_name = Column(String, nullable=True)  # Nome do posto

    notes = Column(String, nullable=True)  # Observações

    # Relacionamentos
    vehicle = relationship("Vehicle", back_populates="fuelings")

    def __repr__(self):
        return f"<Fueling {self.date} - {self.liters}L {self.fuel_type}>"
