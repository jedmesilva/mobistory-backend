from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base
from .base import BaseModel


class VehicleEvent(Base, BaseModel):
    """
    Sistema de eventos para veículos - Timeline imutável de todos os acontecimentos.

    Esta tabela funciona como um log append-only (somente inserção) de todos os eventos
    relevantes que ocorrem com um veículo. Utiliza particionamento trimestral para
    escalabilidade e performance.

    Estrutura Híbrida:
    - Colunas SQL fixas: para campos frequentemente consultados e filtrados
    - JSONB event_data: para flexibilidade e dados específicos de cada tipo de evento

    Categorias de Eventos:
    - documentation: Eventos relacionados a documentação (CNH, licenciamento, etc.)
    - maintenance: Manutenções, revisões, trocas de peças
    - usage: Uso do veículo (abastecimentos, quilometragem)
    - financial: Eventos financeiros (vendas, compras, multas, IPVA)
    - alert: Alertas e notificações importantes
    - modification: Modificações físicas ou de registro

    Rastreabilidade:
    - source_table: Tabela de origem do evento
    - source_record_id: ID do registro na tabela de origem
    - Permite rastrear de onde cada evento foi gerado
    """

    __tablename__ = "vehicle_events"

    # Identificação
    vehicle_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Entidade relacionada (quem executou/registrou o evento)
    entity_id = Column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    # Classificação do evento
    event_category = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Categoria: documentation, maintenance, usage, financial, alert, modification"
    )

    event_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Tipo específico dentro da categoria (ex: refuel, oil_change, etc.)"
    )

    # Temporal
    event_timestamp = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Quando o evento ocorreu (não quando foi registrado)"
    )

    # Severidade/Prioridade
    severity = Column(
        String(20),
        nullable=True,
        comment="info, warning, error, critical - para eventos de alerta"
    )

    # Descrição
    title = Column(
        String(200),
        nullable=False,
        comment="Título curto do evento para exibição em timeline"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Descrição detalhada do evento"
    )

    # Dados específicos do evento (estrutura flexível)
    event_data = Column(
        JSONB,
        nullable=True,
        comment="Dados específicos do tipo de evento em formato JSON"
    )

    # Rastreabilidade (de onde veio o evento)
    source_table = Column(
        String(100),
        nullable=True,
        comment="Tabela de origem (ex: vehicle_refuels, mileage_records, plates)"
    )

    source_record_id = Column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="ID do registro na tabela de origem"
    )

    # Metadados adicionais
    tags = Column(
        JSONB,
        nullable=True,
        comment="Tags/labels para categorização adicional (array de strings)"
    )

    extra_metadata = Column(
        "metadata",
        JSONB,
        nullable=True,
        comment="Metadados extras flexíveis"
    )

    # Visibility & Access Control
    is_public = Column(
        String(20),
        nullable=False,
        default="owner_only",
        comment="owner_only, linked_entities, public - controle de visibilidade"
    )

    # Relacionamentos
    vehicle = relationship("Vehicle", back_populates="events")
    entity = relationship("Entity")

    # Índices estratégicos definidos ao nível da migration para suportar particionamento
    # Ver migration para detalhes dos 7 índices criados
