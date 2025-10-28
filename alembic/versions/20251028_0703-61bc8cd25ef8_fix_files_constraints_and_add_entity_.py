"""fix_files_constraints_and_add_entity_documents

Revision ID: 61bc8cd25ef8
Revises: fa9bc5d6bbab
Create Date: 2025-10-28 07:03:35.162667

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '61bc8cd25ef8'
down_revision = 'fa9bc5d6bbab'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ==========================================================================
    # CORREÇÃO DA TABELA FILES
    # ==========================================================================

    # Tornar vehicle_id NULLABLE (pode ser arquivo de entidade sem veículo)
    op.alter_column('files', 'vehicle_id',
                    existing_type=postgresql.UUID(),
                    nullable=True)

    # Tornar uploaded_by_entity_id NOT NULL (sempre tem alguém que enviou)
    op.alter_column('files', 'uploaded_by_entity_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)

    # ==========================================================================
    # ENTITY_DOCUMENTS - Documentos das Entidades
    # ==========================================================================
    op.create_table(
        'entity_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('files.id', ondelete='CASCADE'), nullable=False),
        sa.Column('document_type', sa.String()),  # 'cnh', 'cpf', 'rg', 'cnpj', 'passport', 'proof_of_address'
        sa.Column('document_number', sa.String()),  # Número do documento
        sa.Column('issue_date', sa.Date()),  # Data de emissão
        sa.Column('expiry_date', sa.Date()),  # Data de validade
        sa.Column('issuing_authority', sa.String()),  # Órgão emissor
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verified_at', sa.TIMESTAMP(timezone=True)),
        sa.Column('verified_by_entity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('entities.id')),
        sa.Column('is_current', sa.Boolean(), default=True),  # Se é o documento atual
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Índices para entity_documents
    op.create_index('idx_entity_documents_entity_id', 'entity_documents', ['entity_id'])
    op.create_index('idx_entity_documents_file_id', 'entity_documents', ['file_id'])
    op.create_index('idx_entity_documents_document_type', 'entity_documents', ['document_type'])
    op.create_index('idx_entity_documents_is_current', 'entity_documents', ['is_current'])
    op.create_index('idx_entity_documents_entity_type', 'entity_documents', ['entity_id', 'document_type'])


def downgrade() -> None:
    # Drop entity_documents
    op.drop_index('idx_entity_documents_entity_type', table_name='entity_documents')
    op.drop_index('idx_entity_documents_is_current', table_name='entity_documents')
    op.drop_index('idx_entity_documents_document_type', table_name='entity_documents')
    op.drop_index('idx_entity_documents_file_id', table_name='entity_documents')
    op.drop_index('idx_entity_documents_entity_id', table_name='entity_documents')
    op.drop_table('entity_documents')

    # Reverter alterações em files
    op.alter_column('files', 'uploaded_by_entity_id',
                    existing_type=postgresql.UUID(),
                    nullable=True)

    op.alter_column('files', 'vehicle_id',
                    existing_type=postgresql.UUID(),
                    nullable=False)
