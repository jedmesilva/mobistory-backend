"""add_color_fields_to_plate_types

Revision ID: f7a8b9c0d1e2
Revises: c2f8af2d9399
Create Date: 2025-11-04 00:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f7a8b9c0d1e2'
down_revision = 'c2f8af2d9399'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar campos de cor à tabela plate_types
    op.add_column('plate_types', sa.Column('category', sa.String(), nullable=True))
    op.add_column('plate_types', sa.Column('plate_color_name', sa.String(), nullable=True))
    op.add_column('plate_types', sa.Column('background_color_hex', sa.String(), nullable=True))
    op.add_column('plate_types', sa.Column('text_color_hex', sa.String(), nullable=True))

    # Criar índice para category
    op.create_index('idx_plate_types_category', 'plate_types', ['category'])


def downgrade() -> None:
    # Remover índice
    op.drop_index('idx_plate_types_category', table_name='plate_types')

    # Remover colunas
    op.drop_column('plate_types', 'text_color_hex')
    op.drop_column('plate_types', 'background_color_hex')
    op.drop_column('plate_types', 'plate_color_name')
    op.drop_column('plate_types', 'category')
