"""create_vehicle_events_with_partitioning

Revision ID: 5b2fdb8cbbee
Revises: d148697e2509
Create Date: 2025-11-10 02:25:56.222517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b2fdb8cbbee'
down_revision = 'd148697e2509'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Cria a estrutura de vehicle_events com particionamento trimestral.

    Esta migration implementa:
    1. Tabela principal vehicle_events particionada por RANGE (event_timestamp)
    2. 6 partições trimestrais (2025 Q1-Q4, 2026 Q1-Q2)
    3. 7 índices estratégicos para performance
    4. Função para criação automática de partições
    """

    # ========================================================================
    # 1. CRIAR TABELA PRINCIPAL (PARTICIONADA)
    # ========================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.vehicle_events (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            vehicle_id uuid NOT NULL,
            entity_id uuid,
            event_category character varying(50) NOT NULL,
            event_type character varying(100) NOT NULL,
            event_timestamp timestamp with time zone NOT NULL DEFAULT now(),
            severity character varying(20),
            title character varying(200) NOT NULL,
            description text,
            event_data jsonb,
            source_table character varying(100),
            source_record_id uuid,
            tags jsonb,
            metadata jsonb,
            is_public character varying(20) NOT NULL DEFAULT 'owner_only',
            created_at timestamp with time zone NOT NULL DEFAULT now(),
            updated_at timestamp with time zone,
            CONSTRAINT vehicle_events_pkey PRIMARY KEY (id, event_timestamp),
            CONSTRAINT vehicle_events_vehicle_id_fkey FOREIGN KEY (vehicle_id)
                REFERENCES public.vehicles (id) ON DELETE CASCADE,
            CONSTRAINT vehicle_events_entity_id_fkey FOREIGN KEY (entity_id)
                REFERENCES public.entities (id) ON DELETE SET NULL
        ) PARTITION BY RANGE (event_timestamp)
    """)

    # ========================================================================
    # 2. CRIAR PARTIÇÕES TRIMESTRAIS (2025 Q1-Q4, 2026 Q1-Q2)
    # ========================================================================

    # 2025 Q1 (Jan-Mar)
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.vehicle_events_2025_q1
            PARTITION OF public.vehicle_events
            FOR VALUES FROM ('2025-01-01') TO ('2025-04-01')
    """)

    # 2025 Q2 (Apr-Jun)
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.vehicle_events_2025_q2
            PARTITION OF public.vehicle_events
            FOR VALUES FROM ('2025-04-01') TO ('2025-07-01')
    """)

    # 2025 Q3 (Jul-Sep)
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.vehicle_events_2025_q3
            PARTITION OF public.vehicle_events
            FOR VALUES FROM ('2025-07-01') TO ('2025-10-01')
    """)

    # 2025 Q4 (Oct-Dec)
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.vehicle_events_2025_q4
            PARTITION OF public.vehicle_events
            FOR VALUES FROM ('2025-10-01') TO ('2026-01-01')
    """)

    # 2026 Q1 (Jan-Mar)
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.vehicle_events_2026_q1
            PARTITION OF public.vehicle_events
            FOR VALUES FROM ('2026-01-01') TO ('2026-04-01')
    """)

    # 2026 Q2 (Apr-Jun)
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.vehicle_events_2026_q2
            PARTITION OF public.vehicle_events
            FOR VALUES FROM ('2026-04-01') TO ('2026-07-01')
    """)

    # ========================================================================
    # 3. CRIAR ÍNDICES ESTRATÉGICOS
    # ========================================================================

    # Índice 1: Timeline por veículo (consulta mais comum)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehicle_events_vehicle_timestamp
            ON public.vehicle_events (vehicle_id, event_timestamp DESC)
    """)

    # Índice 2: Filtragem por categoria
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehicle_events_category
            ON public.vehicle_events (event_category, event_timestamp DESC)
    """)

    # Índice 3: Filtragem por tipo
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehicle_events_type
            ON public.vehicle_events (event_type, event_timestamp DESC)
    """)

    # Índice 4: Eventos por entidade (quem fez o quê)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehicle_events_entity
            ON public.vehicle_events (entity_id, event_timestamp DESC)
            WHERE entity_id IS NOT NULL
    """)

    # Índice 5: Rastreamento de origem
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehicle_events_source
            ON public.vehicle_events (source_table, source_record_id)
            WHERE source_table IS NOT NULL AND source_record_id IS NOT NULL
    """)

    # Índice 6: Alertas e eventos críticos (severidade)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehicle_events_severity
            ON public.vehicle_events (severity, event_timestamp DESC)
            WHERE severity IN ('warning', 'error', 'critical')
    """)

    # Índice 7: Busca por tags (GIN para arrays JSONB)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_vehicle_events_tags
            ON public.vehicle_events USING gin (tags)
            WHERE tags IS NOT NULL
    """)

    # ========================================================================
    # 4. FUNÇÃO PARA CRIAÇÃO AUTOMÁTICA DE PARTIÇÕES
    # ========================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.create_vehicle_events_partition(
            target_year integer,
            target_quarter integer
        )
        RETURNS void
        LANGUAGE plpgsql
        AS $$
        DECLARE
            partition_name text;
            start_date date;
            end_date date;
        BEGIN
            -- Calcular nome da partição
            partition_name := 'vehicle_events_' || target_year || '_q' || target_quarter;

            -- Calcular range de datas
            start_date := DATE(target_year || '-' || ((target_quarter - 1) * 3 + 1) || '-01');
            end_date := start_date + INTERVAL '3 months';

            -- Criar partição se não existir
            EXECUTE format(
                'CREATE TABLE IF NOT EXISTS public.%I PARTITION OF public.vehicle_events FOR VALUES FROM (%L) TO (%L)',
                partition_name,
                start_date,
                end_date
            );

            RAISE NOTICE 'Partição % criada para período % a %', partition_name, start_date, end_date;
        END;
        $$
    """)


def downgrade() -> None:
    """
    Remove a estrutura de vehicle_events.

    ATENÇÃO: Esta operação é destrutiva e removerá TODOS os eventos registrados!
    """

    # Remover função de criação de partições
    op.execute("DROP FUNCTION IF EXISTS public.create_vehicle_events_partition(integer, integer)")

    # Remover índices (serão removidos automaticamente com a tabela)
    # Mas listamos aqui para documentação
    indices_to_drop = [
        "idx_vehicle_events_vehicle_timestamp",
        "idx_vehicle_events_category",
        "idx_vehicle_events_type",
        "idx_vehicle_events_entity",
        "idx_vehicle_events_source",
        "idx_vehicle_events_severity",
        "idx_vehicle_events_tags"
    ]

    # Remover partições (serão removidas automaticamente com a tabela pai)
    partitions_to_drop = [
        "vehicle_events_2025_q1",
        "vehicle_events_2025_q2",
        "vehicle_events_2025_q3",
        "vehicle_events_2025_q4",
        "vehicle_events_2026_q1",
        "vehicle_events_2026_q2"
    ]

    # Remover tabela principal (CASCADE remove partições)
    op.execute("DROP TABLE IF EXISTS public.vehicle_events CASCADE")
