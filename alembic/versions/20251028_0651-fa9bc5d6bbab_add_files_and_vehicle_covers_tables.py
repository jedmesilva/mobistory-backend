"""add_files_and_vehicle_covers_tables

Revision ID: fa9bc5d6bbab
Revises: 451a37a90810
Create Date: 2025-10-28 06:51:30.625818

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'fa9bc5d6bbab'
down_revision = '451a37a90810'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # FILES - Tabela principal de arquivos
    # ==========================================================================
    op.create_table(
        'files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),

        # Relacionamentos principais
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('uploaded_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),

        # Arquivo
        sa.Column('file_url', sa.Text(), nullable=False),
        sa.Column('file_name', sa.String()),
        sa.Column('file_type', sa.String()),  # 'image', 'video', 'pdf', 'document'
        sa.Column('mime_type', sa.String()),  # 'image/jpeg', 'video/mp4', etc
        sa.Column('file_size_bytes', sa.BigInteger()),

        # Metadados
        sa.Column('width', sa.Integer()),  # Para imagens/vídeos
        sa.Column('height', sa.Integer()),
        sa.Column('duration_seconds', sa.Integer()),  # Para vídeos

        # Origem
        sa.Column('source', sa.String()),  # 'mobile_app', 'web_app', 'whatsapp', 'email'

        # Status
        sa.Column('status', sa.String(), default='active'),  # 'active', 'inactive', 'deleted'

        # Datas
        sa.Column('uploaded_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para files
    op.create_index('idx_files_vehicle_id', 'files', ['vehicle_id'])
    op.create_index('idx_files_uploaded_by_entity_id', 'files', ['uploaded_by_entity_id'])
    op.create_index('idx_files_status', 'files', ['status'])
    op.create_index('idx_files_vehicle_status', 'files', ['vehicle_id', 'status'])

    # ==========================================================================
    # VEHICLE_COVERS - Tabela de uso específico para capas de veículos
    # ==========================================================================
    op.create_table(
        'vehicle_covers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('files.id', ondelete='CASCADE'), nullable=False),
        sa.Column('is_primary', sa.Boolean(), default=False),  # Se é a capa principal
        sa.Column('display_order', sa.Integer()),  # Ordem de exibição
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para vehicle_covers
    op.create_index('idx_vehicle_covers_vehicle_id', 'vehicle_covers', ['vehicle_id'])
    op.create_index('idx_vehicle_covers_file_id', 'vehicle_covers', ['file_id'])
    op.create_index('idx_vehicle_covers_is_primary', 'vehicle_covers', ['is_primary'])
    op.create_index('idx_vehicle_covers_vehicle_primary', 'vehicle_covers', ['vehicle_id', 'is_primary'])


def downgrade() -> None:
    # Drop em ordem reversa (por causa das foreign keys)
    op.drop_index('idx_vehicle_covers_vehicle_primary', table_name='vehicle_covers')
    op.drop_index('idx_vehicle_covers_is_primary', table_name='vehicle_covers')
    op.drop_index('idx_vehicle_covers_file_id', table_name='vehicle_covers')
    op.drop_index('idx_vehicle_covers_vehicle_id', table_name='vehicle_covers')
    op.drop_table('vehicle_covers')

    op.drop_index('idx_files_vehicle_status', table_name='files')
    op.drop_index('idx_files_status', table_name='files')
    op.drop_index('idx_files_uploaded_by_entity_id', table_name='files')
    op.drop_index('idx_files_vehicle_id', table_name='files')
    op.drop_table('files')
