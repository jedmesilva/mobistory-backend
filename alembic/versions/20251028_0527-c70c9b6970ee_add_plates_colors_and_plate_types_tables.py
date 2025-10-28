"""add_plates_colors_and_plate_types_tables

Revision ID: c70c9b6970ee
Revises: 0b985f927bf7
Create Date: 2025-10-28 05:27:15.066501

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'c70c9b6970ee'
down_revision = '0b985f927bf7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # PLATE TYPES (Padrões de Placas) - Tabela Mestra
    # ==========================================================================
    op.create_table(
        'plate_types',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('code', sa.String(), nullable=False, unique=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('country', sa.String(), nullable=False),  # País (BR, US, AR, etc)
        sa.Column('format_pattern', sa.String()),  # Padrão formato (AAA-9999, AAA9A99, etc)
        sa.Column('format_example', sa.String()),  # Exemplo (ABC-1234)
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para plate_types
    op.create_index('idx_plate_types_code', 'plate_types', ['code'])
    op.create_index('idx_plate_types_country', 'plate_types', ['country'])
    op.create_index('idx_plate_types_active', 'plate_types', ['active'])

    # ==========================================================================
    # PLATES (Placas dos Veículos) - Histórico
    # ==========================================================================
    op.create_table(
        'plates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('plate_type_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('plate_types.id'), nullable=False),
        sa.Column('plate_number', sa.String(), nullable=False),  # Número da placa
        sa.Column('licensing_date', sa.Date()),  # Data de licenciamento
        sa.Column('licensing_country', sa.String()),  # País de licenciamento
        sa.Column('state', sa.String()),  # Estado/Província
        sa.Column('city', sa.String()),  # Cidade
        sa.Column('status', sa.String(), default='active'),  # active, inactive, transferred, canceled
        sa.Column('end_date', sa.Date()),  # Data de encerramento de uso
        sa.Column('created_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),  # Entidade que criou
        sa.Column('active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para plates
    op.create_index('idx_plates_vehicle_id', 'plates', ['vehicle_id'])
    op.create_index('idx_plates_plate_number', 'plates', ['plate_number'])
    op.create_index('idx_plates_status', 'plates', ['status'])
    op.create_index('idx_plates_active', 'plates', ['active'])
    op.create_index('idx_plates_licensing_date', 'plates', ['licensing_date'])

    # ==========================================================================
    # COLORS (Cores dos Veículos) - Histórico
    # ==========================================================================
    op.create_table(
        'colors',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('color', sa.String(), nullable=False),  # Nome da cor
        sa.Column('hex_code', sa.String()),  # Código hexadecimal (#FFFFFF)
        sa.Column('start_date', sa.Date()),  # Quando começou a usar essa cor
        sa.Column('end_date', sa.Date()),  # Quando parou de usar
        sa.Column('created_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),  # Entidade que criou
        sa.Column('active', sa.Boolean(), default=True),  # Se é a cor atual
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para colors
    op.create_index('idx_colors_vehicle_id', 'colors', ['vehicle_id'])
    op.create_index('idx_colors_color', 'colors', ['color'])
    op.create_index('idx_colors_active', 'colors', ['active'])
    op.create_index('idx_colors_start_date', 'colors', ['start_date'])


def downgrade() -> None:
    # Drop em ordem reversa (por causa das foreign keys)
    op.drop_index('idx_colors_start_date', table_name='colors')
    op.drop_index('idx_colors_active', table_name='colors')
    op.drop_index('idx_colors_color', table_name='colors')
    op.drop_index('idx_colors_vehicle_id', table_name='colors')
    op.drop_table('colors')

    op.drop_index('idx_plates_licensing_date', table_name='plates')
    op.drop_index('idx_plates_active', table_name='plates')
    op.drop_index('idx_plates_status', table_name='plates')
    op.drop_index('idx_plates_plate_number', table_name='plates')
    op.drop_index('idx_plates_vehicle_id', table_name='plates')
    op.drop_table('plates')

    op.drop_index('idx_plate_types_active', table_name='plate_types')
    op.drop_index('idx_plate_types_country', table_name='plate_types')
    op.drop_index('idx_plate_types_code', table_name='plate_types')
    op.drop_table('plate_types')
