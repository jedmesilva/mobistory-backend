"""add_moments_tables

Revision ID: a0bb1482016e
Revises: 61bc8cd25ef8
Create Date: 2025-10-28 07:17:53.902868

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'a0bb1482016e'
down_revision = '61bc8cd25ef8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # MOMENTS - Post principal
    # ==========================================================================
    op.create_table(
        'moments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('created_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id'), nullable=False),

        # Status e visibilidade
        sa.Column('status', sa.String(), default='published'),  # 'published', 'draft', 'archived', 'deleted'
        sa.Column('visibility', sa.String(), default='public'),  # 'public', 'private', 'followers', 'specific_entities'

        # Localização
        sa.Column('location_lat', sa.Numeric(precision=10, scale=7)),
        sa.Column('location_lng', sa.Numeric(precision=10, scale=7)),
        sa.Column('location_name', sa.String()),  # Nome do local

        # Datas
        sa.Column('recorded_at', sa.TIMESTAMP(timezone=True)),  # Quando foi gravado
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para moments
    op.create_index('idx_moments_created_by_entity_id', 'moments', ['created_by_entity_id'])
    op.create_index('idx_moments_status', 'moments', ['status'])
    op.create_index('idx_moments_visibility', 'moments', ['visibility'])
    op.create_index('idx_moments_created_at', 'moments', ['created_at'])

    # ==========================================================================
    # MOMENT_CONTENTS - Arquivos do momento (fotos/vídeos)
    # ==========================================================================
    op.create_table(
        'moment_contents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('moment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('moments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('files.id', ondelete='CASCADE'), nullable=False),

        # Ordenação e destaque
        sa.Column('display_order', sa.Integer()),  # Ordem de exibição (1, 2, 3...)
        sa.Column('is_cover', sa.Boolean(), default=False),  # Se é a capa do post

        # Datas
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Índices para moment_contents
    op.create_index('idx_moment_contents_moment_id', 'moment_contents', ['moment_id'])
    op.create_index('idx_moment_contents_file_id', 'moment_contents', ['file_id'])
    op.create_index('idx_moment_contents_display_order', 'moment_contents', ['moment_id', 'display_order'])

    # ==========================================================================
    # MOMENT_VEHICLES - Veículos marcados no momento
    # ==========================================================================
    op.create_table(
        'moment_vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('moment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('moments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tagged_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),  # Quem marcou

        # Datas
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Índices para moment_vehicles
    op.create_index('idx_moment_vehicles_moment_id', 'moment_vehicles', ['moment_id'])
    op.create_index('idx_moment_vehicles_vehicle_id', 'moment_vehicles', ['vehicle_id'])

    # ==========================================================================
    # MOMENT_DESCRIPTIONS - Histórico de descrições do momento
    # ==========================================================================
    op.create_table(
        'moment_descriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('moment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('moments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('edited_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id'), nullable=False),
        sa.Column('is_current', sa.Boolean(), default=True),  # Se é a descrição atual
        sa.Column('edit_reason', sa.String()),  # Motivo da edição (opcional)

        # Datas
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
    )

    # Índices para moment_descriptions
    op.create_index('idx_moment_descriptions_moment_id', 'moment_descriptions', ['moment_id'])
    op.create_index('idx_moment_descriptions_is_current', 'moment_descriptions', ['moment_id', 'is_current'])


def downgrade() -> None:
    # Drop em ordem reversa (por causa das foreign keys)

    # moment_descriptions
    op.drop_index('idx_moment_descriptions_is_current', table_name='moment_descriptions')
    op.drop_index('idx_moment_descriptions_moment_id', table_name='moment_descriptions')
    op.drop_table('moment_descriptions')

    # moment_vehicles
    op.drop_index('idx_moment_vehicles_vehicle_id', table_name='moment_vehicles')
    op.drop_index('idx_moment_vehicles_moment_id', table_name='moment_vehicles')
    op.drop_table('moment_vehicles')

    # moment_contents
    op.drop_index('idx_moment_contents_display_order', table_name='moment_contents')
    op.drop_index('idx_moment_contents_file_id', table_name='moment_contents')
    op.drop_index('idx_moment_contents_moment_id', table_name='moment_contents')
    op.drop_table('moment_contents')

    # moments
    op.drop_index('idx_moments_created_at', table_name='moments')
    op.drop_index('idx_moments_visibility', table_name='moments')
    op.drop_index('idx_moments_status', table_name='moments')
    op.drop_index('idx_moments_created_by_entity_id', table_name='moments')
    op.drop_table('moments')
