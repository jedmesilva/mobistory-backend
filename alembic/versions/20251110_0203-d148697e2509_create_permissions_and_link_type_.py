"""create_permissions_and_link_type_permissions_tables

Revision ID: d148697e2509
Revises: 4aa859ff2a28
Create Date: 2025-11-10 02:03:59.853011

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd148697e2509'
down_revision = '4aa859ff2a28'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ============================================================================
    # TABELA: permissions
    # Catálogo de todas as permissões possíveis no sistema
    # ============================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.permissions
        (
            id uuid NOT NULL DEFAULT gen_random_uuid(),
            code character varying NOT NULL,
            name character varying NOT NULL,
            description text,
            category character varying,
            active boolean DEFAULT true,
            created_at timestamp with time zone DEFAULT now(),
            CONSTRAINT permissions_pkey PRIMARY KEY (id),
            CONSTRAINT permissions_code_key UNIQUE (code)
        )
    """)

    op.execute("""
        COMMENT ON TABLE public.permissions
            IS 'Catálogo de todas as permissões possíveis no sistema'
    """)

    op.execute("""
        COMMENT ON COLUMN public.permissions.code
            IS 'Código único da permissão (ex: vehicle.edit, vehicle.delete)'
    """)

    op.execute("""
        COMMENT ON COLUMN public.permissions.category
            IS 'Categoria da permissão (ex: operation, management, administration)'
    """)

    # Índices para permissions
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_permissions_code
            ON public.permissions USING btree (code)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_permissions_category
            ON public.permissions USING btree (category, active)
    """)

    # ============================================================================
    # TABELA: link_type_permissions
    # Relacionamento N para N entre tipos de vínculos e permissões
    # ============================================================================
    op.execute("""
        CREATE TABLE IF NOT EXISTS public.link_type_permissions
        (
            link_type_id uuid NOT NULL,
            permission_id uuid NOT NULL,
            created_at timestamp with time zone DEFAULT now(),
            CONSTRAINT link_type_permissions_pkey PRIMARY KEY (link_type_id, permission_id),
            CONSTRAINT link_type_permissions_link_type_id_fkey FOREIGN KEY (link_type_id)
                REFERENCES public.link_types (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE CASCADE,
            CONSTRAINT link_type_permissions_permission_id_fkey FOREIGN KEY (permission_id)
                REFERENCES public.permissions (id) MATCH SIMPLE
                ON UPDATE NO ACTION
                ON DELETE CASCADE
        )
    """)

    op.execute("""
        COMMENT ON TABLE public.link_type_permissions
            IS 'Define quais permissões cada tipo de vínculo possui por padrão'
    """)

    # Índices para link_type_permissions
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_link_type_permissions_link_type
            ON public.link_type_permissions USING btree (link_type_id)
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_link_type_permissions_permission
            ON public.link_type_permissions USING btree (permission_id)
    """)

    # ============================================================================
    # POPULAR: permissions com permissões básicas
    # ============================================================================
    op.execute("""
        INSERT INTO public.permissions (code, name, description, category, active)
        VALUES
            ('vehicle.view', 'Visualizar Veículo', 'Permissão para visualizar dados do veículo', 'operation', true),
            ('vehicle.edit', 'Editar Veículo', 'Permissão para editar configurações do veículo', 'management', true),
            ('vehicle.delete', 'Excluir Veículo', 'Permissão para excluir o veículo', 'administration', true),
            ('vehicle.grant_access', 'Conceder Acesso', 'Permissão para adicionar novos vínculos ao veículo', 'management', true),
            ('vehicle.view_history', 'Ver Histórico', 'Permissão para visualizar histórico completo do veículo', 'operation', true),
            ('vehicle.manage_documents', 'Gerenciar Documentos', 'Permissão para adicionar/editar/excluir documentos', 'management', true)
        ON CONFLICT (code) DO NOTHING
    """)

    # ============================================================================
    # MIGRAÇÃO: Converter dados para link_type_permissions
    # ============================================================================

    # Owner (todas as permissões)
    op.execute("""
        INSERT INTO public.link_type_permissions (link_type_id, permission_id)
        SELECT
            lt.id,
            p.id
        FROM public.link_types lt
        CROSS JOIN public.permissions p
        WHERE lt.code = 'owner'
          AND p.active = true
        ON CONFLICT DO NOTHING
    """)

    # Co-owner (mesmas permissões do owner, exceto delete)
    op.execute("""
        INSERT INTO public.link_type_permissions (link_type_id, permission_id)
        SELECT
            lt.id,
            p.id
        FROM public.link_types lt
        CROSS JOIN public.permissions p
        WHERE lt.code = 'co_owner'
          AND p.code IN ('vehicle.view', 'vehicle.edit', 'vehicle.grant_access', 'vehicle.view_history', 'vehicle.manage_documents')
        ON CONFLICT DO NOTHING
    """)

    # Manager (pode gerenciar, mas não deletar)
    op.execute("""
        INSERT INTO public.link_type_permissions (link_type_id, permission_id)
        SELECT
            lt.id,
            p.id
        FROM public.link_types lt
        CROSS JOIN public.permissions p
        WHERE lt.code = 'manager'
          AND p.code IN ('vehicle.view', 'vehicle.edit', 'vehicle.grant_access', 'vehicle.view_history', 'vehicle.manage_documents')
        ON CONFLICT DO NOTHING
    """)

    # Authorized Driver (só visualizar)
    op.execute("""
        INSERT INTO public.link_type_permissions (link_type_id, permission_id)
        SELECT
            lt.id,
            p.id
        FROM public.link_types lt
        CROSS JOIN public.permissions p
        WHERE lt.code = 'authorized_driver'
          AND p.code IN ('vehicle.view', 'vehicle.view_history')
        ON CONFLICT DO NOTHING
    """)

    # Renter (só visualizar)
    op.execute("""
        INSERT INTO public.link_type_permissions (link_type_id, permission_id)
        SELECT
            lt.id,
            p.id
        FROM public.link_types lt
        CROSS JOIN public.permissions p
        WHERE lt.code = 'renter'
          AND p.code IN ('vehicle.view', 'vehicle.view_history')
        ON CONFLICT DO NOTHING
    """)

    # Mechanic (só visualizar histórico)
    op.execute("""
        INSERT INTO public.link_type_permissions (link_type_id, permission_id)
        SELECT
            lt.id,
            p.id
        FROM public.link_types lt
        CROSS JOIN public.permissions p
        WHERE lt.code = 'mechanic'
          AND p.code IN ('vehicle.view', 'vehicle.view_history')
        ON CONFLICT DO NOTHING
    """)

    # ============================================================================
    # REMOVER: campo permissions JSONB de link_types
    # ============================================================================
    op.execute("""
        ALTER TABLE IF EXISTS public.link_types
            DROP COLUMN IF EXISTS permissions
    """)

    op.execute("""
        COMMENT ON TABLE public.link_types
            IS 'Tipos de vínculos. Permissões agora definidas em link_type_permissions'
    """)

    # ============================================================================
    # FUNÇÃO: check_link_permission
    # Valida se uma entidade tem determinada permissão em um veículo
    # ============================================================================
    op.execute("""
        CREATE OR REPLACE FUNCTION public.check_link_permission(
            p_entity_id uuid,
            p_vehicle_id uuid,
            p_permission_code character varying
        )
        RETURNS boolean
        LANGUAGE plpgsql
        STABLE
        AS $$
        BEGIN
            RETURN EXISTS (
                SELECT 1
                FROM public.links l
                INNER JOIN public.link_type_permissions ltp
                    ON ltp.link_type_id = l.link_type_id
                INNER JOIN public.permissions p
                    ON p.id = ltp.permission_id
                WHERE l.entity_id = p_entity_id
                  AND l.vehicle_id = p_vehicle_id
                  AND l.status = 'active'
                  AND (l.end_date IS NULL OR l.end_date >= CURRENT_DATE)
                  AND l.start_date <= CURRENT_DATE
                  AND p.code = p_permission_code
                  AND p.active = true
            );
        END;
        $$
    """)

    op.execute("""
        COMMENT ON FUNCTION public.check_link_permission(uuid, uuid, character varying)
            IS 'Verifica se uma entidade tem determinada permissão em um veículo específico'
    """)


def downgrade() -> None:
    # Remove função
    op.execute("DROP FUNCTION IF EXISTS public.check_link_permission(uuid, uuid, character varying)")

    # Recria coluna permissions em link_types
    op.execute("""
        ALTER TABLE IF EXISTS public.link_types
            ADD COLUMN IF NOT EXISTS permissions jsonb
    """)

    # Remove tabelas (em ordem reversa devido às FKs)
    op.execute("DROP TABLE IF EXISTS public.link_type_permissions CASCADE")
    op.execute("DROP TABLE IF EXISTS public.permissions CASCADE")
