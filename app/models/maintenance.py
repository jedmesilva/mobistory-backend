from sqlalchemy import Column, String, Numeric, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from .base import BaseModel


class Maintenance(Base, BaseModel):
    """Registro de manutenção"""

    __tablename__ = "maintenance"

    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)

    date = Column(Date, nullable=False, index=True)
    odometer = Column(Integer, nullable=True)  # Quilometragem

    type = Column(String, nullable=False)  # Tipo: oil_change, tire, brake, etc
    description = Column(Text, nullable=True)  # Descrição detalhada
    cost = Column(Numeric(10, 2), nullable=True)  # Custo

    provider = Column(String, nullable=True)  # Oficina/mecânico
    parts = Column(Text, nullable=True)  # Peças trocadas (JSON ou texto)

    next_due_date = Column(Date, nullable=True)  # Próxima manutenção
    next_due_odometer = Column(Integer, nullable=True)  # Próxima km

    # Relacionamentos
    vehicle = relationship("Vehicle", back_populates="maintenances")

    def __repr__(self):
        return f"<Maintenance {self.date} - {self.type}>"
